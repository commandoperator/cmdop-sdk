"""
Workspaces service for CMDOP API.

Provides high-level interface for workspace management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cmdop.api.generated.workspaces import API as WorkspacesAPI
    from cmdop.api.generated.workspaces.workspaces__api__workspaces.models import (
        Workspace,
        WorkspaceMember,
        PaginatedWorkspaceList,
    )


class WorkspacesService:
    """
    High-level workspaces service.

    Wraps the generated workspaces API with convenient methods.

    Example:
        >>> async with CMDOPAPI(api_key="cmd_xxx") as api:
        ...     workspaces = await api.workspaces.list()
        ...     workspace = await api.workspaces.get(123)
    """

    def __init__(self, api: WorkspacesAPI) -> None:
        """
        Initialize workspaces service.

        Args:
            api: Generated workspaces API client
        """
        self._api = api
        self._client = api.workspaces_workspaces

    async def list(
        self,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
    ) -> PaginatedWorkspaceList:
        """
        List workspaces.

        Args:
            search: Search query
            page: Page number
            page_size: Items per page
            ordering: Sort field

        Returns:
            Paginated list of workspaces
        """
        return await self._client.workspaces_list(
            search=search,
            page=page,
            page_size=page_size,
            ordering=ordering,
        )

    async def get(self, workspace_id: int | str) -> Workspace:
        """
        Get workspace by ID.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace details
        """
        return await self._client.workspaces_retrieve(id=str(workspace_id))

    async def get_current(self) -> Workspace:
        """
        Get current workspace (for authenticated user).

        Returns:
            Current workspace details
        """
        return await self._client.workspaces_current_retrieve()

    async def get_members(
        self,
        workspace_id: int | str,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[WorkspaceMember]:
        """
        Get workspace members.

        Args:
            workspace_id: Workspace ID
            page: Page number
            page_size: Items per page

        Returns:
            List of workspace members
        """
        return await self._client.workspaces_members_list(
            id=str(workspace_id),
            page=page,
            page_size=page_size,
        )

    async def invite_member(
        self,
        workspace_id: int | str,
        email: str,
        role: str = "member",
    ) -> None:
        """
        Invite a member to workspace.

        Args:
            workspace_id: Workspace ID
            email: Email to invite
            role: Member role
        """
        from cmdop.api.generated.workspaces.workspaces__api__workspaces.models import (
            WorkspaceInvitationCreateRequest,
        )

        data = WorkspaceInvitationCreateRequest(email=email, role=role)
        await self._client.workspaces_invitations_create(
            id=str(workspace_id),
            data=data,
        )

    async def remove_member(
        self,
        workspace_id: int | str,
        member_id: int | str,
    ) -> None:
        """
        Remove a member from workspace.

        Args:
            workspace_id: Workspace ID
            member_id: Member ID to remove
        """
        await self._client.workspaces_members_destroy(
            id=str(workspace_id),
            member_pk=str(member_id),
        )
