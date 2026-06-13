"""schedules namespace: list/get/create/update/delete/trigger/runs.

Fleet-scoped (default-fleet fallback). ``delete`` (not disable). ``runs`` is
cursor-paginated; ``list`` is offset-paginated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cmdop._proto.cmdop.core.v1 import common_pb2 as common_pb
from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop._proto.cmdop.core.v1 import schedules_pb2 as s_pb
from cmdop.resources.base import BaseResource

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Sequence

    from cmdop.types import (
        ManualTriggerResponse,
        ScheduleList,
        ScheduleRunList,
        ScheduleView,
    )

_TARGET = {
    "all_fleet_machines": common_pb.SCHEDULE_TARGET_KIND_ALL_FLEET_MACHINES,
    "specific_machines": common_pb.SCHEDULE_TARGET_KIND_SPECIFIC_MACHINES,
}


class SchedulesResource(BaseResource):
    async def list(
        self, *, fleet_id: str | None = None, page: int = 1, per_page: int | None = None
    ) -> ScheduleList:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            list_schedules_req=s_pb.ListSchedulesRequest(
                fleet_id=fid, page=self._offset_page(page, per_page)
            )
        )
        return (await self._unary(req)).schedule_list

    async def get(self, schedule_id: str, *, fleet_id: str | None = None) -> ScheduleView:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            get_schedule_req=s_pb.GetScheduleRequest(fleet_id=fid, schedule_id=str(schedule_id))
        )
        return (await self._unary(req)).schedule_view

    async def create(
        self,
        *,
        name: str,
        cron_expr: str,
        command: str,
        fleet_id: str | None = None,
        description: str = "",
        timezone: str = "UTC",
        target_kind: str = "all_fleet_machines",
        is_enabled: bool = True,
        machine_ids: Sequence[str] | None = None,
    ) -> ScheduleView:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            create_schedule_req=s_pb.CreateScheduleRequest(
                fleet_id=fid,
                name=name,
                cron_expr=cron_expr,
                command=command,
                description=description,
                timezone=timezone,
                target_kind=_TARGET.get(target_kind, common_pb.SCHEDULE_TARGET_KIND_ALL_FLEET_MACHINES),
                is_enabled=is_enabled,
                machine_ids=[str(x) for x in (machine_ids or [])],
            )
        )
        return (await self._unary(req)).schedule_view

    async def update(
        self,
        schedule_id: str,
        *,
        fleet_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        cron_expr: str | None = None,
        timezone: str | None = None,
        command: str | None = None,
        target_kind: str | None = None,
        is_enabled: bool | None = None,
        machine_ids: Sequence[str] | None = None,
    ) -> ScheduleView:
        fid = self._fleet(fleet_id)
        body = s_pb.UpdateScheduleRequest(fleet_id=fid, schedule_id=str(schedule_id))
        if name is not None:
            body.name = name
        if description is not None:
            body.description = description
        if cron_expr is not None:
            body.cron_expr = cron_expr
        if timezone is not None:
            body.timezone = timezone
        if command is not None:
            body.command = command
        if target_kind is not None:
            body.target_kind = _TARGET.get(
                target_kind, common_pb.SCHEDULE_TARGET_KIND_ALL_FLEET_MACHINES
            )
        if is_enabled is not None:
            body.is_enabled = is_enabled
        if machine_ids is not None:
            body.machine_ids.extend(str(x) for x in machine_ids)
        return (await self._unary(pb.Envelope(update_schedule_req=body))).schedule_view

    async def delete(self, schedule_id: str, *, fleet_id: str | None = None) -> None:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            delete_schedule_req=s_pb.DeleteScheduleRequest(fleet_id=fid, schedule_id=str(schedule_id))
        )
        await self._unary(req)

    async def trigger(self, schedule_id: str, *, fleet_id: str | None = None) -> ManualTriggerResponse:
        """Run now."""
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            trigger_schedule_req=s_pb.TriggerScheduleRequest(
                fleet_id=fid, schedule_id=str(schedule_id)
            )
        )
        return (await self._unary(req)).manual_trigger_resp

    async def runs(
        self,
        schedule_id: str,
        *,
        fleet_id: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> ScheduleRunList:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            schedule_runs_req=s_pb.ScheduleRunsRequest(
                fleet_id=fid, schedule_id=str(schedule_id), limit=limit, cursor=cursor or ""
            )
        )
        return (await self._unary(req)).schedule_run_list

    # -- pagination --------------------------------------------------------

    async def iter(
        self, *, fleet_id: str | None = None, per_page: int | None = None
    ) -> AsyncIterator[Any]:
        async for page in self.pages(fleet_id=fleet_id, per_page=per_page):
            for item in page.items:
                yield item

    async def pages(
        self, *, fleet_id: str | None = None, per_page: int | None = None
    ) -> AsyncIterator[ScheduleList]:
        async def fetch(page_number: int) -> ScheduleList:
            return await self.list(fleet_id=fleet_id, page=page_number, per_page=per_page)

        async for page in self._paginate_offset(fetch):
            yield page

    async def iter_runs(
        self, schedule_id: str, *, fleet_id: str | None = None, limit: int = 50
    ) -> AsyncIterator[Any]:
        async for page in self.pages_runs(schedule_id, fleet_id=fleet_id, limit=limit):
            for item in page.items:
                yield item

    async def pages_runs(
        self, schedule_id: str, *, fleet_id: str | None = None, limit: int = 50
    ) -> AsyncIterator[ScheduleRunList]:
        async def fetch(cursor: str | None) -> ScheduleRunList:
            return await self.runs(schedule_id, fleet_id=fleet_id, limit=limit, cursor=cursor)

        async for page in self._paginate_cursor(fetch):
            yield page
