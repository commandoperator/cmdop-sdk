"""
Transfer logic for download service.

Contains shared transfer strategies for both sync and async services.
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Protocol

from cmdop.logging import get_logger
from cmdop.services.download._config import MAX_PARALLEL_PARTS, SPLIT_PART_SIZE_MB
from cmdop.services.download._models import TransferStats

if TYPE_CHECKING:
    from cmdop.services.files import AsyncFilesService
    from cmdop.services.terminal import AsyncTerminalService

logger = get_logger(__name__)


class AsyncTransfer:
    """Async transfer strategies for downloading files."""

    def __init__(
        self,
        files: AsyncFilesService,
        terminal: AsyncTerminalService,
        session_id: str,
        chunk_size: int,
        api_key: str | None = None,
    ) -> None:
        self._files = files
        self._terminal = terminal
        self._session_id = session_id
        self._chunk_size = chunk_size
        self._api_key = api_key

    async def direct_chunked(
        self,
        remote_path: str,
        local_path: Path,
        total_size: int,
        on_progress: Callable[[int, int], None] | None = None,
        max_retries: int = 3,
    ) -> TransferStats:
        """
        Transfer file directly in chunks.

        Best for files <= 10MB.
        """
        stats = TransferStats()
        offset = 0
        retries = 0

        with open(local_path, "wb") as f:
            while offset < total_size:
                remaining = total_size - offset
                read_size = min(self._chunk_size, remaining)

                try:
                    content = await self._files.read(
                        remote_path,
                        offset=offset,
                        length=read_size,
                        session_id=self._session_id,
                        timeout=120.0,
                    )

                    if not content:
                        logger.warning(f"Empty chunk at offset {offset}")
                        retries += 1
                        stats.retries_count += 1
                        if retries >= max_retries:
                            break
                        await asyncio.sleep(1)
                        continue

                    f.write(content)
                    offset += len(content)
                    stats.bytes_transferred += len(content)
                    stats.chunks_count += 1
                    retries = 0

                    if on_progress:
                        on_progress(stats.bytes_transferred, total_size)

                except Exception as e:
                    logger.warning(f"Transfer error at offset {offset}: {e}")
                    retries += 1
                    stats.retries_count += 1
                    if retries >= max_retries:
                        raise RuntimeError(
                            f"Transfer failed after {max_retries} retries: {e}"
                        ) from e
                    await asyncio.sleep(2)

        return stats

    async def split_parts(
        self,
        remote_path: str,
        local_path: Path,
        total_size: int,
        on_progress: Callable[[int, int], None] | None = None,
        parallel: int = MAX_PARALLEL_PARTS,
    ) -> TransferStats:
        """
        Transfer large file by splitting on remote and downloading parts.

        Workaround for cloud relay limits (~30MB per session).
        Parts are downloaded in parallel with fresh connections.

        Args:
            remote_path: Path to file on remote.
            local_path: Local path to save file.
            total_size: Total file size in bytes.
            on_progress: Progress callback(transferred, total).
            parallel: Max parallel downloads (default: 4).
        """
        if not self._api_key:
            raise RuntimeError(
                "API key required for large file downloads. "
                "Call download.configure(api_key=...)"
            )

        stats = TransferStats()
        split_dir = f"/tmp/cmdop_split_{int(time.time())}"

        # Split file on remote
        split_cmd = (
            f"mkdir -p {split_dir} && "
            f"split -b {SPLIT_PART_SIZE_MB}M {remote_path} {split_dir}/part_"
        )
        await self._terminal.send_input(self._session_id, f"{split_cmd}\n")
        await asyncio.sleep(3)

        # Get list of parts
        response = await self._files.list(split_dir, session_id=self._session_id)
        parts = sorted(
            [(e.name, e.size) for e in response.entries if e.name.startswith("part_")]
        )

        if not parts:
            raise RuntimeError("Failed to split file on remote")

        logger.debug(f"Split into {len(parts)} parts, downloading {parallel} in parallel")

        # Download parts in parallel batches
        part_results: dict[int, _PartResult] = {}
        transferred = 0
        semaphore = asyncio.Semaphore(parallel)

        async def download_part(idx: int, name: str, size: int) -> None:
            async with semaphore:
                part_remote = f"{split_dir}/{name}"
                logger.debug(f"Downloading part {idx + 1}/{len(parts)}: {name}")
                result = await self._download_part_reconnect(part_remote, size)
                part_results[idx] = result

        # Start all downloads
        tasks = [
            asyncio.create_task(download_part(i, name, size))
            for i, (name, size) in enumerate(parts)
        ]

        # Wait and track progress
        for task in asyncio.as_completed(tasks):
            await task
            # Update progress after each part completes
            current_transferred = sum(len(r.data) for r in part_results.values())
            if on_progress and current_transferred > transferred:
                transferred = current_transferred
                on_progress(transferred, total_size)

        # Write parts in order
        with open(local_path, "wb") as f:
            for i in range(len(parts)):
                result = part_results[i]
                f.write(result.data)
                stats.bytes_transferred += len(result.data)
                stats.chunks_count += result.chunks_count
                stats.retries_count += result.retries_count

        # Cleanup
        try:
            await self._terminal.send_input(self._session_id, f"rm -rf {split_dir}\n")
        except Exception:
            pass

        return stats

    async def _download_part_reconnect(
        self,
        remote_path: str,
        total_size: int,
        max_retries: int = 3,
    ) -> _PartResult:
        """Download a part with fresh connection."""
        from cmdop import AsyncCMDOPClient

        data = bytearray()
        chunks = 0
        retries = 0

        for attempt in range(max_retries):
            try:
                async with AsyncCMDOPClient.remote(api_key=self._api_key) as client:
                    session = await client.terminal.get_active_session()
                    if not session:
                        raise RuntimeError("No active session on remote")
                    client.files.set_session_id(session.session_id)

                    offset = len(data)
                    while offset < total_size:
                        remaining = total_size - offset
                        read_size = min(self._chunk_size, remaining)

                        content = await client.files.read(
                            remote_path,
                            offset=offset,
                            length=read_size,
                            timeout=60.0,
                        )

                        if not content:
                            break

                        data.extend(content)
                        offset += len(content)
                        chunks += 1

                    if len(data) >= total_size:
                        return _PartResult(bytes(data), chunks, retries)

            except Exception as e:
                logger.warning(f"Part download attempt {attempt + 1} failed: {e}")
                retries += 1
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                else:
                    raise

        return _PartResult(bytes(data), chunks, retries)


class _PartResult:
    """Result of downloading a single part."""

    __slots__ = ("data", "chunks_count", "retries_count")

    def __init__(self, data: bytes, chunks_count: int, retries_count: int) -> None:
        self.data = data
        self.chunks_count = chunks_count
        self.retries_count = retries_count
