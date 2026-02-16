from __future__ import annotations

import httpx

from .models import *


class SyncMachinesMachineSharingAPI:
    """Synchronous API endpoints for Machine Sharing."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def machines_machines_share_create(self, id: str, data: SharedMachineCreateRequest) -> SharedMachine:
        """
        Create share link for machine

        Create a public share link for read-only terminal viewing. Only
        workspace owner or admin can create shares.
        """
        url = f"/api/machines/machines/{id}/share/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return SharedMachine.model_validate(response.json())


    def machines_machines_shares_list(self, id: str, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedSharedMachineListList]:
        """
        List active shares for machine

        Get all active share links for this machine
        """
        url = f"/api/machines/machines/{id}/shares/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return PaginatedSharedMachineListList.model_validate(response.json())


    def machines_machines_unshare_destroy(self, id: str) -> None:
        """
        Remove all shares for machine

        Deactivate all share links for this machine. Only workspace owner or
        admin can remove shares.
        """
        url = f"/api/machines/machines/{id}/unshare/"
        response = self._client.delete(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)


