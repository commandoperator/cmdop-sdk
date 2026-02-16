"""Tests for browser state methods (HTML, screenshot, state, cookies)."""

from unittest.mock import MagicMock

import pytest

from cmdop.services.browser import BrowserService, BrowserState, BrowserCookie

from .conftest import MockTransport


class TestBrowserServiceGetHtml:
    """Test BrowserService.get_html method."""

    def test_get_html_full_page(self):
        """Test getting full page HTML."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.html = "<html><body>Hello</body></html>"
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserGetHTML = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.get_html("session-123")

        assert "<body>Hello</body>" in result

    def test_get_html_selector(self):
        """Test getting HTML of specific element."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.html = "<div class='content'>Text</div>"
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserGetHTML = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.get_html("session-123", selector=".content")

        assert "content" in result


class TestBrowserServiceGetText:
    """Test BrowserService.get_text method."""

    def test_get_text(self):
        """Test getting clean text."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.text = "Hello World"
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserGetText = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.get_text("session-123")

        assert result == "Hello World"


class TestBrowserServiceScreenshot:
    """Test BrowserService.screenshot method."""

    def test_screenshot(self):
        """Test taking screenshot."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.data = b"\x89PNG\r\n\x1a\n..."
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserScreenshot = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.screenshot("session-123")

        assert result.startswith(b"\x89PNG")

    def test_screenshot_full_page(self):
        """Test taking full page screenshot."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.data = b"\x89PNG..."
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserScreenshot = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.screenshot("session-123", full_page=True)

        assert result.startswith(b"\x89PNG")
        mock_stub.BrowserScreenshot.assert_called_once()


class TestBrowserServiceGetState:
    """Test BrowserService.get_state method."""

    def test_get_state(self):
        """Test getting browser state."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.url = "https://example.com/page"
        mock_response.title = "Example Page"
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserGetState = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.get_state("session-123")

        assert isinstance(result, BrowserState)
        assert result.url == "https://example.com/page"
        assert result.title == "Example Page"


class TestBrowserServiceCookies:
    """Test BrowserService cookie methods."""

    def test_set_cookies(self):
        """Test setting cookies."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserSetCookies = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        cookies = [
            {"name": "session", "value": "abc123", "domain": "example.com"}
        ]
        service.set_cookies("session-123", cookies)

        mock_stub.BrowserSetCookies.assert_called_once()

    def test_set_cookies_with_browser_cookie(self):
        """Test setting cookies with BrowserCookie objects."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserSetCookies = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        cookies = [
            BrowserCookie(
                name="session",
                value="abc123",
                domain="example.com",
                path="/",
                secure=True,
                http_only=True,
                same_site="Lax",
                expires=0,
            )
        ]
        service.set_cookies("session-123", cookies)

        mock_stub.BrowserSetCookies.assert_called_once()

    def test_get_cookies(self):
        """Test getting cookies."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_cookie = MagicMock()
        mock_cookie.name = "session"
        mock_cookie.value = "abc123"
        mock_cookie.domain = "example.com"
        mock_cookie.path = "/"
        mock_cookie.secure = True
        mock_cookie.http_only = True
        mock_cookie.same_site = "Lax"
        mock_cookie.expires = 0

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.cookies = [mock_cookie]
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserGetCookies = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.get_cookies("session-123")

        assert len(result) == 1
        assert isinstance(result[0], BrowserCookie)
        assert result[0].name == "session"
        assert result[0].value == "abc123"

    def test_get_cookies_by_domain(self):
        """Test getting cookies filtered by domain."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_cookie = MagicMock()
        mock_cookie.name = "test"
        mock_cookie.value = "value"
        mock_cookie.domain = "example.com"
        mock_cookie.path = "/"
        mock_cookie.secure = False
        mock_cookie.http_only = False
        mock_cookie.same_site = ""
        mock_cookie.expires = 0

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.cookies = [mock_cookie]
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserGetCookies = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.get_cookies("session-123", domain="example.com")

        assert len(result) == 1
        mock_stub.BrowserGetCookies.assert_called_once()
