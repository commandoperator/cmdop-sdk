"""Tests for transfer logic."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile

from cmdop.services.download._transfer import AsyncTransfer
from cmdop.services.download._models import TransferStats


class TestAsyncTransferInit:
    """Tests for AsyncTransfer initialization."""

    def test_init(self, mock_async_files_service, mock_async_terminal_service):
        transfer = AsyncTransfer(
            files=mock_async_files_service,
            terminal=mock_async_terminal_service,
            session_id="test-session",
            chunk_size=1024 * 1024,
            api_key="cmd_test",
        )
        assert transfer._session_id == "test-session"
        assert transfer._chunk_size == 1024 * 1024
        assert transfer._api_key == "cmd_test"


class TestAsyncTransferDirectChunked:
    """Tests for direct chunked transfer."""

    @pytest.mark.asyncio
    async def test_transfer_small_file(
        self, mock_async_files_service, mock_async_terminal_service
    ):
        """Test transfer of small file in chunks."""
        # Setup: 3 chunks of data
        chunk_data = b"x" * 1024
        mock_async_files_service.read = AsyncMock(
            side_effect=[chunk_data, chunk_data, chunk_data, b""]
        )

        transfer = AsyncTransfer(
            files=mock_async_files_service,
            terminal=mock_async_terminal_service,
            session_id="test",
            chunk_size=1024,
        )

        with tempfile.NamedTemporaryFile(delete=False) as f:
            local_path = Path(f.name)

        try:
            stats = await transfer.direct_chunked(
                remote_path="/tmp/test.bin",
                local_path=local_path,
                total_size=3072,
            )

            assert stats.bytes_transferred == 3072
            assert stats.chunks_count == 3
            assert stats.retries_count == 0
            assert local_path.stat().st_size == 3072
        finally:
            local_path.unlink()

    @pytest.mark.asyncio
    async def test_transfer_with_progress(
        self, mock_async_files_service, mock_async_terminal_service
    ):
        """Test progress callback is called."""
        chunk_data = b"x" * 512
        mock_async_files_service.read = AsyncMock(
            side_effect=[chunk_data, chunk_data, b""]
        )

        progress_calls = []

        def on_progress(transferred, total):
            progress_calls.append((transferred, total))

        transfer = AsyncTransfer(
            files=mock_async_files_service,
            terminal=mock_async_terminal_service,
            session_id="test",
            chunk_size=512,
        )

        with tempfile.NamedTemporaryFile(delete=False) as f:
            local_path = Path(f.name)

        try:
            await transfer.direct_chunked(
                remote_path="/tmp/test.bin",
                local_path=local_path,
                total_size=1024,
                on_progress=on_progress,
            )

            assert len(progress_calls) == 2
            assert progress_calls[0] == (512, 1024)
            assert progress_calls[1] == (1024, 1024)
        finally:
            local_path.unlink()

    @pytest.mark.asyncio
    async def test_transfer_retry_on_empty_chunk(
        self, mock_async_files_service, mock_async_terminal_service
    ):
        """Test retry when receiving empty chunk."""
        chunk_data = b"x" * 1024
        # First call returns empty, then retries succeed
        mock_async_files_service.read = AsyncMock(
            side_effect=[b"", chunk_data, b""]
        )

        transfer = AsyncTransfer(
            files=mock_async_files_service,
            terminal=mock_async_terminal_service,
            session_id="test",
            chunk_size=1024,
        )

        with tempfile.NamedTemporaryFile(delete=False) as f:
            local_path = Path(f.name)

        try:
            stats = await transfer.direct_chunked(
                remote_path="/tmp/test.bin",
                local_path=local_path,
                total_size=1024,
            )

            assert stats.bytes_transferred == 1024
            assert stats.retries_count == 1
        finally:
            local_path.unlink()


class TestAsyncTransferSplitParts:
    """Tests for split parts transfer."""

    @pytest.mark.asyncio
    async def test_split_requires_api_key(
        self, mock_async_files_service, mock_async_terminal_service
    ):
        """Test that split_parts requires api_key."""
        transfer = AsyncTransfer(
            files=mock_async_files_service,
            terminal=mock_async_terminal_service,
            session_id="test",
            chunk_size=1024,
            api_key=None,  # No API key
        )

        with tempfile.NamedTemporaryFile(delete=False) as f:
            local_path = Path(f.name)

        try:
            with pytest.raises(RuntimeError, match="API key required"):
                await transfer.split_parts(
                    remote_path="/tmp/large.bin",
                    local_path=local_path,
                    total_size=50 * 1024 * 1024,
                )
        finally:
            local_path.unlink()
