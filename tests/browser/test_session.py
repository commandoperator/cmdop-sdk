"""Tests for BrowserSession with capability-based API."""

from unittest.mock import MagicMock

import pytest

from cmdop.services.browser import BrowserSession
from cmdop.services.browser.models import WaitUntil


class TestBrowserSessionCore:
    """Test BrowserSession core methods."""

    def test_session_id_property(self):
        """Test session_id property."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")
        assert session.session_id == "session-123"

    def test_navigate(self):
        """Test navigate method."""
        mock_service = MagicMock()
        mock_service.navigate.return_value = "https://example.com/"

        session = BrowserSession(mock_service, "session-123")
        result = session.navigate("https://example.com")

        assert result == "https://example.com/"
        mock_service.navigate.assert_called_once_with(
            "session-123", "https://example.com", 30000, WaitUntil.LOAD
        )

    def test_click(self):
        """Test click method."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")
        session.click("button.submit")

        mock_service.click.assert_called_once_with(
            "session-123", "button.submit", 5000, False
        )

    def test_click_with_move_cursor(self):
        """Test click with move_cursor option."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")
        session.click("button.submit", move_cursor=True)

        mock_service.click.assert_called_once_with(
            "session-123", "button.submit", 5000, True
        )

    def test_type(self):
        """Test type method."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")
        session.type("input[name='q']", "test")

        mock_service.type.assert_called_once_with(
            "session-123", "input[name='q']", "test", False, True
        )

    def test_wait_for(self):
        """Test wait_for method."""
        mock_service = MagicMock()
        mock_service.wait_for.return_value = True

        session = BrowserSession(mock_service, "session-123")
        result = session.wait_for(".loaded")

        assert result is True
        mock_service.wait_for.assert_called_once()

    def test_execute_script(self):
        """Test execute_script method."""
        mock_service = MagicMock()
        mock_service.execute_script.return_value = '{"result": 42}'

        session = BrowserSession(mock_service, "session-123")
        result = session.execute_script("return {result: 42}")

        assert result == '{"result": 42}'

    def test_screenshot(self):
        """Test screenshot method."""
        mock_service = MagicMock()
        mock_service.screenshot.return_value = b"PNG..."

        session = BrowserSession(mock_service, "session-123")
        result = session.screenshot()

        assert result == b"PNG..."

    def test_get_state(self):
        """Test get_state method."""
        mock_service = MagicMock()
        mock_state = MagicMock()
        mock_state.url = "https://example.com"
        mock_state.title = "Example"
        mock_service.get_state.return_value = mock_state

        session = BrowserSession(mock_service, "session-123")
        result = session.get_state()

        assert result.url == "https://example.com"

    def test_get_cookies(self):
        """Test get_cookies method."""
        mock_service = MagicMock()
        mock_service.get_cookies.return_value = []

        session = BrowserSession(mock_service, "session-123")
        result = session.get_cookies()

        assert result == []

    def test_set_cookies(self):
        """Test set_cookies method."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")
        session.set_cookies([{"name": "test", "value": "123"}])

        mock_service.set_cookies.assert_called_once()

    def test_get_page_info(self):
        """Test get_page_info method."""
        mock_service = MagicMock()
        mock_info = MagicMock()
        mock_info.url = "https://example.com"
        mock_service.get_page_info.return_value = mock_info

        session = BrowserSession(mock_service, "session-123")
        result = session.get_page_info()

        assert result.url == "https://example.com"

    def test_close(self):
        """Test close method."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")
        session.close()

        mock_service.close_session.assert_called_once_with("session-123")

    def test_context_manager(self):
        """Test session as context manager."""
        mock_service = MagicMock()

        with BrowserSession(mock_service, "session-123") as session:
            assert session.session_id == "session-123"

        mock_service.close_session.assert_called_once_with("session-123")

    def test_context_manager_on_error(self):
        """Test session closes on error within context."""
        mock_service = MagicMock()
        mock_service.navigate.side_effect = RuntimeError("Navigation failed")

        with pytest.raises(RuntimeError):
            with BrowserSession(mock_service, "session-123") as session:
                session.navigate("https://example.com")

        mock_service.close_session.assert_called_once_with("session-123")


class TestBrowserSessionCapabilities:
    """Test BrowserSession capabilities are lazy-loaded."""

    def test_scroll_capability(self):
        """Test scroll capability is lazy-loaded."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")

        assert session._scroll is None
        scroll = session.scroll
        assert scroll is not None
        assert session._scroll is scroll
        # Second access returns same instance
        assert session.scroll is scroll

    def test_input_capability(self):
        """Test input capability is lazy-loaded."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")

        assert session._input is None
        inp = session.input
        assert inp is not None
        assert session._input is inp

    def test_timing_capability(self):
        """Test timing capability is lazy-loaded."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")

        assert session._timing is None
        timing = session.timing
        assert timing is not None
        assert session._timing is timing

    def test_dom_capability(self):
        """Test dom capability is lazy-loaded."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")

        assert session._dom is None
        dom = session.dom
        assert dom is not None
        assert session._dom is dom

    def test_fetch_capability(self):
        """Test fetch capability is lazy-loaded."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")

        assert session._fetch is None
        fetch = session.fetch
        assert fetch is not None
        assert session._fetch is fetch


class TestBrowserSessionDOMCapability:
    """Test DOM capability through session."""

    def test_dom_html(self):
        """Test dom.html() method."""
        mock_service = MagicMock()
        mock_service.get_html.return_value = "<html>...</html>"

        session = BrowserSession(mock_service, "session-123")
        result = session.dom.html()

        assert "<html>" in result

    def test_dom_text(self):
        """Test dom.text() method."""
        mock_service = MagicMock()
        mock_service.get_text.return_value = "Page text"

        session = BrowserSession(mock_service, "session-123")
        result = session.dom.text()

        assert result == "Page text"

    def test_dom_extract(self):
        """Test dom.extract() method."""
        mock_service = MagicMock()
        mock_service.extract.return_value = ["text1", "text2"]

        session = BrowserSession(mock_service, "session-123")
        result = session.dom.extract(".item")

        assert result == ["text1", "text2"]

    def test_dom_extract_regex(self):
        """Test dom.extract_regex() method."""
        mock_service = MagicMock()
        mock_service.extract_regex.return_value = ["123", "456"]

        session = BrowserSession(mock_service, "session-123")
        result = session.dom.extract_regex(r"\d+")

        assert result == ["123", "456"]

    def test_dom_validate_selectors(self):
        """Test dom.validate_selectors() method."""
        mock_service = MagicMock()
        mock_service.validate_selectors.return_value = {
            "valid": True,
            "counts": {"title": 5},
            "samples": {"title": "Test"},
            "errors": [],
        }

        session = BrowserSession(mock_service, "session-123")
        result = session.dom.validate_selectors(".item", {"title": ".title"})

        assert result["valid"] is True

    def test_dom_extract_data(self):
        """Test dom.extract_data() method."""
        mock_service = MagicMock()
        mock_service.extract_data.return_value = {
            "items": [{"title": "Item 1"}],
            "count": 1,
        }

        session = BrowserSession(mock_service, "session-123")
        result = session.dom.extract_data(".item", '{"title": ".title"}', limit=50)

        assert result["count"] == 1


class TestBrowserSessionFetchCapability:
    """Test Fetch capability through session."""

    def test_fetch_json(self):
        """Test fetch.json() method."""
        mock_service = MagicMock()
        mock_service.execute_script.return_value = '{"data": [1, 2, 3]}'

        session = BrowserSession(mock_service, "session-123")
        result = session.fetch.json("/api/data")

        assert result == {"data": [1, 2, 3]}

    def test_fetch_all(self):
        """Test fetch.all() method."""
        mock_service = MagicMock()
        mock_service.execute_script.return_value = '{"a": {"data": {"id": 1}, "error": null}}'

        session = BrowserSession(mock_service, "session-123")
        result = session.fetch.all({"a": "/api/a"})

        assert "a" in result
        assert result["a"]["data"] == {"id": 1}

    def test_fetch_all_empty(self):
        """Test fetch.all() with empty urls returns empty dict."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")
        result = session.fetch.all({})

        assert result == {}
        mock_service.execute_script.assert_not_called()


class TestBrowserSessionScrollCapability:
    """Test Scroll capability through session."""

    def test_scroll_js(self):
        """Test scroll.js() method."""
        mock_service = MagicMock()
        mock_service.execute_script.return_value = '{"success": true, "scrollY": 500, "atBottom": false}'

        session = BrowserSession(mock_service, "session-123")
        result = session.scroll.js("down", 500)

        assert result.success is True
        assert result.scroll_y == 500

    def test_scroll_native(self):
        """Test scroll.native() method."""
        mock_service = MagicMock()
        mock_service.scroll.return_value = {"scroll_y": 500, "scrolled_by": 500, "at_bottom": False}

        session = BrowserSession(mock_service, "session-123")
        result = session.scroll.native("down", 500)

        assert result.scroll_y == 500

    def test_scroll_info(self):
        """Test scroll.info() method."""
        mock_service = MagicMock()
        mock_service.execute_script.return_value = '{"scrollY": 100, "pageHeight": 2000, "viewportHeight": 800}'

        session = BrowserSession(mock_service, "session-123")
        result = session.scroll.info()

        assert result.scroll_y == 100
        assert result.page_height == 2000


class TestBrowserSessionInputCapability:
    """Test Input capability through session."""

    def test_input_click_js(self):
        """Test input.click_js() method."""
        mock_service = MagicMock()
        mock_service.execute_script.return_value = '{"success": true}'

        session = BrowserSession(mock_service, "session-123")
        result = session.input.click_js(".button")

        assert result is True

    def test_input_key(self):
        """Test input.key() method."""
        mock_service = MagicMock()
        mock_service.execute_script.return_value = '{"success": true}'

        session = BrowserSession(mock_service, "session-123")
        result = session.input.key("Escape")

        assert result is True

    def test_input_mouse_move(self):
        """Test input.mouse_move() method."""
        mock_service = MagicMock()
        session = BrowserSession(mock_service, "session-123")
        session.input.mouse_move(100, 200)

        mock_service.mouse_move.assert_called_once()


class TestBrowserSessionTimingCapability:
    """Test Timing capability through session."""

    def test_timing_wait(self):
        """Test timing.wait() method."""
        mock_service = MagicMock()
        mock_service.execute_script.return_value = '{"waited": 1000}'

        session = BrowserSession(mock_service, "session-123")
        # Should not raise
        session.timing.wait(1000)
