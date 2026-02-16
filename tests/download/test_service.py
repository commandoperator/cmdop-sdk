"""Tests for download service."""

import pytest

from cmdop.services.download import AsyncDownloadService, DownloadService
from cmdop.services.download._config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_DOWNLOAD_TIMEOUT,
)


class TestDownloadServiceInit:
    """Tests for DownloadService initialization (sync wrapper)."""

    def test_wraps_async_service(self, sync_download_service):
        """Sync service should wrap async service."""
        service = sync_download_service
        assert hasattr(service, "_async_service")
        assert isinstance(service._async_service, AsyncDownloadService)

    def test_set_session_id_delegates(self, sync_download_service):
        """set_session_id should delegate to async service."""
        service = sync_download_service
        service.set_session_id("test-session-123")
        assert service._async_service._session_id == "test-session-123"

    def test_configure_delegates(self, sync_download_service):
        """configure should delegate to async service."""
        service = sync_download_service
        service.configure(
            chunk_size=2 * 1024 * 1024,
            download_timeout=600,
        )
        assert service._async_service._chunk_size == 2 * 1024 * 1024
        assert service._async_service._download_timeout == 600


class TestAsyncDownloadServiceInit:
    """Tests for AsyncDownloadService initialization."""

    def test_default_values(self, async_download_service):
        service = async_download_service
        assert service._chunk_size == DEFAULT_CHUNK_SIZE
        assert service._download_timeout == DEFAULT_DOWNLOAD_TIMEOUT
        assert service._session_id is None
        assert service._api_key is None

    def test_set_session_id(self, async_download_service):
        service = async_download_service
        service.set_session_id("test-session-456")
        assert service._session_id == "test-session-456"

    def test_set_api_key(self, async_download_service):
        service = async_download_service
        service.set_api_key("cmd_test_key")
        assert service._api_key == "cmd_test_key"

    def test_configure_all(self, async_download_service):
        service = async_download_service
        service.configure(
            chunk_size=4 * 1024 * 1024,
            download_timeout=900,
            api_key="cmd_another_key",
        )
        assert service._chunk_size == 4 * 1024 * 1024
        assert service._download_timeout == 900
        assert service._api_key == "cmd_another_key"

    def test_configure_partial(self, async_download_service):
        service = async_download_service
        original_chunk = service._chunk_size
        service.configure(api_key="cmd_key_only")
        assert service._chunk_size == original_chunk
        assert service._api_key == "cmd_key_only"
