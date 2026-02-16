"""Browser SDK with capability-based API.

Usage:
    from cmdop.services.browser import BrowserSession

    with service.create_session() as session:
        session.navigate("https://example.com")

        # Capabilities
        session.scroll.js("down", 500)
        session.scroll.to_bottom()

        session.input.click_js(".button")
        session.input.key("Escape")

        session.timing.wait(1000)

        soup = session.dom.soup()
        data = session.fetch.json("/api/data")
"""

from .session import BrowserSession
from .service.sync import BrowserService
from .service.aio import AsyncBrowserService
from .models import (
    BrowserCookie,
    BrowserState,
    PageInfo,
    ScrollResult,
    ScrollInfo,
    InfiniteScrollResult,
)
from .capabilities import (
    ScrollCapability,
    InputCapability,
    TimingCapability,
    DOMCapability,
    FetchCapability,
)

__all__ = [
    # Session & Service
    "BrowserSession",
    "BrowserService",
    "AsyncBrowserService",
    # Models
    "BrowserCookie",
    "BrowserState",
    "PageInfo",
    "ScrollResult",
    "ScrollInfo",
    "InfiniteScrollResult",
    # Capabilities
    "ScrollCapability",
    "InputCapability",
    "TimingCapability",
    "DOMCapability",
    "FetchCapability",
]
