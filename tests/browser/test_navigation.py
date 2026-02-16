"""Tests for browser navigation methods."""

from unittest.mock import MagicMock

import pytest

from cmdop.exceptions import BrowserNavigationError
from cmdop.services.browser import BrowserService

from .conftest import MockTransport


class TestBrowserServiceNavigate:
    """Test BrowserService.navigate method."""

    def test_navigate_success(self):
        """Test successful navigation."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.final_url = "https://example.com/"
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserNavigate = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.navigate("session-123", "https://example.com")

        assert result == "https://example.com/"

    def test_navigate_failure(self):
        """Test navigation failure."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = False
        mock_response.final_url = ""
        mock_response.error = "navigation timeout"

        mock_stub = MagicMock()
        mock_stub.BrowserNavigate = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with pytest.raises(BrowserNavigationError):
            service.navigate("session-123", "https://example.com")

    def test_navigate_with_custom_timeout(self):
        """Test navigation with custom timeout."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.final_url = "https://example.com/"
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserNavigate = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.navigate("session-123", "https://example.com", timeout_ms=60000)

        assert result == "https://example.com/"
        mock_stub.BrowserNavigate.assert_called_once()
