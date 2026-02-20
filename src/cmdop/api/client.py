"""
CMDOP API Client.

Unified client for all CMDOP HTTP APIs (machines, workspaces, system).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Literal

from cmdop.api.config import get_base_url

if TYPE_CHECKING:
    from cmdop.api.services.machines import MachinesService
    from cmdop.api.services.workspaces import WorkspacesService
    from cmdop.api.services.system import SystemService


class CMDOPAPI:
    """
    Unified CMDOP API client.

    Provides access to all CMDOP HTTP APIs through a single interface.
    Uses lazy initialization for service clients.

    Example:
        >>> # Basic usage
        >>> async with CMDOPAPI(api_key="cmd_xxx") as api:
        ...     machines = await api.machines.list()
        ...     workspaces = await api.workspaces.list()

        >>> # With environment mode
        >>> api = CMDOPAPI(api_key="cmd_xxx", mode="dev")

        >>> # With custom base URL
        >>> api = CMDOPAPI(api_key="cmd_xxx", base_url="https://custom.api.com")

        >>> # From environment variable
        >>> os.environ["CMDOP_API_KEY"] = "cmd_xxx"
        >>> async with CMDOPAPI() as api:
        ...     machines = await api.machines.list()
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        mode: Literal["prod", "dev", "local"] = "prod",
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize CMDOP API client.

        Args:
            api_key: API key (or set CMDOP_API_KEY env var)
            base_url: Custom base URL (overrides mode)
            mode: Environment mode - "prod", "dev", or "local"
            timeout: Request timeout in seconds

        Raises:
            ValueError: If no API key provided
        """
        self._api_key = api_key or os.environ.get("CMDOP_API_KEY")
        if not self._api_key:
            raise ValueError(
                "API key required. Pass api_key or set CMDOP_API_KEY environment variable."
            )

        self._base_url = base_url or get_base_url(mode)
        self._timeout = timeout
        self._mode = mode

        # Lazy-initialized API clients
        self._machines_api: Any = None
        self._workspaces_api: Any = None
        self._system_api: Any = None

        # Lazy-initialized services
        self._machines_service: MachinesService | None = None
        self._workspaces_service: WorkspacesService | None = None
        self._system_service: SystemService | None = None

    @property
    def machines(self) -> MachinesService:
        """
        Access machines API.

        Returns:
            MachinesService for machine management
        """
        if self._machines_service is None:
            from cmdop.api.generated import machines
            from cmdop.api.services.machines import MachinesService

            self._machines_api = machines.API(self._base_url)
            self._machines_api.set_token(self._api_key)
            self._machines_service = MachinesService(self._machines_api)

        return self._machines_service

    @property
    def workspaces(self) -> WorkspacesService:
        """
        Access workspaces API.

        Returns:
            WorkspacesService for workspace management
        """
        if self._workspaces_service is None:
            from cmdop.api.generated import workspaces
            from cmdop.api.services.workspaces import WorkspacesService

            self._workspaces_api = workspaces.API(self._base_url)
            self._workspaces_api.set_token(self._api_key)
            self._workspaces_service = WorkspacesService(self._workspaces_api)

        return self._workspaces_service

    @property
    def system(self) -> SystemService:
        """
        Access system API.

        Returns:
            SystemService for system operations
        """
        if self._system_service is None:
            from cmdop.api.generated import system
            from cmdop.api.services.system import SystemService

            self._system_api = system.API(self._base_url)
            self._system_api.set_token(self._api_key)
            self._system_service = SystemService(self._system_api)

        return self._system_service

    @property
    def base_url(self) -> str:
        """Get current base URL."""
        return self._base_url

    @property
    def mode(self) -> str:
        """Get current environment mode."""
        return self._mode

    async def __aenter__(self) -> CMDOPAPI:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close all API clients."""
        if self._machines_api:
            await self._machines_api.close()
        if self._workspaces_api:
            await self._workspaces_api.close()
        if self._system_api:
            await self._system_api.close()

    def __repr__(self) -> str:
        return f"<CMDOPAPI base_url={self._base_url!r} mode={self._mode!r}>"


__all__ = ["CMDOPAPI"]
