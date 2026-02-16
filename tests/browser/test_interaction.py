"""Tests for browser interaction methods (click, type, wait)."""

from unittest.mock import MagicMock

import pytest

from cmdop.exceptions import BrowserElementNotFoundError, BrowserError
from cmdop.services.browser import BrowserService

from .conftest import MockTransport


class TestBrowserServiceClick:
    """Test BrowserService.click method."""

    def test_click_success(self):
        """Test successful click."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserClick = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        # Should not raise
        service.click("session-123", "button.submit")

    def test_click_element_not_found(self):
        """Test click when element not found."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = False
        mock_response.error = "element not found: .nonexistent"

        mock_stub = MagicMock()
        mock_stub.BrowserClick = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with pytest.raises(BrowserError):
            service.click("session-123", ".nonexistent")

    def test_click_with_timeout(self):
        """Test click with custom timeout."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserClick = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        service.click("session-123", "button", timeout_ms=10000)
        mock_stub.BrowserClick.assert_called_once()


class TestBrowserServiceType:
    """Test BrowserService.type method."""

    def test_type_success(self):
        """Test successful typing."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserType = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        # Should not raise
        service.type("session-123", "input[name='q']", "test query")

    def test_type_with_clear(self):
        """Test typing with clear option."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserType = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        service.type("session-123", "input", "text", clear_first=True, human_like=True)
        mock_stub.BrowserType.assert_called_once()

    def test_type_failure(self):
        """Test type failure when element not found."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = False
        mock_response.error = "element not found"

        mock_stub = MagicMock()
        mock_stub.BrowserType = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with pytest.raises(BrowserError):
            service.type("session-123", "input.missing", "text")


class TestBrowserServiceWait:
    """Test BrowserService.wait_for method."""

    def test_wait_found(self):
        """Test wait when element found."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.found = True
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserWait = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.wait_for("session-123", ".loaded")
        assert result is True

    def test_wait_not_found(self):
        """Test wait when element not found within timeout."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.found = False
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserWait = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.wait_for("session-123", ".missing", timeout_ms=5000)
        assert result is False
