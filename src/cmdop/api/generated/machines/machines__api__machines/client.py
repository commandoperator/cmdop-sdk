from __future__ import annotations

import httpx

from .models import *


class MachinesMachinesAPI:
    """API endpoints for Machines."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def logs_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedMachineLogList]:
        """
        ViewSet for MachineLog operations. Read-only except for creation. Logs
        are created by agents.
        """
        url = "/api/machines/logs/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return PaginatedMachineLogList.model_validate(response.json())


    async def logs_create(self, data: MachineLogRequest) -> MachineLog:
        """
        ViewSet for MachineLog operations. Read-only except for creation. Logs
        are created by agents.
        """
        url = "/api/machines/logs/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return MachineLog.model_validate(response.json())


    async def logs_retrieve(self, id: str) -> MachineLog:
        """
        ViewSet for MachineLog operations. Read-only except for creation. Logs
        are created by agents.
        """
        url = f"/api/machines/logs/{id}/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return MachineLog.model_validate(response.json())


    async def machines_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedMachineList]:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = "/api/machines/machines/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return PaginatedMachineList.model_validate(response.json())


    async def machines_create(self, data: MachineCreateRequest) -> MachineCreate:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = "/api/machines/machines/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return MachineCreate.model_validate(response.json())


    async def machines_retrieve(self, id: str) -> Machine:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = f"/api/machines/machines/{id}/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return Machine.model_validate(response.json())


    async def machines_update(self, id: str, data: MachineRequest) -> Machine:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = f"/api/machines/machines/{id}/"
        response = await self._client.put(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return Machine.model_validate(response.json())


    async def machines_partial_update(self, id: str, data: PatchedMachineRequest | None = None) -> Machine:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = f"/api/machines/machines/{id}/"
        response = await self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return Machine.model_validate(response.json())


    async def machines_destroy(self, id: str) -> None:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = f"/api/machines/machines/{id}/"
        response = await self._client.delete(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


    async def machines_logs_list(self, id: str, level: str | None = None, limit: int | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedMachineLogList]:
        """
        Get machine logs

        Get logs for this machine.
        """
        url = f"/api/machines/machines/{id}/logs/"
        response = await self._client.get(url, params={"level": level if level is not None else None, "limit": limit if limit is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return PaginatedMachineLogList.model_validate(response.json())


    async def machines_regenerate_token_create(self, id: str, data: MachineRequest) -> None:
        """
        Regenerate agent token

        Regenerate machine agent token.
        """
        url = f"/api/machines/machines/{id}/regenerate-token/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


    async def machines_stats_retrieve(self, id: str) -> None:
        """
        Get machine statistics

        Get machine statistics.
        """
        url = f"/api/machines/machines/{id}/stats/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


    async def machines_update_metrics_create(self, id: str, data: MachinesMachinesUpdateMetricsCreateRequest) -> Machine:
        """
        Update machine metrics

        Update machine metrics (called by agent).
        """
        url = f"/api/machines/machines/{id}/update-metrics/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return Machine.model_validate(response.json())


