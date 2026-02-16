"""Tests for async browser service stub."""

import pytest

from cmdop.services.browser import AsyncBrowserService

from .conftest import MockTransport


class TestAsyncBrowserServiceStub:
    """Test AsyncBrowserService stub (not implemented)."""

    def test_async_service_creation(self):
        """Test async service can be created."""
        transport = MockTransport()
        service = AsyncBrowserService(transport)
        assert service._transport == transport

    @pytest.mark.asyncio
    async def test_create_session_raises_not_implemented(self):
        """Test create_session raises NotImplementedError."""
        transport = MockTransport()
        service = AsyncBrowserService(transport)

        with pytest.raises(NotImplementedError) as exc_info:
            await service.create_session()

        assert "Async browser is not implemented" in str(exc_info.value)
        assert "sync CMDOPClient.browser" in str(exc_info.value)
