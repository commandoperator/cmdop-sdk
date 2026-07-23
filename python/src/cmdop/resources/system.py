"""Public, credential-free relay discovery."""

from __future__ import annotations

from cmdop._proto.cmdop.core.v2 import contract_pb2 as pb
from cmdop.resources.base import BaseResource


class SystemResource(BaseResource):
    async def bootstrap(self) -> pb.SystemBootstrapResponse:
        response = await self._unary(
            pb.Envelope(system_bootstrap_req=pb.SystemBootstrapRequest())
        )
        return response.system_bootstrap_resp
