"""The current machine roster, agent stream, and durable messages."""

from __future__ import annotations

from collections.abc import Iterable

from cmdop._proto.cmdop.core.v2 import contract_pb2 as pb
from cmdop.resources.base import BaseResource
from cmdop.streaming import AskStream


class MachinesResource(BaseResource):
    async def list(self) -> pb.MachineRosterSnapshot:
        response = await self._unary(pb.Envelope(list_machines_req=pb.ListMachinesRequest()))
        return response.machine_roster_snapshot

    def ask(
        self,
        machine_id: str,
        prompt: str = "",
        *,
        pin: str | None = None,
        session: str | None = None,
        attachment_ids: Iterable[str] = (),
        engine: str | None = None,
        working_dir: str | None = None,
        project_root_id: str | None = None,
        model: str | None = None,
    ) -> AskStream:
        attachments = list(attachment_ids)
        if not prompt and not attachments:
            raise ValueError("prompt or at least one attachment_id is required")
        options = pb.AskOptions(attachment_ids=attachments)
        for name, value in (
            ("pin", pin),
            ("session", session),
            ("engine", engine),
            ("working_dir", working_dir),
            ("project_root_id", project_root_id),
            ("model", model),
        ):
            if value is not None:
                setattr(options, name, value)
        return self._t.call_stream(
            pb.Envelope(
                ask_machine_req=pb.AskMachineRequest(
                    machine_id=str(machine_id), prompt=prompt, options=options
                )
            )
        )

    async def messages(
        self,
        machine_id: str,
        *,
        session: str | None = None,
        limit: int | None = None,
    ) -> pb.MachineMessageList:
        if limit is not None and not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        request = pb.ListMachineMessagesRequest(machine_id=str(machine_id))
        if session is not None:
            request.session = session
        if limit is not None:
            request.limit = limit
        response = await self._unary(pb.Envelope(list_machine_messages_req=request))
        return response.machine_message_list
