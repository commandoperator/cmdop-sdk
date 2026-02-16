"""Browser session with capability-based API."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

from cmdop.services.browser.models import BrowserCookie, BrowserState, PageInfo, WaitUntil

from .capabilities import (
    ScrollCapability,
    InputCapability,
    TimingCapability,
    DOMCapability,
    FetchCapability,
    NetworkCapability,
    VisualCapability,
)

if TYPE_CHECKING:
    from cmdop.services.browser.service.sync import BrowserService


class BrowserSession:
    """Browser session with grouped capabilities.

    Core methods (on session directly):
        session.navigate(url)
        session.click(selector)
        session.type(selector, text)
        session.wait_for(selector)
        session.execute_script(js)

    Capabilities (grouped by function):
        session.scroll.js("down", 500)
        session.scroll.to_bottom()
        session.input.click_js(selector)
        session.input.key("Escape")
        session.timing.wait(1000)
        session.dom.soup()
        session.fetch.json("/api/data")

    Usage:
        with service.create_session() as session:
            session.navigate("https://example.com")
            session.scroll.js("down", 500)
            session.input.click_js(".button")
    """

    __slots__ = (
        "_service",
        "_session_id",
        "_scroll",
        "_input",
        "_timing",
        "_dom",
        "_fetch",
        "_network",
        "_visual",
    )

    def __init__(self, service: "BrowserService", session_id: str) -> None:
        self._service = service
        self._session_id = session_id
        self._scroll: ScrollCapability | None = None
        self._input: InputCapability | None = None
        self._timing: TimingCapability | None = None
        self._dom: DOMCapability | None = None
        self._fetch: FetchCapability | None = None
        self._network: NetworkCapability | None = None
        self._visual: VisualCapability | None = None

    @property
    def session_id(self) -> str:
        return self._session_id

    # === Capabilities (lazy init) ===

    @property
    def scroll(self) -> ScrollCapability:
        """Scroll: js(), to_bottom(), to_element(), info(), native(), collect()"""
        if self._scroll is None:
            self._scroll = ScrollCapability(self)
        return self._scroll

    @property
    def input(self) -> InputCapability:
        """Input: click_js(), key(), click_all(), hover(), hover_js()"""
        if self._input is None:
            self._input = InputCapability(self)
        return self._input

    @property
    def timing(self) -> TimingCapability:
        """Timing: wait(), seconds(), random(), timeout()"""
        if self._timing is None:
            self._timing = TimingCapability(self)
        return self._timing

    @property
    def dom(self) -> DOMCapability:
        """DOM: html(), text(), soup(), parse(), select(), close_modal(), extract()"""
        if self._dom is None:
            self._dom = DOMCapability(self)
        return self._dom

    @property
    def fetch(self) -> FetchCapability:
        """Fetch: json(), all(), execute()"""
        if self._fetch is None:
            self._fetch = FetchCapability(self)
        return self._fetch

    @property
    def network(self) -> NetworkCapability:
        """Network: enable(), disable(), get_all(), filter(), last(), clear(), stats()"""
        if self._network is None:
            self._network = NetworkCapability(self)
        return self._network

    @property
    def visual(self) -> VisualCapability:
        """Visual: toast(), click(), move(), highlight(), hide_highlight(), clear_trail(), set_state()"""
        if self._visual is None:
            self._visual = VisualCapability(self)
        return self._visual

    # === Core Methods ===

    def navigate(
        self,
        url: str,
        timeout_ms: int = 30000,
        wait_until: WaitUntil = WaitUntil.LOAD,
    ) -> str:
        """Navigate to URL with specified wait strategy.

        Args:
            url: URL to navigate to.
            timeout_ms: Timeout in milliseconds.
            wait_until: When navigation is considered complete:
                - WaitUntil.LOAD: Wait for load event (default, slow for SPA)
                - WaitUntil.DOMCONTENTLOADED: Wait for DOMContentLoaded event
                - WaitUntil.NETWORKIDLE: Wait until network is idle (best for SPA)
                - WaitUntil.COMMIT: Return immediately (fastest)

        Returns:
            Final URL after navigation (may differ due to redirects).
        """
        return self._service.navigate(self._session_id, url, timeout_ms, wait_until)

    def click(self, selector: str, timeout_ms: int = 5000, move_cursor: bool = False) -> None:
        """Click element by CSS selector."""
        self._service.click(self._session_id, selector, timeout_ms, move_cursor)

    def type(self, selector: str, text: str, human_like: bool = False, clear_first: bool = True) -> None:
        """Type text into element."""
        self._service.type(self._session_id, selector, text, human_like, clear_first)

    def wait_for(self, selector: str, timeout_ms: int = 30000) -> bool:
        """Wait for element to appear."""
        return self._service.wait_for(self._session_id, selector, timeout_ms)

    def execute_script(self, script: str) -> str:
        """Execute raw JavaScript."""
        return self._service.execute_script(self._session_id, script)

    # === State ===

    def screenshot(self, full_page: bool = False) -> bytes:
        """Take screenshot."""
        return self._service.screenshot(self._session_id, full_page)

    def get_state(self) -> BrowserState:
        """Get browser state."""
        return self._service.get_state(self._session_id)

    def get_cookies(self, domain: str = "") -> list[BrowserCookie]:
        """Get cookies."""
        return self._service.get_cookies(self._session_id, domain)

    def set_cookies(self, cookies: list[BrowserCookie | dict]) -> None:
        """Set cookies."""
        self._service.set_cookies(self._session_id, cookies)

    def get_page_info(self) -> PageInfo:
        """Get page info."""
        return self._service.get_page_info(self._session_id)

    # === Internal ===

    def _call_service(self, method: str, *args: Any, **kwargs: Any) -> Any:
        """Call service method (used by capabilities)."""
        return getattr(self._service, method)(self._session_id, *args, **kwargs)

    # === Context Manager ===

    def close(self) -> None:
        """Close session."""
        self._service.close_session(self._session_id)

    def __enter__(self) -> "BrowserSession":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
