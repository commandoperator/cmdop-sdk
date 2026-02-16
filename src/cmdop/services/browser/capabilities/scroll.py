"""Scroll capability."""

import time
from typing import Any, Callable

from cmdop.services.browser.js import (
    build_scroll_js,
    build_scroll_to_bottom_js,
    build_get_scroll_info_js,
    build_infinite_scroll_js,
)
from cmdop.services.browser.models import ScrollResult, ScrollInfo, InfiniteScrollResult

from ._base import BaseCapability
from ._helpers import to_dict


class ScrollCapability(BaseCapability):
    """Scroll operations.

    Usage:
        session.scroll.js("down", 500)
        session.scroll.to_bottom()
        info = session.scroll.info()
    """

    def js(
        self,
        direction: str = "down",
        amount: int = 500,
        selector: str | None = None,
        smooth: bool = True,
        human_like: bool = False,
        container: str | None = None,
    ) -> ScrollResult:
        """Scroll using JavaScript. Use when native scroll doesn't work."""
        js = build_scroll_js(direction, amount, selector, smooth, human_like, container)
        data = to_dict(self._js(js))
        return ScrollResult(
            success=data.get("success", False),
            scroll_y=int(data.get("scrollY", 0)),
            scrolled_by=int(data.get("scrolledBy", 0)),
            at_bottom=data.get("atBottom", False),
            error=data.get("error"),
        )

    def to_bottom(self) -> ScrollResult:
        """Scroll to page bottom."""
        data = to_dict(self._js(build_scroll_to_bottom_js()))
        return ScrollResult(
            success=data.get("success", False),
            scroll_y=int(data.get("scrollY", 0)),
            scrolled_by=int(data.get("scrolledBy", 0)),
            at_bottom=True,
        )

    def to_element(self, selector: str) -> ScrollResult:
        """Scroll element into view."""
        return self.js(selector=selector)

    def info(self) -> ScrollInfo:
        """Get scroll position and page dimensions."""
        data = to_dict(self._js(build_get_scroll_info_js()))
        return ScrollInfo(
            scroll_x=int(data.get("scrollX", 0)),
            scroll_y=int(data.get("scrollY", 0)),
            page_height=int(data.get("pageHeight", 0)),
            page_width=int(data.get("pageWidth", 0)),
            viewport_height=int(data.get("viewportHeight", 0)),
            viewport_width=int(data.get("viewportWidth", 0)),
            at_bottom=data.get("atBottom", False),
            at_top=data.get("atTop", True),
        )

    def native(
        self,
        direction: str = "down",
        amount: int = 500,
        selector: str | None = None,
        smooth: bool = True,
    ) -> ScrollResult:
        """Scroll using native browser API."""
        data = self._call("scroll", direction, amount, selector, smooth)
        return ScrollResult(
            success=True,
            scroll_y=data.get("scroll_y", 0),
            scrolled_by=data.get("scrolled_by", 0),
            at_bottom=data.get("at_bottom", False),
        )

    def collect(
        self,
        seen_keys: set[str],
        key_selector: str = "a[href]",
        key_attr: str = "href",
        container_selector: str = "body",
    ) -> InfiniteScrollResult:
        """Extract new keys for infinite scroll patterns. Updates seen_keys in-place."""
        js = build_infinite_scroll_js(list(seen_keys), key_selector, key_attr, container_selector)
        data = to_dict(self._js(js))
        new_keys = data.get("new_keys", [])
        seen_keys.update(new_keys)
        return InfiniteScrollResult(
            new_keys=new_keys,
            at_bottom=data.get("at_bottom", False),
            total_seen=data.get("total_seen", len(seen_keys)),
            error=data.get("error"),
        )

    def infinite(
        self,
        extract_fn: Callable[[], list[Any]],
        limit: int = 100,
        max_scrolls: int = 50,
        max_no_new: int = 3,
        scroll_amount: int = 800,
        delay: float = 1.0,
    ) -> list[Any]:
        """Smart infinite scroll with extraction.

        Args:
            extract_fn: Returns new items each call (dedup is caller's job)
            limit: Stop after this many items
            max_scrolls: Max scroll attempts
            max_no_new: Stop after N scrolls with no new items
            scroll_amount: Pixels per scroll
            delay: Seconds between scrolls
        """
        items: list[Any] = []
        no_new = 0

        for _ in range(max_scrolls):
            new = extract_fn()
            if new:
                items.extend(new)
                no_new = 0
                if len(items) >= limit:
                    break
            else:
                no_new += 1
                if no_new >= max_no_new:
                    break

            self.js("down", scroll_amount)
            time.sleep(delay)

        return items[:limit]
