"""tunnels namespace: open/close/list/get/sessions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop._proto.cmdop.core.v1 import tunnels_pb2 as t_pb
from cmdop.resources.base import BaseResource

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Sequence

    from cmdop.types import ConnectedSessionOption, TunnelList, TunnelView


class TunnelsResource(BaseResource):
    async def open(
        self,
        session_id: str,
        *,
        local_port: int,
        protocol: str = "http",
        local_host: str = "127.0.0.1",
        subdomain: str | None = None,
        options: dict[str, str] | None = None,
    ) -> TunnelView:
        req = pb.Envelope(
            open_tunnel_req=t_pb.OpenTunnelRequest(
                session_id=session_id,
                protocol=protocol,
                local_host=local_host,
                local_port=local_port,
                subdomain=subdomain or "",
                options=options or {},
            )
        )
        return (await self._unary(req)).tunnel_view

    async def close(self, tunnel_id: str) -> None:
        """Close a tunnel (idempotent)."""
        req = pb.Envelope(close_tunnel_req=t_pb.CloseTunnelRequest(tunnel_id=str(tunnel_id)))
        await self._unary(req)

    async def list(self, *, page: int = 1, per_page: int | None = None) -> TunnelList:
        req = pb.Envelope(
            list_tunnels_req=t_pb.ListTunnelsRequest(page=self._offset_page(page, per_page))
        )
        return (await self._unary(req)).tunnel_list

    async def get(self, tunnel_id: str) -> TunnelView:
        req = pb.Envelope(get_tunnel_req=t_pb.GetTunnelRequest(tunnel_id=str(tunnel_id)))
        return (await self._unary(req)).tunnel_view

    async def sessions(self) -> Sequence[ConnectedSessionOption]:
        """Connected-session picker for opening tunnels."""
        req = pb.Envelope(list_sessions_req=t_pb.ListSessionsRequest())
        return list((await self._unary(req)).session_list.items)

    # -- pagination --------------------------------------------------------

    async def iter(self, *, per_page: int | None = None) -> AsyncIterator[Any]:
        async for page in self.pages(per_page=per_page):
            for item in page.items:
                yield item

    async def pages(self, *, per_page: int | None = None) -> AsyncIterator[TunnelList]:
        async def fetch(page_number: int) -> TunnelList:
            return await self.list(page=page_number, per_page=per_page)

        async for page in self._paginate_offset(fetch):
            yield page
