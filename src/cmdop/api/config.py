"""
CMDOP API configuration.

Provides URL configuration for dev/prod environments.
"""

from __future__ import annotations

from typing import Literal

# Base URLs for different environments
BASE_URLS = {
    "prod": "https://api.cmdop.com",
    "dev": "https://dev.cmdop.com",
    "local": "http://localhost:8000",
}


def get_base_url(mode: Literal["prod", "dev", "local"] = "prod") -> str:
    """
    Get base URL for the specified environment.

    Args:
        mode: Environment mode - "prod", "dev", or "local"

    Returns:
        Base URL for the API

    Example:
        >>> get_base_url("prod")
        'https://api.cmdop.com'
        >>> get_base_url("dev")
        'https://dev.cmdop.com'
    """
    return BASE_URLS.get(mode, BASE_URLS["prod"])


__all__ = ["get_base_url", "BASE_URLS"]
