"""Synchronous browser service."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from cmdop.services.base import BaseService
from cmdop.services.browser.service._helpers import BaseServiceMixin, cookie_to_pb, pb_to_cookie
from cmdop.services.browser.models import BrowserCookie, BrowserState, PageInfo, WaitUntil, raise_browser_error

if TYPE_CHECKING:
    from cmdop.transport.base import BaseTransport


class BrowserService(BaseService, BaseServiceMixin):
    """
    Synchronous browser service.

    Example:
        with client.browser.create_session() as session:
            session.navigate("https://google.com")
            session.type("input[name='q']", "Python")
            results = session.extract(".result-title")
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None

    @property
    def _get_stub(self) -> Any:
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import TerminalStreamingServiceStub
            self._stub = TerminalStreamingServiceStub(self._channel)
        return self._stub

    # === Session Management ===

    def create_session(
        self,
        start_url: str | None = None,
        provider: str = "camoufox",
        profile_id: str | None = None,
        headless: bool = False,
        width: int = 1280,
        height: int = 800,
        block_images: bool = False,
        block_media: bool = False,
    ) -> "BrowserSession":
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserCreateSessionRequest
        from cmdop.services.browser.session import BrowserSession

        request = BrowserCreateSessionRequest(
            provider=provider,
            profile_id=profile_id or "",
            start_url=start_url or "",
            headless=headless,
            width=width,
            height=height,
            block_images=block_images,
            block_media=block_media,
        )
        response = self._call_sync(self._get_stub.BrowserCreateSession, request)

        if not response.success:
            raise_browser_error(response.error, "create_session")

        return BrowserSession(self, response.browser_session_id)

    def close_session(self, session_id: str) -> None:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserCloseSessionRequest

        request = BrowserCloseSessionRequest(browser_session_id=session_id)
        response = self._call_sync(self._get_stub.BrowserCloseSession, request)

        if not response.success:
            raise RuntimeError(f"Failed to close browser session: {response.error}")

    # === Navigation & Interaction ===

    def navigate(
        self,
        session_id: str,
        url: str,
        timeout_ms: int = 30000,
        wait_until: WaitUntil = WaitUntil.LOAD,
    ) -> str:
        from cmdop._generated.rpc_messages.browser_pb2 import (
            BrowserNavigateRequest,
            WaitUntil as PbWaitUntil,
        )

        # Convert Python enum to proto enum
        pb_wait_until = {
            WaitUntil.LOAD: PbWaitUntil.WAIT_LOAD,
            WaitUntil.DOMCONTENTLOADED: PbWaitUntil.WAIT_DOMCONTENTLOADED,
            WaitUntil.NETWORKIDLE: PbWaitUntil.WAIT_NETWORKIDLE,
            WaitUntil.COMMIT: PbWaitUntil.WAIT_COMMIT,
        }.get(wait_until, PbWaitUntil.WAIT_LOAD)

        request = BrowserNavigateRequest(
            browser_session_id=session_id,
            url=url,
            timeout_ms=timeout_ms,
            wait_until=pb_wait_until,
        )
        response = self._call_sync(self._get_stub.BrowserNavigate, request)

        if not response.success:
            raise_browser_error(response.error, "navigate", url=url)

        return response.final_url

    def click(
        self, session_id: str, selector: str, timeout_ms: int = 5000, move_cursor: bool = False
    ) -> None:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserClickRequest

        request = BrowserClickRequest(
            browser_session_id=session_id,
            selector=selector,
            timeout_ms=timeout_ms,
            move_cursor=move_cursor,
        )
        response = self._call_sync(self._get_stub.BrowserClick, request)

        if not response.success:
            raise_browser_error(response.error, "click", selector=selector)

    def type(
        self,
        session_id: str,
        selector: str,
        text: str,
        human_like: bool = False,
        clear_first: bool = True,
    ) -> None:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserTypeRequest

        request = BrowserTypeRequest(
            browser_session_id=session_id,
            selector=selector,
            text=text,
            human_like=human_like,
            clear_first=clear_first,
        )
        response = self._call_sync(self._get_stub.BrowserType, request)

        if not response.success:
            raise_browser_error(response.error, "type", selector=selector)

    def wait_for(self, session_id: str, selector: str, timeout_ms: int = 30000) -> bool:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserWaitRequest

        request = BrowserWaitRequest(
            browser_session_id=session_id, selector=selector, timeout_ms=timeout_ms
        )
        response = self._call_sync(self._get_stub.BrowserWait, request)

        if not response.success:
            raise_browser_error(response.error, "wait_for", selector=selector)

        return response.found

    # === Extraction ===

    def extract(
        self, session_id: str, selector: str, attr: str | None = None, limit: int = 100
    ) -> list[str]:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserExtractRequest

        request = BrowserExtractRequest(
            browser_session_id=session_id,
            selector=selector,
            attribute=attr or "",
            limit=limit,
        )
        response = self._call_sync(self._get_stub.BrowserExtract, request)

        if not response.success:
            raise RuntimeError(f"Extract failed: {response.error}")

        return list(response.values)

    def extract_regex(
        self, session_id: str, pattern: str, from_html: bool = False, limit: int = 100
    ) -> list[str]:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserExtractRegexRequest

        request = BrowserExtractRegexRequest(
            browser_session_id=session_id,
            pattern=pattern,
            from_html=from_html,
            limit=limit,
        )
        response = self._call_sync(self._get_stub.BrowserExtractRegex, request)

        if not response.success:
            raise RuntimeError(f"ExtractRegex failed: {response.error}")

        return list(response.matches)

    def get_html(self, session_id: str, selector: str | None = None) -> str:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserGetHTMLRequest

        request = BrowserGetHTMLRequest(
            browser_session_id=session_id, selector=selector or ""
        )
        response = self._call_sync(self._get_stub.BrowserGetHTML, request)

        if not response.success:
            raise RuntimeError(f"GetHTML failed: {response.error}")

        return response.html

    def get_text(self, session_id: str, selector: str | None = None) -> str:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserGetTextRequest

        request = BrowserGetTextRequest(
            browser_session_id=session_id, selector=selector or ""
        )
        response = self._call_sync(self._get_stub.BrowserGetText, request)

        if not response.success:
            raise RuntimeError(f"GetText failed: {response.error}")

        return response.text

    # === JavaScript ===

    def execute_script(self, session_id: str, script: str) -> str:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserExecuteScriptRequest

        request = BrowserExecuteScriptRequest(
            browser_session_id=session_id, script=script
        )
        response = self._call_sync(self._get_stub.BrowserExecuteScript, request)

        if not response.success:
            raise RuntimeError(f"ExecuteScript failed: {response.error}")

        return response.result

    # === State & Cookies ===

    def screenshot(self, session_id: str, full_page: bool = False) -> bytes:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserScreenshotRequest

        request = BrowserScreenshotRequest(
            browser_session_id=session_id, full_page=full_page
        )
        response = self._call_sync(self._get_stub.BrowserScreenshot, request)

        if not response.success:
            raise RuntimeError(f"Screenshot failed: {response.error}")

        return response.data

    def get_state(self, session_id: str) -> BrowserState:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserGetStateRequest

        request = BrowserGetStateRequest(browser_session_id=session_id)
        response = self._call_sync(self._get_stub.BrowserGetState, request)

        if not response.success:
            raise RuntimeError(f"GetState failed: {response.error}")

        return BrowserState(url=response.url, title=response.title)

    def set_cookies(self, session_id: str, cookies: list[BrowserCookie | dict]) -> None:
        from cmdop._generated.rpc_messages.browser_pb2 import (
            BrowserCookie as PbCookie,
            BrowserSetCookiesRequest,
        )

        pb_cookies = [cookie_to_pb(c, PbCookie) for c in cookies]
        request = BrowserSetCookiesRequest(
            browser_session_id=session_id, cookies=pb_cookies
        )
        response = self._call_sync(self._get_stub.BrowserSetCookies, request)

        if not response.success:
            raise RuntimeError(f"SetCookies failed: {response.error}")

    def get_cookies(self, session_id: str, domain: str = "") -> list[BrowserCookie]:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserGetCookiesRequest

        request = BrowserGetCookiesRequest(
            browser_session_id=session_id, domain=domain
        )
        response = self._call_sync(self._get_stub.BrowserGetCookies, request)

        if not response.success:
            raise RuntimeError(f"GetCookies failed: {response.error}")

        return [pb_to_cookie(c) for c in response.cookies]

    # === Mouse & Scroll (v2.18.0) ===

    def mouse_move(
        self, session_id: str, x: int, y: int, steps: int = 10
    ) -> None:
        """
        Move mouse to coordinates with human-like movement.

        Args:
            session_id: Browser session ID
            x: Target X coordinate
            y: Target Y coordinate
            steps: Number of intermediate steps (1 = instant, >1 = smooth)
        """
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserMouseMoveRequest

        request = BrowserMouseMoveRequest(
            browser_session_id=session_id, x=x, y=y, steps=steps
        )
        response = self._call_sync(self._get_stub.BrowserMouseMove, request)

        if not response.success:
            raise RuntimeError(f"MouseMove failed: {response.error}")

    def hover(self, session_id: str, selector: str, timeout_ms: int = 5000) -> None:
        """
        Hover over an element.

        Args:
            session_id: Browser session ID
            selector: CSS selector
            timeout_ms: Timeout in milliseconds
        """
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserHoverRequest

        request = BrowserHoverRequest(
            browser_session_id=session_id, selector=selector, timeout_ms=timeout_ms
        )
        response = self._call_sync(self._get_stub.BrowserHover, request)

        if not response.success:
            raise_browser_error(response.error, "hover", selector=selector)

    def scroll(
        self,
        session_id: str,
        direction: str = "down",
        amount: int = 500,
        selector: str | None = None,
        smooth: bool = True,
    ) -> dict:
        """
        Native scroll operation.

        Args:
            session_id: Browser session ID
            direction: "up", "down", "left", "right"
            amount: Scroll amount in pixels
            selector: If provided, scroll element into view
            smooth: Use smooth scrolling

        Returns:
            dict with scroll_x, scroll_y, scrolled_by, at_bottom
        """
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserScrollRequest

        request = BrowserScrollRequest(
            browser_session_id=session_id,
            direction=direction,
            amount=amount,
            selector=selector or "",
            smooth=smooth,
        )
        response = self._call_sync(self._get_stub.BrowserScroll, request)

        if not response.success:
            raise RuntimeError(f"Scroll failed: {response.error}")

        return {
            "scroll_x": response.scroll_x,
            "scroll_y": response.scroll_y,
            "scrolled_by": response.scrolled_by,
            "page_height": response.page_height,
            "viewport_height": response.viewport_height,
            "at_bottom": response.at_bottom,
        }

    def get_page_info(self, session_id: str) -> PageInfo:
        """Get comprehensive page information (v2.18.0)."""
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserGetPageInfoRequest

        request = BrowserGetPageInfoRequest(browser_session_id=session_id)
        response = self._call_sync(self._get_stub.BrowserGetPageInfo, request)

        if not response.success:
            raise RuntimeError(f"GetPageInfo failed: {response.error}")

        return PageInfo(
            url=response.url,
            title=response.title,
            page_height=response.page_height,
            viewport_height=response.viewport_height,
            viewport_width=response.viewport_width,
            scroll_x=response.scroll_x,
            scroll_y=response.scroll_y,
            at_top=response.at_top,
            at_bottom=response.at_bottom,
            load_time_ms=response.load_time_ms,
            cookies_count=response.cookies_count,
            is_https=response.is_https,
            has_iframes=response.has_iframes,
            dom_nodes_raw=response.dom_nodes_raw,
            dom_nodes_cleaned=response.dom_nodes_cleaned,
            tokens_estimate=response.tokens_estimate,
            cloudflare_detected=response.cloudflare_detected,
            captcha_detected=response.captcha_detected,
        )

    # === Parser helpers ===

    def validate_selectors(
        self, session_id: str, item: str, fields: dict[str, str]
    ) -> dict:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserValidateSelectorsRequest

        request = BrowserValidateSelectorsRequest(
            browser_session_id=session_id,
            item=item,
            fields=fields,
        )
        response = self._call_sync(self._get_stub.BrowserValidateSelectors, request)

        if not response.success:
            raise RuntimeError(f"ValidateSelectors failed: {response.error}")

        return {
            "valid": response.valid,
            "counts": dict(response.counts),
            "samples": dict(response.samples),
            "errors": list(response.errors),
        }

    def extract_data(
        self, session_id: str, item: str, fields_json: str, limit: int = 100
    ) -> dict:
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserExtractDataRequest

        request = BrowserExtractDataRequest(
            browser_session_id=session_id,
            item=item,
            fields_json=fields_json,
            limit=limit,
        )
        response = self._call_sync(self._get_stub.BrowserExtractData, request)

        if not response.success:
            raise RuntimeError(f"ExtractData failed: {response.error}")

        return {
            "items": json.loads(response.items_json) if response.items_json else [],
            "count": response.count,
        }

    # === Network Capture (v2.19.0) ===

    def network_enable(
        self, session_id: str, max_exchanges: int = 1000, max_response_size: int = 10_000_000
    ) -> None:
        """Enable network capture."""
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserNetworkEnableRequest

        request = BrowserNetworkEnableRequest(
            browser_session_id=session_id,
            max_exchanges=max_exchanges,
            max_response_size=max_response_size,
        )
        response = self._call_sync(self._get_stub.BrowserNetworkEnable, request)

        if not response.success:
            raise RuntimeError(f"NetworkEnable failed: {response.error}")

    def network_disable(self, session_id: str) -> None:
        """Disable network capture."""
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserNetworkDisableRequest

        request = BrowserNetworkDisableRequest(browser_session_id=session_id)
        response = self._call_sync(self._get_stub.BrowserNetworkDisable, request)

        if not response.success:
            raise RuntimeError(f"NetworkDisable failed: {response.error}")

    def network_get_exchanges(
        self,
        session_id: str,
        url_pattern: str = "",
        methods: list[str] | None = None,
        status_codes: list[int] | None = None,
        resource_types: list[str] | None = None,
        limit: int = 0,
    ) -> dict:
        """Get captured exchanges."""
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserNetworkGetExchangesRequest

        request = BrowserNetworkGetExchangesRequest(
            browser_session_id=session_id,
            url_pattern=url_pattern,
            methods=methods or [],
            status_codes=status_codes or [],
            resource_types=resource_types or [],
            limit=limit,
        )
        response = self._call_sync(self._get_stub.BrowserNetworkGetExchanges, request)

        if not response.success:
            raise RuntimeError(f"NetworkGetExchanges failed: {response.error}")

        return {
            "exchanges": [self._pb_to_exchange(e) for e in response.exchanges],
            "count": response.count,
        }

    def network_get_exchange(self, session_id: str, exchange_id: str) -> dict:
        """Get specific exchange by ID."""
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserNetworkGetExchangeRequest

        request = BrowserNetworkGetExchangeRequest(
            browser_session_id=session_id, exchange_id=exchange_id
        )
        response = self._call_sync(self._get_stub.BrowserNetworkGetExchange, request)

        if not response.success:
            raise RuntimeError(f"NetworkGetExchange failed: {response.error}")

        return {"exchange": self._pb_to_exchange(response.exchange) if response.exchange else None}

    def network_get_last(self, session_id: str, url_pattern: str = "") -> dict:
        """Get most recent exchange matching URL pattern."""
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserNetworkGetLastRequest

        request = BrowserNetworkGetLastRequest(
            browser_session_id=session_id, url_pattern=url_pattern
        )
        response = self._call_sync(self._get_stub.BrowserNetworkGetLast, request)

        if not response.success:
            raise RuntimeError(f"NetworkGetLast failed: {response.error}")

        return {"exchange": self._pb_to_exchange(response.exchange) if response.exchange else None}

    def network_clear(self, session_id: str) -> None:
        """Clear all captured exchanges."""
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserNetworkClearRequest

        request = BrowserNetworkClearRequest(browser_session_id=session_id)
        response = self._call_sync(self._get_stub.BrowserNetworkClear, request)

        if not response.success:
            raise RuntimeError(f"NetworkClear failed: {response.error}")

    def network_stats(self, session_id: str) -> dict:
        """Get capture statistics."""
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserNetworkStatsRequest

        request = BrowserNetworkStatsRequest(browser_session_id=session_id)
        response = self._call_sync(self._get_stub.BrowserNetworkStats, request)

        if not response.success:
            raise RuntimeError(f"NetworkStats failed: {response.error}")

        return {
            "enabled": response.enabled,
            "total_captured": response.total_captured,
            "total_errors": response.total_errors,
            "total_bytes": response.total_bytes,
            "average_duration_ms": response.average_duration_ms,
        }

    def network_export_har(
        self,
        session_id: str,
        url_pattern: str = "",
        methods: list[str] | None = None,
        status_codes: list[int] | None = None,
        resource_types: list[str] | None = None,
    ) -> dict:
        """Export captured exchanges to HAR format."""
        from cmdop._generated.rpc_messages.browser_pb2 import BrowserNetworkExportHARRequest

        request = BrowserNetworkExportHARRequest(
            browser_session_id=session_id,
            url_pattern=url_pattern,
            methods=methods or [],
            status_codes=status_codes or [],
            resource_types=resource_types or [],
        )
        response = self._call_sync(self._get_stub.BrowserNetworkExportHAR, request)

        if not response.success:
            raise RuntimeError(f"NetworkExportHAR failed: {response.error}")

        return {"har_data": response.har_data}

    def _pb_to_exchange(self, pb: Any) -> dict:
        """Convert protobuf exchange to dict."""
        result: dict[str, Any] = {
            "id": pb.id,
            "error": pb.error,
            "frame_id": pb.frame_id,
            "initiator": pb.initiator,
        }

        if pb.request:
            result["request"] = {
                "url": pb.request.url,
                "method": pb.request.method,
                "headers": dict(pb.request.headers),
                "body": pb.request.body,
                "content_type": pb.request.content_type,
                "resource_type": pb.request.resource_type,
            }

        if pb.response:
            result["response"] = {
                "status": pb.response.status,
                "status_text": pb.response.status_text,
                "headers": dict(pb.response.headers),
                "body": pb.response.body,
                "content_type": pb.response.content_type,
                "size": pb.response.size,
                "from_cache": pb.response.from_cache,
            }

        if pb.timing:
            result["timing"] = {
                "started_at_ms": pb.timing.started_at_ms,
                "ended_at_ms": pb.timing.ended_at_ms,
                "duration_ms": pb.timing.duration_ms,
                "wait_time_ms": pb.timing.wait_time_ms,
                "receive_time_ms": pb.timing.receive_time_ms,
            }

        return result
