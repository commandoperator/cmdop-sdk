"""
Remote agent discovery via REST API.

Lists agents available for an API key from the cloud management API.
For local agent discovery, see transport/discovery.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import httpx

from cmdop.config import get_settings


class AgentStatus(str, Enum):
    """Remote agent status."""

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


@dataclass
class RemoteAgentInfo:
    """
    Information about a remote agent from the cloud API.

    Different from transport.discovery.AgentInfo which is for local discovery.
    """

    agent_id: str
    """Unique agent identifier."""

    name: str
    """Human-readable agent name."""

    hostname: str
    """Machine hostname."""

    platform: str
    """OS platform (darwin, linux, windows)."""

    version: str
    """Agent version string."""

    status: AgentStatus
    """Current agent status."""

    last_seen: datetime | None
    """Last time agent was seen online."""

    workspace_id: str | None
    """Workspace this agent belongs to."""

    labels: dict[str, str] | None
    """Optional agent labels/tags."""

    @property
    def is_online(self) -> bool:
        """Check if agent is online."""
        return self.status == AgentStatus.ONLINE

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RemoteAgentInfo:
        """Create from API response dictionary."""
        last_seen = None
        if data.get("last_seen"):
            try:
                last_seen = datetime.fromisoformat(
                    data["last_seen"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass

        return cls(
            agent_id=data["agent_id"],
            name=data.get("name", data.get("hostname", "Unknown")),
            hostname=data.get("hostname", ""),
            platform=data.get("platform", ""),
            version=data.get("version", ""),
            status=AgentStatus(data.get("status", "offline")),
            last_seen=last_seen,
            workspace_id=data.get("workspace_id"),
            labels=data.get("labels"),
        )


class AgentDiscovery:
    """
    Remote agent discovery client.

    Lists agents available for an API key via REST API.
    Uses httpx for async HTTP requests with stamina retry.

    Usage:
        >>> discovery = AgentDiscovery(api_key="cmdop_live_xxx")
        >>> agents = await discovery.list_agents()
        >>> online = await discovery.get_online_agents()
        >>> agent = await discovery.get_agent("agent-id")
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize agent discovery.

        Args:
            api_key: CMDOP API key for authentication.
        """
        self._api_key = api_key
        self._settings = get_settings()

    @property
    def _base_url(self) -> str:
        """Get API base URL."""
        return self._settings.api_base_url

    @property
    def _headers(self) -> dict[str, str]:
        """Get request headers with auth."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "User-Agent": "cmdop-sdk-python/0.1.0",
        }

    async def list_agents(self) -> list[RemoteAgentInfo]:
        """
        List all agents available for API key.

        Returns:
            List of RemoteAgentInfo objects.

        Raises:
            httpx.HTTPError: On network or API errors.
            AuthenticationError: On invalid API key.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._base_url}/api/v1/sdk/agents/",
                headers=self._headers,
                timeout=self._settings.request_timeout,
            )

            if response.status_code == 401:
                from cmdop.exceptions import InvalidAPIKeyError

                raise InvalidAPIKeyError("Invalid or expired API key")

            if response.status_code == 403:
                from cmdop.exceptions import PermissionDeniedError

                raise PermissionDeniedError("API key lacks agent access")

            response.raise_for_status()
            data = response.json()

            agents = [
                RemoteAgentInfo.from_dict(agent)
                for agent in data.get("agents", data.get("results", []))
            ]

            return agents

    async def get_online_agents(self) -> list[RemoteAgentInfo]:
        """
        List only online agents.

        Returns:
            List of online RemoteAgentInfo objects.
        """
        agents = await self.list_agents()
        return [a for a in agents if a.is_online]

    async def get_agent(self, agent_id: str) -> RemoteAgentInfo | None:
        """
        Get specific agent by ID.

        Args:
            agent_id: Agent UUID.

        Returns:
            RemoteAgentInfo if found, None otherwise.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._base_url}/api/v1/sdk/agents/{agent_id}/",
                headers=self._headers,
                timeout=self._settings.request_timeout,
            )

            if response.status_code == 404:
                return None

            if response.status_code == 401:
                from cmdop.exceptions import InvalidAPIKeyError

                raise InvalidAPIKeyError("Invalid or expired API key")

            response.raise_for_status()
            data = response.json()

            return RemoteAgentInfo.from_dict(data)

    async def wait_for_agent(
        self,
        agent_id: str,
        timeout: float = 30.0,
        poll_interval: float = 2.0,
    ) -> RemoteAgentInfo:
        """
        Wait for agent to come online.

        Args:
            agent_id: Agent UUID to wait for.
            timeout: Maximum time to wait in seconds.
            poll_interval: Time between checks in seconds.

        Returns:
            RemoteAgentInfo when agent is online.

        Raises:
            TimeoutError: If agent doesn't come online within timeout.
        """
        import asyncio

        deadline = asyncio.get_event_loop().time() + timeout

        while asyncio.get_event_loop().time() < deadline:
            agent = await self.get_agent(agent_id)

            if agent and agent.is_online:
                return agent

            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Agent {agent_id} did not come online within {timeout}s")


async def list_agents(api_key: str) -> list[RemoteAgentInfo]:
    """
    Convenience function to list agents.

    Args:
        api_key: CMDOP API key.

    Returns:
        List of available agents.

    Example:
        >>> from cmdop import list_agents
        >>> agents = await list_agents("cmdop_live_xxx")
        >>> for agent in agents:
        ...     print(f"{agent.name}: {agent.status.value}")
    """
    discovery = AgentDiscovery(api_key)
    return await discovery.list_agents()


async def get_online_agents(api_key: str) -> list[RemoteAgentInfo]:
    """
    Convenience function to list online agents.

    Args:
        api_key: CMDOP API key.

    Returns:
        List of online agents.
    """
    discovery = AgentDiscovery(api_key)
    return await discovery.get_online_agents()
