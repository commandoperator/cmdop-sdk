"""machines namespace: list/get/update/disable/info/spend + ask (stream) +
messages/clear_messages/active_session.

Each method builds the request Envelope arm, calls the transport, and returns
the typed proto response arm. ``ask`` returns a :class:`FrameStream`.
``disable`` is soft-disable (not delete), ``spend`` takes a ``window``.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop._proto.cmdop.core.v1 import machines_pb2 as m_pb
from cmdop.resources.base import BaseResource
from cmdop.streaming import FrameStream

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from cmdop.types import (
        ClearMessagesResponse,
        MachineDetail,
        MachineInfoResponse,
        MachineList,
        MachineSummary,
        MessagesResponse,
    )


class MachinesResource(BaseResource):
    # -- unary -------------------------------------------------------------

    async def list(
        self,
        *,
        presence: str = "any",
        q: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> MachineList:
        req = pb.Envelope(
            list_machines_req=m_pb.ListMachinesRequest(
                presence=presence, q=q or "", limit=limit, cursor=cursor or ""
            )
        )
        return (await self._unary(req)).machine_list

    async def get(self, machine_id: str) -> MachineDetail:
        req = pb.Envelope(get_machine_req=m_pb.GetMachineRequest(machine_id=str(machine_id)))
        return (await self._unary(req)).machine_detail

    async def update(self, machine_id: str, name: str | None = None) -> MachineSummary:
        req = pb.Envelope(
            update_machine_req=m_pb.UpdateMachineRequest(
                machine_id=str(machine_id), name=name or ""
            )
        )
        return (await self._unary(req)).machine_summary

    async def disable(self, machine_id: str) -> None:
        """Soft-disable (not delete)."""
        req = pb.Envelope(disable_machine_req=m_pb.DisableMachineRequest(machine_id=str(machine_id)))
        await self._unary(req)

    async def info(self, machine_id: str) -> MachineInfoResponse:
        """The /info read model (identity / hardware / live_state / session /
        presence / fingerprint) — distinct from get()'s MachineDetail."""
        req = pb.Envelope(machine_info_req=m_pb.MachineInfoRequest(machine_id=str(machine_id)))
        return (await self._unary(req)).machine_info_resp

    async def spend(self, machine_id: str, *, window: str = "7d") -> m_pb.MachineSpend:
        req = pb.Envelope(
            machine_spend_req=m_pb.MachineSpendRequest(machine_id=str(machine_id), window=window)
        )
        return (await self._unary(req)).machine_spend

    # -- pagination --------------------------------------------------------

    async def iter(
        self, *, presence: str = "any", q: str | None = None, limit: int = 100
    ) -> AsyncIterator[Any]:
        """Yield every machine, transparently following ``next_cursor``."""
        async for page in self.pages(presence=presence, q=q, limit=limit):
            for item in page.items:
                yield item

    async def pages(
        self, *, presence: str = "any", q: str | None = None, limit: int = 100
    ) -> AsyncIterator[MachineList]:
        """Yield machine pages (cursor pagination)."""

        async def fetch(cursor: str | None) -> MachineList:
            return await self.list(presence=presence, q=q, limit=limit, cursor=cursor)

        async for page in self._paginate_cursor(fetch):
            yield page

    # -- stream ------------------------------------------------------------

    def ask(
        self,
        machine_id: str,
        prompt: str,
        *,
        session_id: str | None = None,
        agent_type: str | None = None,
        timeout_seconds: int | None = None,
        options: dict[str, str] | None = None,
        pin: str | None = None,
    ) -> FrameStream:
        """Talk to the machine's AI agent. Returns a :class:`FrameStream` with
        ``pin()`` / ``confirm()`` / ``collect()``.

        ``pin`` is the upfront connection PIN for a PIN-gated target: the relay
        forwards it once to the machine for local verification (zero-knowledge —
        never stored/hashed). Omit for machines that require no PIN."""
        req = m_pb.AskRequest(
            machine_id=str(machine_id),
            session_id=session_id or uuid.uuid4().hex,
            prompt=prompt,
            options=options or {},
        )
        if agent_type is not None:
            req.agent_type = agent_type
        if timeout_seconds is not None:
            req.timeout_seconds = timeout_seconds
        if pin is not None:
            req.pin = pin
        return self._t.call_stream(pb.Envelope(ask_req=req))

    # -- chat history ------------------------------------------------------

    async def messages(self, machine_id: str, *, limit: int = 50) -> MessagesResponse:
        """Recent chat history for the machine."""
        req = pb.Envelope(messages_req=m_pb.MessagesRequest(machine_id=str(machine_id), limit=limit))
        return (await self._unary(req)).messages_resp

    async def clear_messages(self, machine_id: str) -> ClearMessagesResponse:
        """Wipe chat history for the machine."""
        req = pb.Envelope(clear_messages_req=m_pb.ClearMessagesRequest(machine_id=str(machine_id)))
        return (await self._unary(req)).clear_messages_resp

    async def active_session(self, machine_id: str) -> str:
        """Return the live agent session id (empty if none)."""
        req = pb.Envelope(active_session_req=m_pb.ActiveSessionRequest(machine_id=str(machine_id)))
        return (await self._unary(req)).active_session_resp.agent_session_id
