"""Tests for BrowserService creation and session management."""

from unittest.mock import MagicMock

import pytest

from cmdop.exceptions import BrowserError
from cmdop.services.browser import BrowserService, BrowserSession

from .conftest import MockTransport


class TestBrowserServiceCreation:
    """Test BrowserService initialization."""

    def test_service_creation(self):
        """Test service can be created with transport."""
        transport = MockTransport()
        service = BrowserService(transport)
        assert service._transport == transport
        assert service._stub is None

    def test_transport_property(self):
        """Test transport property access."""
        transport = MockTransport()
        service = BrowserService(transport)
        assert service.transport == transport


class TestBrowserServiceCreateSession:
    """Test BrowserService.create_session method."""

    def test_create_session_default(self):
        """Test creating session with defaults."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.browser_session_id = "browser-123"
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserCreateSession = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        session = service.create_session()

        assert isinstance(session, BrowserSession)
        assert session.session_id == "browser-123"

    def test_create_session_with_options(self):
        """Test creating session with custom options."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.browser_session_id = "browser-456"
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserCreateSession = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        session = service.create_session(
            headless=False,
            provider="camoufox",
            profile_id="my-profile",
            start_url="https://example.com",
        )

        assert session.session_id == "browser-456"
        mock_stub.BrowserCreateSession.assert_called_once()

    def test_create_session_failure(self):
        """Test create session returns error on failure."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = False
        mock_response.browser_session_id = ""
        mock_response.error = "browser not available"

        mock_stub = MagicMock()
        mock_stub.BrowserCreateSession = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with pytest.raises(BrowserError):
            service.create_session()
