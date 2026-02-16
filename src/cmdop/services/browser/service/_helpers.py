"""Base service mixin with shared utilities."""

from __future__ import annotations

from typing import Any

from cmdop.services.browser.models import BrowserCookie


def cookie_to_pb(c: BrowserCookie | dict, PbCookie: type) -> Any:
    """Convert cookie to protobuf."""
    if isinstance(c, dict):
        return PbCookie(
            name=c.get("name", ""),
            value=c.get("value", ""),
            domain=c.get("domain", ""),
            path=c.get("path", "/"),
            secure=c.get("secure", False),
            http_only=c.get("http_only", False),
            same_site=c.get("same_site", ""),
            expires=c.get("expires", 0),
        )
    return PbCookie(
        name=c.name,
        value=c.value,
        domain=c.domain,
        path=c.path,
        secure=c.secure,
        http_only=c.http_only,
        same_site=c.same_site,
        expires=c.expires,
    )


def pb_to_cookie(c: Any) -> BrowserCookie:
    """Convert protobuf to cookie."""
    return BrowserCookie(
        name=c.name,
        value=c.value,
        domain=c.domain,
        path=c.path,
        secure=c.secure,
        http_only=c.http_only,
        same_site=c.same_site,
        expires=c.expires,
    )


class BaseServiceMixin:
    """
    Mixin with shared service utilities.

    Used by both BrowserService and AsyncBrowserService.
    """

    @staticmethod
    def _cookie_to_pb(c: BrowserCookie | dict, PbCookie: type) -> Any:
        return cookie_to_pb(c, PbCookie)

    @staticmethod
    def _pb_to_cookie(c: Any) -> BrowserCookie:
        return pb_to_cookie(c)
