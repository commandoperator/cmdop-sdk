"""
Asynchronous download service.

Handles cloud relay limits (~30MB per session) by:
- Splitting large files on remote server
- Downloading each part with fresh connection
- Automatic retry with exponential backoff
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from cmdop.logging import get_logger
from cmdop.models.terminal import SessionListItem
from cmdop.services.base import BaseService
from cmdop.services.download._config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_DOWNLOAD_TIMEOUT,
    LARGE_FILE_THRESHOLD,
)
from cmdop.services.download._models import DownloadMetrics, DownloadResult
from cmdop.services.download._transfer import AsyncTransfer

if TYPE_CHECKING:
    from datetime import datetime

    from cmdop.transport.base import BaseTransport

logger = get_logger(__name__)


class AsyncDownloadService(BaseService):
    """
    Asynchronous download service.

    Handles cloud relay limits (~30MB per session) by:
    - For small files (<=10MB): Direct chunked transfer
    - For large files (>10MB): Split on remote, download parts with reconnection

    Example:
        >>> async with AsyncCMDOPClient.remote(api_key="cmd_xxx") as client:
        ...     # Configure for large files
        ...     client.download.configure(api_key="cmd_xxx")
        ...
        ...     result = await client.download.url(
        ...         url="https://example.com/data.csv.gz",
        ...         local_path=Path("./data.csv.gz"),
        ...     )
        ...     print(result)  # Shows metrics summary
        ...     print(result.metrics.summary())  # Detailed metrics
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._session_id: str | None = None
        self._cached_hostname: str | None = None
        self._cached_session_info: SessionListItem | None = None
        self._chunk_size = DEFAULT_CHUNK_SIZE
        self._download_timeout = DEFAULT_DOWNLOAD_TIMEOUT
        self._api_key: str | None = None

    async def set_machine(self, hostname: str, partial_match: bool = True) -> SessionListItem:
        """
        Set target machine by hostname for download operations.

        Uses GetSessionByHostname RPC for efficient server-side resolution.
        Caches session_id for all subsequent download operations.

        Args:
            hostname: Machine hostname.
            partial_match: If True, allows partial hostname matching (default).
                          If False, requires exact hostname match.

        Returns:
            SessionListItem for the found session.

        Raises:
            CMDOPError: If no active session found, or hostname is ambiguous.

        Example:
            >>> await client.download.set_machine("my-server")
            >>> result = await client.download.url("https://...", Path("./file"))
        """
        from datetime import datetime, timezone

        from cmdop._generated.rpc_messages.session_pb2 import (
            GetSessionByHostnameRequest,
        )
        from cmdop._generated.service_pb2_grpc import TerminalStreamingServiceStub
        from cmdop.exceptions import CMDOPError

        stub = TerminalStreamingServiceStub(self._async_channel)
        request = GetSessionByHostnameRequest(
            hostname=hostname,
            partial_match=partial_match,
        )
        response = await self._call_async(stub.GetSessionByHostname, request)

        if not response.found:
            if response.ambiguous:
                raise CMDOPError(
                    f"Ambiguous hostname '{hostname}' matches {response.matches_count} machines. "
                    "Use a more specific hostname or set partial_match=False."
                )
            raise CMDOPError(response.error or f"No active session found for hostname: {hostname}")

        # Parse connected_at timestamp
        connected_at: datetime | None = None
        if response.connected_at and response.connected_at.seconds > 0:
            connected_at = datetime.fromtimestamp(
                response.connected_at.seconds, tz=timezone.utc
            )

        # Build SessionListItem
        session = SessionListItem(
            session_id=response.session_id,
            machine_hostname=response.machine_hostname,
            machine_name=response.machine_name,
            status=response.status,
            os=response.os,
            agent_version=response.agent_version,
            heartbeat_age_seconds=response.heartbeat_age_seconds,
            has_shell=response.has_shell,
            shell=response.shell,
            working_directory=response.working_directory,
            connected_at=connected_at,
        )

        # Cache session info
        self._cached_hostname = response.machine_hostname
        self._session_id = response.session_id
        self._cached_session_info = session
        return session

    def set_session_id(self, session_id: str) -> None:
        """Set session ID for operations. Prefer set_machine() for hostname-based targeting."""
        self._session_id = session_id

    def clear_session(self) -> None:
        """Clear cached session and hostname."""
        self._session_id = None
        self._cached_hostname = None
        self._cached_session_info = None

    @property
    def current_session(self) -> SessionListItem | None:
        """Get currently cached session info."""
        return self._cached_session_info

    @property
    def current_hostname(self) -> str | None:
        """Get currently cached hostname."""
        return self._cached_hostname

    def set_api_key(self, api_key: str) -> None:
        """Set API key for reconnection during large file transfers."""
        self._api_key = api_key

    def configure(
        self,
        chunk_size: int | None = None,
        download_timeout: int | None = None,
        api_key: str | None = None,
    ) -> None:
        """
        Configure download settings.

        Args:
            chunk_size: Chunk size for file transfer (bytes).
            download_timeout: Timeout for download completion (seconds).
            api_key: API key for reconnection (required for files >10MB).
        """
        if chunk_size is not None:
            self._chunk_size = chunk_size
        if download_timeout is not None:
            self._download_timeout = download_timeout
        if api_key is not None:
            self._api_key = api_key

    async def url(
        self,
        url: str,
        local_path: Path,
        remote_temp_path: str | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        cleanup: bool = True,
    ) -> DownloadResult:
        """
        Download file from URL via remote server.

        For large files (>10MB), automatically splits on remote and
        downloads parts with reconnection to avoid relay limits.

        Args:
            url: URL to download.
            local_path: Local path to save file.
            remote_temp_path: Temp path on remote (auto-generated if None).
            on_progress: Callback(transferred, total) for progress.
            cleanup: Delete remote temp file after transfer.

        Returns:
            DownloadResult with success status, size, and metrics.
        """
        from cmdop.services.files import AsyncFilesService
        from cmdop.services.terminal import AsyncTerminalService

        metrics = DownloadMetrics()
        total_start = time.perf_counter()

        terminal = AsyncTerminalService(self._transport)
        files = AsyncFilesService(self._transport)

        if remote_temp_path is None:
            filename = url.split("/")[-1].split("?")[0] or "download"
            remote_temp_path = f"/tmp/cmdop_dl_{int(time.time())}_{filename}"

        session_id = self._session_id
        created_session = False

        if not session_id:
            active = await terminal.get_active_session()
            if active:
                session_id = active.session_id
                logger.debug(f"Using active session: {session_id}")
            else:
                session = await terminal.create()
                session_id = session.session_id
                created_session = True
                logger.debug(f"Created new session: {session_id}")
            files.set_session_id(session_id)

        try:
            # Execute curl on remote
            curl_start = time.perf_counter()
            curl_cmd = f"curl -sS -o '{remote_temp_path}' '{url}'"
            await terminal.send_input(session_id, f"{curl_cmd}\n")

            # Wait for download
            file_size = await self._wait_for_file(files, remote_path=remote_temp_path)
            metrics.curl_time = time.perf_counter() - curl_start
            metrics.remote_size = file_size

            if file_size == 0:
                metrics.total_time = time.perf_counter() - total_start
                return DownloadResult(
                    success=False,
                    error=f"Download failed or timeout for {url}",
                    metrics=metrics,
                )

            logger.debug(f"Remote file ready: {file_size:,} bytes (curl: {metrics.curl_time:.1f}s)")

            # Create transfer helper
            transfer = AsyncTransfer(
                files=files,
                terminal=terminal,
                session_id=session_id,
                chunk_size=self._chunk_size,
                api_key=self._api_key,
            )

            # Transfer file
            local_path.parent.mkdir(parents=True, exist_ok=True)
            transfer_start = time.perf_counter()

            if file_size <= LARGE_FILE_THRESHOLD:
                stats = await transfer.direct_chunked(
                    remote_path=remote_temp_path,
                    local_path=local_path,
                    total_size=file_size,
                    on_progress=on_progress,
                )
            else:
                stats = await transfer.split_parts(
                    remote_path=remote_temp_path,
                    local_path=local_path,
                    total_size=file_size,
                    on_progress=on_progress,
                )
                metrics.parts_count = (file_size // (5 * 1024 * 1024)) + 1

            metrics.transfer_time = time.perf_counter() - transfer_start
            metrics.transferred_size = stats.bytes_transferred
            metrics.chunks_count = stats.chunks_count
            metrics.retries_count = stats.retries_count
            metrics.local_size = local_path.stat().st_size if local_path.exists() else 0

            # Cleanup
            if cleanup:
                try:
                    await files.delete(remote_temp_path, session_id=session_id)
                except Exception:
                    pass

            metrics.total_time = time.perf_counter() - total_start
            logger.debug(
                f"Complete: {stats.bytes_transferred:,} bytes in {metrics.total_time:.1f}s "
                f"({metrics.total_speed_mbps:.1f} MB/s)"
            )

            return DownloadResult(
                success=True,
                local_path=local_path,
                size=stats.bytes_transferred,
                metrics=metrics,
            )

        except Exception as e:
            metrics.total_time = time.perf_counter() - total_start
            logger.error(f"Download failed: {e}")
            return DownloadResult(success=False, error=str(e), metrics=metrics)

        finally:
            if created_session and session_id:
                try:
                    await terminal.close(session_id)
                except Exception:
                    pass

    async def _wait_for_file(
        self,
        files: "AsyncFilesService",
        remote_path: str,
        poll_interval: float = 2.0,
    ) -> int:
        """Wait for file to be ready (size stable)."""
        from cmdop.services.files import AsyncFilesService

        waited = 0.0
        last_size = 0

        while waited < self._download_timeout:
            await asyncio.sleep(poll_interval)
            waited += poll_interval

            try:
                info = await files.info(remote_path)
                if info.size > 0 and info.size == last_size:
                    return info.size
                last_size = info.size
            except Exception:
                continue

        return 0
