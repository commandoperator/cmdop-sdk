"""Input capability."""

from cmdop.services.browser.js import (
    build_click_js,
    build_press_key_js,
    build_click_all_by_text_js,
    build_hover_js,
)

from ._base import BaseCapability
from ._helpers import to_dict


class InputCapability(BaseCapability):
    """Input operations: clicks, keyboard, hover.

    Usage:
        session.input.click_js(".button")
        session.input.key("Escape")
        session.input.click_all("See more")
    """

    def click_js(self, selector: str, scroll_into_view: bool = True) -> bool:
        """Click using JavaScript. More reliable than native click."""
        js = build_click_js(selector, scroll_into_view)
        return to_dict(self._js(js)).get("success", False)

    def key(self, key: str, selector: str | None = None) -> bool:
        """Press keyboard key. Keys: Escape, Enter, Tab, ArrowDown, etc."""
        js = build_press_key_js(key, selector)
        return to_dict(self._js(js)).get("success", False)

    def click_all(self, text: str, role: str = "button") -> int:
        """Click all elements containing text. Returns count clicked."""
        js = build_click_all_by_text_js(text, role)
        return to_dict(self._js(js)).get("clicked", 0)

    def hover_js(self, selector: str) -> bool:
        """Hover using JavaScript."""
        js = build_hover_js(selector)
        return to_dict(self._js(js)).get("success", False)

    def hover(self, selector: str, timeout_ms: int = 5000) -> None:
        """Hover using native browser API."""
        self._call("hover", selector, timeout_ms)

    def mouse_move(self, x: int, y: int, steps: int = 10) -> None:
        """Move mouse to coordinates with human-like movement."""
        self._call("mouse_move", x, y, steps)
