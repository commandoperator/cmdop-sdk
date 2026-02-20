"""
Machines service for CMDOP API.

Provides high-level interface for machine management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cmdop.api.generated.machines import API as MachinesAPI
    from cmdop.api.generated.machines.machines__api__machines.models import (
        Machine,
        MachineCreate,
        MachineCreateRequest,
        PaginatedMachineList,
        PaginatedMachineLogList,
    )
    from cmdop.api.generated.machines.enums import MachineOs, MachineStatus


class MachinesService:
    """
    High-level machines service.

    Wraps the generated machines API with convenient methods.

    Example:
        >>> async with CMDOPAPI(api_key="cmd_xxx") as api:
        ...     machines = await api.machines.list()
        ...     machine = await api.machines.get(123)
    """

    def __init__(self, api: MachinesAPI) -> None:
        """
        Initialize machines service.

        Args:
            api: Generated machines API client
        """
        self._api = api
        self._client = api.machines_machines

    async def list(
        self,
        status: MachineStatus | str | None = None,
        os: MachineOs | str | None = None,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
    ) -> PaginatedMachineList:
        """
        List machines with optional filtering.

        Args:
            status: Filter by status ("online", "offline")
            os: Filter by OS ("macos", "linux", "windows")
            search: Search query
            page: Page number
            page_size: Items per page
            ordering: Sort field (e.g., "-created_at")

        Returns:
            Paginated list of machines
        """
        return await self._client.machines_list(
            search=search,
            page=page,
            page_size=page_size,
            ordering=ordering,
        )

    async def get(self, machine_id: int | str) -> Machine:
        """
        Get machine by ID.

        Args:
            machine_id: Machine ID

        Returns:
            Machine details
        """
        return await self._client.machines_retrieve(id=str(machine_id))

    async def create(
        self,
        name: str,
        hostname: str | None = None,
        os: MachineOs | str | None = None,
        **kwargs,
    ) -> MachineCreate:
        """
        Create a new machine.

        Args:
            name: Machine name
            hostname: Machine hostname
            os: Operating system
            **kwargs: Additional fields

        Returns:
            Created machine with agent token
        """
        from cmdop.api.generated.machines.machines__api__machines.models import (
            MachineCreateRequest,
        )

        data = MachineCreateRequest(
            name=name,
            hostname=hostname or name,
            os=os,
            **kwargs,
        )
        return await self._client.machines_create(data=data)

    async def update(
        self,
        machine_id: int | str,
        name: str | None = None,
        **kwargs,
    ) -> Machine:
        """
        Update machine.

        Args:
            machine_id: Machine ID
            name: New name
            **kwargs: Additional fields to update

        Returns:
            Updated machine
        """
        from cmdop.api.generated.machines.machines__api__machines.models import (
            PatchedMachineRequest,
        )

        data = PatchedMachineRequest(name=name, **kwargs)
        return await self._client.machines_partial_update(
            id=str(machine_id),
            data=data,
        )

    async def delete(self, machine_id: int | str) -> None:
        """
        Delete machine.

        Args:
            machine_id: Machine ID
        """
        await self._client.machines_destroy(id=str(machine_id))

    async def get_logs(
        self,
        machine_id: int | str,
        level: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> PaginatedMachineLogList:
        """
        Get machine logs.

        Args:
            machine_id: Machine ID
            level: Filter by log level ("info", "warning", "error")
            limit: Max logs to return
            page: Page number
            page_size: Items per page

        Returns:
            Paginated list of logs
        """
        return await self._client.machines_logs_list(
            id=str(machine_id),
            level=level,
            limit=limit,
            page=page,
            page_size=page_size,
        )

    async def regenerate_token(self, machine_id: int | str) -> None:
        """
        Regenerate agent token for machine.

        Args:
            machine_id: Machine ID
        """
        from cmdop.api.generated.machines.machines__api__machines.models import (
            MachineRequest,
        )

        await self._client.machines_regenerate_token_create(
            id=str(machine_id),
            data=MachineRequest(),
        )

    async def get_stats(self, machine_id: int | str) -> None:
        """
        Get machine statistics.

        Args:
            machine_id: Machine ID
        """
        return await self._client.machines_stats_retrieve(id=str(machine_id))
