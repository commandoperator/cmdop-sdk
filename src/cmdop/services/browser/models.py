"""Browser models and error handling."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel

from cmdop.exceptions import (
    BrowserElementNotFoundError,
    BrowserError,
    BrowserNavigationError,
    BrowserSessionClosedError,
)


class WaitUntil(str, Enum):
    """Wait strategy for navigation.

    Determines when navigation is considered complete.
    """

    LOAD = "load"
    """Wait for load event (default, not recommended for SPA)."""

    DOMCONTENTLOADED = "domcontentloaded"
    """Wait for DOMContentLoaded event."""

    NETWORKIDLE = "networkidle"
    """Wait until no network activity for 500ms (best for SPA)."""

    COMMIT = "commit"
    """Return immediately after navigation commits (fastest)."""


def raise_browser_error(error: str, operation: str, **context: Any) -> None:
    """Raise appropriate browser exception based on error message."""
    error_lower = error.lower()

    if "target closed" in error_lower or "context closed" in error_lower:
        raise BrowserSessionClosedError(error)

    if operation == "navigate":
        raise BrowserNavigationError(context.get("url", ""), error)

    if "element not found" in error_lower or "no element" in error_lower:
        raise BrowserElementNotFoundError(context.get("selector", ""), operation)

    raise BrowserError(f"{operation} failed: {error}")


class BrowserCookie(BaseModel):
    """Browser cookie."""

    name: str
    value: str
    domain: str = ""
    path: str = "/"
    secure: bool = False
    http_only: bool = False
    same_site: str = ""
    expires: int = 0


class BrowserState(BaseModel):
    """Current browser state."""

    url: str
    title: str


class ScrollInfo(BaseModel):
    """Scroll position and page dimensions."""

    scroll_x: int = 0
    scroll_y: int = 0
    page_height: int = 0
    page_width: int = 0
    viewport_height: int = 0
    viewport_width: int = 0
    at_bottom: bool = False
    at_top: bool = True


class ScrollResult(BaseModel):
    """Result of scroll operation (v2.18.0)."""

    success: bool = True
    scroll_x: int = 0
    scroll_y: int = 0
    scrolled_by: int = 0
    page_height: int = 0
    viewport_height: int = 0
    at_bottom: bool = False
    error: str | None = None


class PageInfo(BaseModel):
    """Comprehensive page information (v2.18.0)."""

    # Basic
    url: str = ""
    title: str = ""
    page_height: int = 0
    viewport_height: int = 0
    viewport_width: int = 0

    # Scroll position
    scroll_x: int = 0
    scroll_y: int = 0
    at_top: bool = True
    at_bottom: bool = False

    # Technical
    load_time_ms: int = 0
    cookies_count: int = 0
    is_https: bool = False
    has_iframes: bool = False

    # DOM complexity
    dom_nodes_raw: int = 0
    dom_nodes_cleaned: int = 0
    tokens_estimate: int = 0

    # Protection detection
    cloudflare_detected: bool = False
    captcha_detected: bool = False


class InfiniteScrollResult(BaseModel):
    """Result of infinite scroll extraction."""

    new_keys: list[str] = []
    at_bottom: bool = False
    total_seen: int = 0
    error: str | None = None


# =============================================================================
# Network Capture Models (v2.19.0)
# =============================================================================


class NetworkRequest(BaseModel):
    """Captured HTTP request."""

    url: str = ""
    method: str = "GET"
    headers: dict[str, str] = {}
    body: bytes = b""
    content_type: str = ""
    resource_type: str = ""  # document, script, xhr, fetch, image, etc.


class NetworkResponse(BaseModel):
    """Captured HTTP response."""

    status: int = 0
    status_text: str = ""
    headers: dict[str, str] = {}
    body: bytes = b""
    content_type: str = ""
    size: int = 0
    from_cache: bool = False


class NetworkTiming(BaseModel):
    """Request timing data."""

    started_at_ms: int = 0
    ended_at_ms: int = 0
    duration_ms: int = 0
    wait_time_ms: int = 0  # Time to first byte
    receive_time_ms: int = 0  # Time to download body


class NetworkExchange(BaseModel):
    """Complete request/response exchange."""

    id: str = ""
    request: NetworkRequest = NetworkRequest()
    response: NetworkResponse | None = None
    timing: NetworkTiming = NetworkTiming()
    error: str = ""
    frame_id: str = ""
    initiator: str = ""  # URL or script that initiated

    def json_body(self) -> Any:
        """Parse response body as JSON."""
        import json
        if self.response and self.response.body:
            return json.loads(self.response.body)
        return None

    def text_body(self) -> str:
        """Get response body as text."""
        if self.response and self.response.body:
            return self.response.body.decode("utf-8", errors="replace")
        return ""


class NetworkStats(BaseModel):
    """Network capture statistics."""

    enabled: bool = False
    total_captured: int = 0
    total_errors: int = 0
    total_bytes: int = 0
    average_duration_ms: int = 0


class NetworkFilter(BaseModel):
    """Filter for querying captured exchanges."""

    url_pattern: str = ""
    methods: list[str] = []
    status_codes: list[int] = []
    resource_types: list[str] = []
    limit: int = 0
