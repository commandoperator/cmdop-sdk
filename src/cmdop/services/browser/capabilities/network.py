"""Network capture capability (v2.19.0)."""

from __future__ import annotations
from typing import Any

from cmdop.services.browser.models import (
    NetworkExchange,
    NetworkRequest,
    NetworkResponse,
    NetworkTiming,
    NetworkStats,
    NetworkFilter,
)

from ._base import BaseCapability


class NetworkCapability(BaseCapability):
    """Network capture operations.

    Captures HTTP requests/responses made by the browser.
    Useful for:
    - Intercepting API responses
    - Debugging network issues
    - Extracting data from XHR/Fetch calls

    Usage:
        # Enable capture
        session.network.enable()

        # Navigate and trigger requests
        session.navigate("https://example.com")

        # Get all captured exchanges
        exchanges = session.network.get_all()

        # Get last API response
        api = session.network.last("/api/data")
        data = api.json_body()

        # Filter by criteria
        xhr = session.network.filter(
            url_pattern="/api/",
            methods=["POST"],
            status_codes=[200],
        )

        # Disable capture
        session.network.disable()
    """

    def enable(self, max_exchanges: int = 1000, max_response_size: int = 10_000_000) -> None:
        """Enable network capture.

        Args:
            max_exchanges: Max exchanges to keep in memory (FIFO eviction)
            max_response_size: Max response body size in bytes
        """
        self._call("network_enable", max_exchanges, max_response_size)

    def disable(self) -> None:
        """Disable network capture."""
        self._call("network_disable")

    def get_all(self, limit: int = 0) -> list[NetworkExchange]:
        """Get all captured exchanges.

        Args:
            limit: Max results (0 = unlimited)
        """
        return self.filter(limit=limit)

    def filter(
        self,
        url_pattern: str = "",
        methods: list[str] | None = None,
        status_codes: list[int] | None = None,
        resource_types: list[str] | None = None,
        limit: int = 0,
    ) -> list[NetworkExchange]:
        """Get exchanges matching filter criteria.

        Args:
            url_pattern: Regex pattern for URL matching
            methods: HTTP methods (GET, POST, etc.)
            status_codes: HTTP status codes (200, 404, etc.)
            resource_types: xhr, fetch, document, script, image, etc.
            limit: Max results (0 = unlimited)
        """
        data = self._call(
            "network_get_exchanges",
            url_pattern,
            methods or [],
            status_codes or [],
            resource_types or [],
            limit,
        )
        return [self._parse_exchange(e) for e in data.get("exchanges", [])]

    def get(self, exchange_id: str) -> NetworkExchange | None:
        """Get specific exchange by ID."""
        data = self._call("network_get_exchange", exchange_id)
        exchange = data.get("exchange")
        if exchange:
            return self._parse_exchange(exchange)
        return None

    def last(self, url_pattern: str = "") -> NetworkExchange | None:
        """Get most recent exchange matching URL pattern.

        Args:
            url_pattern: Regex pattern for URL (empty = any)
        """
        data = self._call("network_get_last", url_pattern)
        exchange = data.get("exchange")
        if exchange:
            return self._parse_exchange(exchange)
        return None

    def clear(self) -> None:
        """Clear all captured exchanges."""
        self._call("network_clear")

    def stats(self) -> NetworkStats:
        """Get capture statistics."""
        data = self._call("network_stats")
        return NetworkStats(
            enabled=data.get("enabled", False),
            total_captured=data.get("total_captured", 0),
            total_errors=data.get("total_errors", 0),
            total_bytes=data.get("total_bytes", 0),
            average_duration_ms=data.get("average_duration_ms", 0),
        )

    def export_har(
        self,
        url_pattern: str = "",
        methods: list[str] | None = None,
        status_codes: list[int] | None = None,
        resource_types: list[str] | None = None,
    ) -> bytes:
        """Export captured exchanges to HAR format.

        Args:
            url_pattern: Regex pattern for URL matching
            methods: HTTP methods filter
            status_codes: HTTP status codes filter
            resource_types: Resource types filter

        Returns:
            HAR JSON as bytes
        """
        data = self._call(
            "network_export_har",
            url_pattern,
            methods or [],
            status_codes or [],
            resource_types or [],
        )
        return data.get("har_data", b"")

    # === Convenience Methods ===

    def api_calls(self, url_pattern: str = "/api/") -> list[NetworkExchange]:
        """Get XHR/Fetch API calls matching pattern."""
        return self.filter(
            url_pattern=url_pattern,
            resource_types=["xhr", "fetch"],
        )

    def last_json(self, url_pattern: str = "") -> Any:
        """Get JSON body from most recent matching response."""
        exchange = self.last(url_pattern)
        if exchange:
            return exchange.json_body()
        return None

    def wait_for(self, url_pattern: str, timeout_ms: int = 30000) -> NetworkExchange | None:
        """Wait for a matching request to be captured.

        Args:
            url_pattern: Regex pattern for URL
            timeout_ms: Timeout in milliseconds

        Returns:
            Matching exchange or None if timeout
        """
        import time
        start = time.time()
        timeout_sec = timeout_ms / 1000

        while time.time() - start < timeout_sec:
            exchange = self.last(url_pattern)
            if exchange:
                return exchange
            time.sleep(0.1)

        return None

    # === Internal ===

    def _parse_exchange(self, data: dict[str, Any]) -> NetworkExchange:
        """Parse exchange from dict."""
        request_data = data.get("request", {})
        response_data = data.get("response")
        timing_data = data.get("timing", {})

        request = NetworkRequest(
            url=request_data.get("url", ""),
            method=request_data.get("method", "GET"),
            headers=request_data.get("headers", {}),
            body=request_data.get("body", b""),
            content_type=request_data.get("content_type", ""),
            resource_type=request_data.get("resource_type", ""),
        )

        response = None
        if response_data:
            response = NetworkResponse(
                status=response_data.get("status", 0),
                status_text=response_data.get("status_text", ""),
                headers=response_data.get("headers", {}),
                body=response_data.get("body", b""),
                content_type=response_data.get("content_type", ""),
                size=response_data.get("size", 0),
                from_cache=response_data.get("from_cache", False),
            )

        timing = NetworkTiming(
            started_at_ms=timing_data.get("started_at_ms", 0),
            ended_at_ms=timing_data.get("ended_at_ms", 0),
            duration_ms=timing_data.get("duration_ms", 0),
            wait_time_ms=timing_data.get("wait_time_ms", 0),
            receive_time_ms=timing_data.get("receive_time_ms", 0),
        )

        return NetworkExchange(
            id=data.get("id", ""),
            request=request,
            response=response,
            timing=timing,
            error=data.get("error", ""),
            frame_id=data.get("frame_id", ""),
            initiator=data.get("initiator", ""),
        )
