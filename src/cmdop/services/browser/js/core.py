"""Core JavaScript utilities for browser automation."""

from __future__ import annotations

import json
from typing import Any


def parse_json_result(result: str) -> dict | list | None:
    """Parse JSON result from JS execution."""
    if result:
        try:
            data = json.loads(result)
            if isinstance(data, dict) and "__error" in data:
                return None
            return data
        except json.JSONDecodeError:
            return None
    return None


def build_async_js(code: str) -> str:
    """
    Wrap JS code in async IIFE with error handling.

    The code should return a value (will be JSON.stringify'd).
    Use for async operations like fetch, Promise.all, etc.
    """
    return f"""
    (async function() {{
        try {{
            const result = await (async () => {{ {code} }})();
            return JSON.stringify(result);
        }} catch(e) {{
            return JSON.stringify({{__error: e.message}});
        }}
    }})()
    """
