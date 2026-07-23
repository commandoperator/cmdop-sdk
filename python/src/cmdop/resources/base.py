from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cmdop._proto.cmdop.core.v2 import contract_pb2 as pb
    from cmdop._transport import Transport
    from cmdop.client import Client


class BaseResource:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._t: Transport = client._t

    async def _unary(self, request: pb.Envelope) -> pb.Envelope:
        return await self._t.call_unary(request)
