"""
Synchronous download service.

Wrapper around AsyncDownloadService using asyncio.run().
For large files (>10MB), use AsyncDownloadService directly.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from cmdop.services.base import BaseService
from cmdop.services.download._aio import AsyncDownloadService
from cmdop.services.download._config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_DOWNLOAD_TIMEOUT,
)
from cmdop.services.download._models import DownloadResult

if TYPE_CHECKING:
    from cmdop.transport.base import BaseTransport


class DownloadService(BaseService):
    """
    Synchronous download service.

    Thin wrapper around AsyncDownloadService.
    Best for small files (<=10MB). For large files, use AsyncDownloadService.

    Example:
        >>> client = CMDOPClient.remote(api_key="cmd_xxx")
        >>> result = client.download.url(
        ...     url="https://example.com/data.csv.gz",
        ...     local_path=Path("./data.csv.gz"),
        ... )
        >>> print(result)
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._async_service = AsyncDownloadService(transport)

    def set_session_id(self, session_id: str) -> None:
        """Set session ID for operations."""
        self._async_service.set_session_id(session_id)

    def configure(
        self,
        chunk_size: int | None = None,
        download_timeout: int | None = None,
    ) -> None:
        """
        Configure download settings.

        Args:
            chunk_size: Chunk size for file transfer (bytes).
            download_timeout: Timeout for download completion (seconds).
        """
        self._async_service.configure(
            chunk_size=chunk_size,
            download_timeout=download_timeout,
        )

    def url(
        self,
        url: str,
        local_path: Path,
        remote_temp_path: str | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        cleanup: bool = True,
    ) -> DownloadResult:
        """
        Download file from URL via remote server.

        Args:
            url: URL to download.
            local_path: Local path to save file.
            remote_temp_path: Temp path on remote (auto-generated if None).
            on_progress: Callback(transferred, total) for progress.
            cleanup: Delete remote temp file after transfer.

        Returns:
            DownloadResult with success status, size, and metrics.
        """
        return asyncio.run(
            self._async_service.url(
                url=url,
                local_path=local_path,
                remote_temp_path=remote_temp_path,
                on_progress=on_progress,
                cleanup=cleanup,
            )
        )
