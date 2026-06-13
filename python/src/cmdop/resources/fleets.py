"""fleets namespace + fleets.members + fleets.machines sub-resources.

``get`` scans ``list`` client-side (no dedicated op); ``disable`` is soft-disable.
``members`` / ``machines`` are fleet-scoped (default-fleet fallback).
"""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from cmdop._proto.cmdop.core.v1 import common_pb2 as common_pb
from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop._proto.cmdop.core.v1 import fleets_pb2 as f_pb
from cmdop.resources.base import BaseResource

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from cmdop.types import (
        FleetList,
        FleetSummary,
        MachineFleetLink,
        MachineList,
        MemberInfo,
        MemberList,
    )

_MFA = {
    "none": common_pb.MFA_REQUIREMENT_NONE,
    "optional": common_pb.MFA_REQUIREMENT_OPTIONAL,
    "required": common_pb.MFA_REQUIREMENT_REQUIRED,
}


class FleetsResource(BaseResource):
    @cached_property
    def members(self) -> FleetMembersResource:
        return FleetMembersResource(self._client)

    @cached_property
    def machines(self) -> FleetMachinesResource:
        return FleetMachinesResource(self._client)

    async def list(self, *, page: int = 1, per_page: int | None = None) -> FleetList:
        req = pb.Envelope(
            list_fleets_req=f_pb.ListFleetsRequest(page=self._offset_page(page, per_page))
        )
        return (await self._unary(req)).fleet_list

    async def get(self, fleet_id: str) -> FleetSummary:
        """Find a fleet by id within the (offset-paginated) list."""
        async for fleet in self.iter():
            if str(fleet.id) == str(fleet_id):
                return fleet
        from cmdop.errors import NotFoundError

        raise NotFoundError(f"Fleet {fleet_id} not found", code="not_found")

    async def create(self, *, name: str, slug: str, mfa_required: str = "none") -> FleetSummary:
        req = pb.Envelope(
            create_fleet_req=f_pb.CreateFleetRequest(
                name=name, slug=slug, mfa_required=_MFA.get(mfa_required, common_pb.MFA_REQUIREMENT_NONE)
            )
        )
        return (await self._unary(req)).fleet_summary

    async def update(
        self, fleet_id: str, *, name: str | None = None, mfa_required: str | None = None
    ) -> FleetSummary:
        body = f_pb.UpdateFleetRequest(fleet_id=str(fleet_id), name=name or "")
        if mfa_required is not None:
            body.mfa_required = _MFA.get(mfa_required, common_pb.MFA_REQUIREMENT_NONE)
        return (await self._unary(pb.Envelope(update_fleet_req=body))).fleet_summary

    async def disable(self, fleet_id: str) -> None:
        """Soft-disable (not delete)."""
        req = pb.Envelope(disable_fleet_req=f_pb.DisableFleetRequest(fleet_id=str(fleet_id)))
        await self._unary(req)

    # -- pagination --------------------------------------------------------

    async def iter(self, *, per_page: int | None = None) -> AsyncIterator[Any]:
        async for page in self.pages(per_page=per_page):
            for item in page.items:
                yield item

    async def pages(self, *, per_page: int | None = None) -> AsyncIterator[FleetList]:
        async def fetch(page_number: int) -> FleetList:
            return await self.list(page=page_number, per_page=per_page)

        async for page in self._paginate_offset(fetch):
            yield page


class FleetMembersResource(BaseResource):
    async def list(
        self, fleet_id: str | None = None, *, page: int = 1, per_page: int | None = None
    ) -> MemberList:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            list_members_req=f_pb.ListMembersRequest(
                fleet_id=fid, page=self._offset_page(page, per_page)
            )
        )
        return (await self._unary(req)).member_list

    async def add(self, email: str, role: str = "member", *, fleet_id: str | None = None) -> MemberInfo:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(add_member_req=f_pb.AddMemberRequest(fleet_id=fid, email=email, role=role))
        return (await self._unary(req)).member_info

    async def set_role(self, user_id: str, role: str, *, fleet_id: str | None = None) -> MemberInfo:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            set_member_role_req=f_pb.SetMemberRoleRequest(
                fleet_id=fid, user_id=str(user_id), role=role
            )
        )
        return (await self._unary(req)).member_info

    async def remove(self, user_id: str, *, fleet_id: str | None = None) -> None:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            remove_member_req=f_pb.RemoveMemberRequest(fleet_id=fid, user_id=str(user_id))
        )
        await self._unary(req)


class FleetMachinesResource(BaseResource):
    async def list(
        self,
        fleet_id: str | None = None,
        *,
        presence: str = "any",
        q: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> MachineList:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            list_fleet_machines_req=f_pb.ListFleetMachinesRequest(
                fleet_id=fid, presence=presence, q=q or "", limit=limit, cursor=cursor or ""
            )
        )
        return (await self._unary(req)).machine_list

    async def attach(self, machine_id: str, *, fleet_id: str | None = None) -> MachineFleetLink:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            attach_machine_req=f_pb.AttachMachineRequest(fleet_id=fid, machine_id=str(machine_id))
        )
        return (await self._unary(req)).machine_fleet_link

    async def detach(self, machine_id: str, *, fleet_id: str | None = None) -> None:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            detach_machine_req=f_pb.DetachMachineRequest(fleet_id=fid, machine_id=str(machine_id))
        )
        await self._unary(req)
