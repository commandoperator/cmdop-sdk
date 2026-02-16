"""Fetch capability."""

from typing import Any

from cmdop.services.browser.js import (
    build_fetch_js,
    build_fetch_all_js,
    build_async_js,
    parse_json_result,
)

from ._base import BaseCapability


class FetchCapability(BaseCapability):
    """HTTP fetch operations from browser context.

    Usage:
        data = session.fetch.json("/api/data")
        results = session.fetch.all({"a": "/api/a", "b": "/api/b"})
    """

    def json(self, url: str) -> dict | list | None:
        """Fetch JSON from URL."""
        js = build_fetch_js(url)
        return parse_json_result(self._js(js))

    def all(
        self,
        urls: dict[str, str],
        headers: dict[str, str] | None = None,
        credentials: bool = False,
    ) -> dict[str, Any]:
        """Fetch multiple URLs in parallel. Returns {id: {data, error}}."""
        if not urls:
            return {}
        js = build_fetch_all_js(urls, headers, credentials)
        wrapped = build_async_js(js)
        result = parse_json_result(self._js(wrapped))
        return result if isinstance(result, dict) else {}

    def execute(self, code: str) -> dict | list | str | None:
        """Execute async JS code (can use await, fetch, etc)."""
        js = build_async_js(code)
        return parse_json_result(self._js(js))
