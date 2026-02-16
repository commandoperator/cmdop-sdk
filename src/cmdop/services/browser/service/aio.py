"""Async browser service stub.

Async browser is not implemented yet. Use sync BrowserService instead.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from cmdop.transport.base import BaseTransport


class AsyncBrowserService:
    """
    Async browser service stub.

    Not implemented yet. Use sync CMDOPClient.browser instead.
    """

    def __init__(self, transport: BaseTransport) -> None:
        self._transport = transport

    def _not_implemented(self) -> NoReturn:
        raise NotImplementedError(
            "Async browser is not implemented. Use sync CMDOPClient.browser instead."
        )

    async def create_session(self, *args, **kwargs) -> NoReturn:
        self._not_implemented()
