"""Tests for browser JavaScript builders."""

import json

import pytest

from cmdop.services.browser.js import (
    build_async_js,
    build_fetch_js,
    build_fetch_all_js,
    parse_json_result,
)


class TestBuildAsyncJs:
    """Tests for build_async_js function."""

    def test_wraps_code_in_async_iife(self):
        """Test code is wrapped in async IIFE."""
        code = "return 42"
        result = build_async_js(code)

        assert "(async function()" in result
        assert "return 42" in result
        assert "JSON.stringify" in result

    def test_includes_error_handling(self):
        """Test error handling is included."""
        code = "throw new Error('test')"
        result = build_async_js(code)

        assert "try {" in result
        assert "catch(e)" in result
        assert "__error" in result

    def test_handles_await_code(self):
        """Test async code with await."""
        code = "const resp = await fetch('/api'); return resp.json()"
        result = build_async_js(code)

        assert "await fetch" in result


class TestBuildFetchJs:
    """Tests for build_fetch_js function."""

    def test_builds_fetch_call(self):
        """Test fetch call is built correctly."""
        result = build_fetch_js("https://api.example.com/data")

        assert "fetch(" in result
        assert "https://api.example.com/data" in result
        assert "async function" in result

    def test_includes_error_handling(self):
        """Test error handling for non-ok responses."""
        result = build_fetch_js("https://api.example.com")

        assert "resp.ok" in result
        assert "__error" in result

    def test_returns_json(self):
        """Test response is parsed as JSON."""
        result = build_fetch_js("https://api.example.com")

        assert "resp.json()" in result
        assert "JSON.stringify" in result


class TestBuildFetchAllJs:
    """Tests for build_fetch_all_js function."""

    def test_builds_parallel_fetch(self):
        """Test parallel fetch is built correctly."""
        urls = {"a": "https://a.com", "b": "https://b.com"}
        result = build_fetch_all_js(urls)

        assert "https://a.com" in result
        assert "https://b.com" in result
        assert "Promise.all" in result

    def test_with_headers(self):
        """Test headers are included."""
        urls = {"a": "https://a.com"}
        headers = {"Accept": "application/json", "X-Custom": "value"}
        result = build_fetch_all_js(urls, headers=headers)

        assert "application/json" in result
        assert "X-Custom" in result

    def test_with_credentials(self):
        """Test credentials option."""
        urls = {"a": "https://a.com"}

        # Without credentials
        result_no_creds = build_fetch_all_js(urls, credentials=False)
        assert "'same-origin'" in result_no_creds

        # With credentials
        result_with_creds = build_fetch_all_js(urls, credentials=True)
        assert "'include'" in result_with_creds

    def test_result_structure(self):
        """Test result structure with data and error."""
        urls = {"id1": "https://example.com"}
        result = build_fetch_all_js(urls)

        assert "data:" in result
        assert "error:" in result
        assert "results[id]" in result

    def test_handles_http_errors(self):
        """Test HTTP error handling."""
        urls = {"a": "https://a.com"}
        result = build_fetch_all_js(urls)

        assert "resp.ok" in result
        assert "HTTP ${resp.status}" in result

    def test_handles_exceptions(self):
        """Test exception handling."""
        urls = {"a": "https://a.com"}
        result = build_fetch_all_js(urls)

        assert "catch (e)" in result
        assert "e.message" in result

    def test_empty_urls(self):
        """Test empty urls dict."""
        result = build_fetch_all_js({})
        # Should still generate valid JS
        assert "const urls" in result

    def test_special_characters_in_url(self):
        """Test URLs with special characters."""
        urls = {"a": "https://api.com/search?q=test&limit=10"}
        result = build_fetch_all_js(urls)

        assert "q=test" in result
        assert "limit=10" in result


class TestParseJsonResult:
    """Tests for parse_json_result function."""

    def test_parses_dict(self):
        """Test parsing dict result."""
        result = parse_json_result('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parses_list(self):
        """Test parsing list result."""
        result = parse_json_result('[1, 2, 3]')
        assert result == [1, 2, 3]

    def test_parses_nested(self):
        """Test parsing nested structure."""
        data = {"items": [{"id": 1}, {"id": 2}], "total": 2}
        result = parse_json_result(json.dumps(data))
        assert result == data

    def test_returns_none_on_error(self):
        """Test __error results return None."""
        result = parse_json_result('{"__error": "Something failed"}')
        assert result is None

    def test_returns_none_on_empty(self):
        """Test empty string returns None."""
        assert parse_json_result("") is None
        assert parse_json_result(None) is None

    def test_returns_none_on_invalid_json(self):
        """Test invalid JSON returns None."""
        assert parse_json_result("not json") is None
        assert parse_json_result("{broken") is None

    def test_preserves_types(self):
        """Test various JSON types are preserved."""
        assert parse_json_result("42") == 42
        assert parse_json_result("true") is True
        assert parse_json_result('"string"') == "string"
        assert parse_json_result("null") is None
