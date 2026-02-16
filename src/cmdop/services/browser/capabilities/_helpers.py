"""Shared parsing helpers for capabilities."""

from typing import Any
from cmdop.services.browser.js import parse_json_result


def to_dict(raw: str) -> dict[str, Any]:
    """Parse JS result to dict, default empty."""
    result = parse_json_result(raw)
    return result if isinstance(result, dict) else {}


def to_list(raw: str) -> list[Any]:
    """Parse JS result to list, default empty."""
    result = parse_json_result(raw)
    return result if isinstance(result, list) else []
