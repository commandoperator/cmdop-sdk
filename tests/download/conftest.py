"""
Pytest fixtures for download service tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from cmdop.services.download import AsyncDownloadService, DownloadService


class MockTransport:
    """Mock transport for download service tests."""

    @property
    def mode(self) -> str:
        return "mock"

    def get_channel(self):
        return MagicMock()

    def get_async_channel(self):
        return MagicMock()

    @property
    def metadata(self):
        return [("authorization", "Bearer test_token")]


@pytest.fixture
def mock_transport():
    """Provide mock transport."""
    return MockTransport()


@pytest.fixture
def sync_download_service(mock_transport):
    """Provide sync download service with mock transport."""
    return DownloadService(mock_transport)


@pytest.fixture
def async_download_service(mock_transport):
    """Provide async download service with mock transport."""
    return AsyncDownloadService(mock_transport)


@pytest.fixture
def mock_files_service():
    """Provide mock files service."""
    service = MagicMock()
    service.info = MagicMock()
    service.read = MagicMock()
    service.list = MagicMock()
    service.delete = MagicMock()
    service.set_session_id = MagicMock()
    return service


@pytest.fixture
def mock_async_files_service():
    """Provide mock async files service."""
    service = AsyncMock()
    service.info = AsyncMock()
    service.read = AsyncMock()
    service.list = AsyncMock()
    service.delete = AsyncMock()
    service.set_session_id = MagicMock()
    return service


@pytest.fixture
def mock_terminal_service():
    """Provide mock terminal service."""
    service = MagicMock()
    service.create = MagicMock()
    service.send_input = MagicMock()
    service.close = MagicMock()
    return service


@pytest.fixture
def mock_async_terminal_service():
    """Provide mock async terminal service."""
    service = AsyncMock()
    service.create = AsyncMock()
    service.get_active_session = AsyncMock()
    service.send_input = AsyncMock()
    service.close = AsyncMock()
    return service
