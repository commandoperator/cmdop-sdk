from __future__ import annotations

import httpx

from .models import *


class WorkspacesWorkspacesAPI:
    """API endpoints for Workspaces."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def invitations_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedWorkspaceInvitationList]:
        """
        List invitations

        List all pending invitations for workspaces you manage
        """
        url = "/api/workspaces/invitations/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return PaginatedWorkspaceInvitationList.model_validate(response.json())


    async def invitations_create(self, data: WorkspaceInvitationCreateRequest) -> WorkspaceInvitation:
        """
        Create invitation

        Invite a user to a workspace by email
        """
        url = "/api/workspaces/invitations/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return WorkspaceInvitation.model_validate(response.json())


    async def invitations_retrieve(self, id: str) -> WorkspaceInvitation:
        """
        Get invitation details

        Get details of a specific invitation
        """
        url = f"/api/workspaces/invitations/{id}/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return WorkspaceInvitation.model_validate(response.json())


    async def invitations_destroy(self, id: str) -> None:
        """
        Cancel invitation

        Cancel a pending invitation
        """
        url = f"/api/workspaces/invitations/{id}/"
        response = await self._client.delete(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


    async def invitations_resend_create(self, id: str, data: WorkspaceInvitationRequest) -> WorkspaceInvitation:
        """
        Resend invitation

        Resend invitation email and regenerate token
        """
        url = f"/api/workspaces/invitations/{id}/resend/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return WorkspaceInvitation.model_validate(response.json())


    async def invitations_accept_create(self, data: WorkspaceInvitationAcceptRequest) -> None:
        """
        Accept invitation

        Accept a workspace invitation
        """
        url = "/api/workspaces/invitations/accept/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


    async def invitations_decline_create(self, data: WorkspaceInvitationAcceptRequest) -> None:
        """
        Decline invitation

        Decline a workspace invitation (no auth required)
        """
        url = "/api/workspaces/invitations/decline/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


    async def invitations_details_retrieve(self, token: str) -> WorkspaceInvitationPublic:
        """
        Get invitation details by token

        Get public invitation details for accept page (no auth required)
        """
        url = f"/api/workspaces/invitations/details/{token}/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return WorkspaceInvitationPublic.model_validate(response.json())


    async def members_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, role: str | None = None, search: str | None = None) -> list[PaginatedWorkspaceMemberList]:
        """
        List workspace members with optional search and role filters.
        """
        url = "/api/workspaces/members/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "role": role if role is not None else None, "search": search if search is not None else None})
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return PaginatedWorkspaceMemberList.model_validate(response.json())


    async def members_create(self, data: WorkspaceMemberRequest) -> WorkspaceMember:
        """
        ViewSet for WorkspaceMember operations. Manage workspace memberships and
        roles.
        """
        url = "/api/workspaces/members/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return WorkspaceMember.model_validate(response.json())


    async def members_retrieve(self, id: str) -> WorkspaceMember:
        """
        ViewSet for WorkspaceMember operations. Manage workspace memberships and
        roles.
        """
        url = f"/api/workspaces/members/{id}/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return WorkspaceMember.model_validate(response.json())


    async def members_update(self, id: str, data: WorkspaceMemberRequest) -> WorkspaceMember:
        """
        ViewSet for WorkspaceMember operations. Manage workspace memberships and
        roles.
        """
        url = f"/api/workspaces/members/{id}/"
        response = await self._client.put(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return WorkspaceMember.model_validate(response.json())


    async def members_partial_update(self, id: str, data: PatchedWorkspaceMemberRequest | None = None) -> WorkspaceMember:
        """
        ViewSet for WorkspaceMember operations. Manage workspace memberships and
        roles.
        """
        url = f"/api/workspaces/members/{id}/"
        response = await self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return WorkspaceMember.model_validate(response.json())


    async def members_destroy(self, id: str) -> None:
        """
        ViewSet for WorkspaceMember operations. Manage workspace memberships and
        roles.
        """
        url = f"/api/workspaces/members/{id}/"
        response = await self._client.delete(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


    async def members_update_role_create(self, id: str, data: WorkspaceMemberRequest) -> WorkspaceMember:
        """
        Update member role

        Update workspace member role.
        """
        url = f"/api/workspaces/members/{id}/update-role/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return WorkspaceMember.model_validate(response.json())


    async def workspaces_list(self, ordering: str | None = None, search: str | None = None) -> list[Workspace]:
        """
        ViewSet for Workspace operations. Provides CRUD operations for
        workspaces with team/personal modes.
        """
        url = "/api/workspaces/workspaces/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "search": search if search is not None else None})
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return [Workspace.model_validate(item) for item in response.json()]


    async def workspaces_create(self, data: WorkspaceCreateRequest) -> Workspace:
        """
        Create new workspace

        Create workspace and return full workspace data.
        """
        url = "/api/workspaces/workspaces/"
        response = await self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return Workspace.model_validate(response.json())


    async def workspaces_retrieve(self, id: str) -> Workspace:
        """
        ViewSet for Workspace operations. Provides CRUD operations for
        workspaces with team/personal modes.
        """
        url = f"/api/workspaces/workspaces/{id}/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return Workspace.model_validate(response.json())


    async def workspaces_update(self, id: str, data: WorkspaceRequest) -> Workspace:
        """
        ViewSet for Workspace operations. Provides CRUD operations for
        workspaces with team/personal modes.
        """
        url = f"/api/workspaces/workspaces/{id}/"
        response = await self._client.put(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return Workspace.model_validate(response.json())


    async def workspaces_partial_update(self, id: str, data: PatchedWorkspaceRequest | None = None) -> Workspace:
        """
        ViewSet for Workspace operations. Provides CRUD operations for
        workspaces with team/personal modes.
        """
        url = f"/api/workspaces/workspaces/{id}/"
        response = await self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return Workspace.model_validate(response.json())


    async def workspaces_destroy(self, id: str) -> None:
        """
        ViewSet for Workspace operations. Provides CRUD operations for
        workspaces with team/personal modes.
        """
        url = f"/api/workspaces/workspaces/{id}/"
        response = await self._client.delete(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


    async def workspaces_members_retrieve(self, id: str) -> None:
        """
        List workspace members

        Get all members of this workspace.
        """
        url = f"/api/workspaces/workspaces/{id}/members/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


    async def workspaces_stats_retrieve(self, id: str) -> None:
        """
        Get workspace statistics

        Get workspace statistics.
        """
        url = f"/api/workspaces/workspaces/{id}/stats/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return None


