"""Shared resource plumbing: transport handle, fleet defaulting, pagination.

Every resource method builds a request ``Envelope`` (one oneof arm set,
``kind``/``id`` filled by the transport), calls ``call_unary``/``call_stream``,
and reads the typed response arm back out. The proto message classes are the
message layer; resources are the only place that touches the raw Envelope.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cmdop._proto.cmdop.core.v1 import common_pb2 as common_pb

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable

    from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
    from cmdop._transport import Transport
    from cmdop.client import Client


class BaseResource:
    """Base for every resource wrapper. Owns the shared transport + fleet defaulting."""

    def __init__(self, client: Client) -> None:
        self._client = client
        self._t: Transport = client._t

    # -- fleet defaulting --------------------------------------------------

    def _fleet(self, fleet_id: str | None) -> str:
        fid = fleet_id or self._client.fleet_id
        if not fid:
            raise ValueError(
                "No fleet_id; pass one or set a default on the client (CMDOP_FLEET_ID)."
            )
        return fid

    # -- offset-page helper ------------------------------------------------

    @staticmethod
    def _offset_page(page: int, per_page: int | None) -> common_pb.OffsetPage:
        """Convert a 1-based ``page`` + optional ``per_page`` to the proto
        ``OffsetPage{offset, per_page}`` the core expects."""
        pp = per_page or 0
        offset = (max(page, 1) - 1) * pp if pp else 0
        return common_pb.OffsetPage(offset=offset, per_page=pp)

    # -- call wrappers -----------------------------------------------------

    async def _unary(self, req: pb.Envelope) -> pb.Envelope:
        return await self._t.call_unary(req)

    # -- pagination helpers ------------------------------------------------

    async def _paginate_cursor(
        self,
        fetch_page: Callable[[str | None], Awaitable[Any]],
    ) -> AsyncIterator[Any]:
        """Yield each cursor page; follow ``next_cursor`` until exhausted.

        Works over both ``MachineList`` (next_cursor + has_more) and
        ``ScheduleRunList`` (next_cursor only).
        """
        cursor: str | None = None
        while True:
            page = await fetch_page(cursor)
            yield page
            next_cursor = getattr(page, "next_cursor", "") or None
            if not next_cursor:
                return
            # has_more is only present on MachineList; absent (truthy default) elsewhere.
            has_more_field = page.DESCRIPTOR.fields_by_name.get("has_more")
            if has_more_field is not None and not getattr(page, "has_more", True):
                return
            cursor = next_cursor

    async def _paginate_offset(
        self,
        fetch_page: Callable[[int], Awaitable[Any]],
    ) -> AsyncIterator[Any]:
        """Yield each offset page (1-based) until the offset+items covers total."""
        page_number = 1
        while True:
            page = await fetch_page(page_number)
            yield page
            items = list(getattr(page, "items", []) or [])
            total = getattr(page, "total", None)
            offset = getattr(page, "offset", None) or 0
            per_page = getattr(page, "per_page", None) or len(items) or 1
            if not items:
                return
            if total is not None and offset + len(items) >= total:
                return
            if total is None and len(items) < per_page:
                return
            page_number += 1
