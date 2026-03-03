"""
Remote agent discovery via REST API.

Uses the generated machines API client (CMDOPAPI).
For local agent discovery, see transport/discovery.py.
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from cmdop.api.client import CMDOPAPI
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
            with contextlib.suppress(ValueError, TypeError):
                last_seen = datetime.fromisoformat(
                    data["last_seen"].replace("Z", "+00:00")
                )

        status_str = data.get("status", "offline")
        if data.get("is_online"):
            status_str = "online"

        return cls(
            agent_id=data.get("id", data.get("agent_id", "")),
            name=data.get("name", data.get("hostname", "Unknown")),
            hostname=data.get("hostname", ""),
            platform=data.get("os", data.get("platform", "")),
            version=data.get("agent_version", data.get("version", "")),
            status=AgentStatus(status_str),
            last_seen=last_seen,
            workspace_id=data.get("workspace", data.get("workspace_id")),
            labels=data.get("labels"),
        )


class AgentDiscovery:
    """
    Remote agent discovery client.

    Lists agents available for an API key via the machines REST API.

    Usage:
        >>> discovery = AgentDiscovery(api_key="cmdop_live_xxx")
        >>> agents = await discovery.list_agents()
        >>> online = await discovery.get_online_agents()
        >>> agent = await discovery.get_agent("agent-id")
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._settings = get_settings()

    def _create_api(self) -> CMDOPAPI:
        """Create API client with the stored key."""
        return CMDOPAPI(
            api_key=self._api_key,
            base_url=self._settings.api_base_url,
        )

    async def list_agents(self) -> list[RemoteAgentInfo]:
        """
        List all agents available for API key.
        Fetches all pages of machines from the workspace.

        Raises:
            InvalidAPIKeyError: On invalid API key.
            PermissionDeniedError: On insufficient permissions.
        """
        async with self._create_api() as api:
            all_agents: list[RemoteAgentInfo] = []
            page = 1

            while True:
                result = await api.machines.list(page=page, page_size=100)
                for m in result.results:
                    data = m.model_dump()
                    all_agents.append(RemoteAgentInfo.from_dict(data))

                if not result.has_next:
                    break
                page += 1

            return all_agents

    async def get_online_agents(self) -> list[RemoteAgentInfo]:
        """List only online agents."""
        agents = await self.list_agents()
        return [a for a in agents if a.is_online]

    async def get_agent(self, agent_id: str) -> RemoteAgentInfo | None:
        """
        Get specific agent by ID.

        Returns:
            RemoteAgentInfo if found, None otherwise.
        """
        async with self._create_api() as api:
            try:
                machine = await api.machines.get(agent_id)
                data = machine.model_dump()
                return RemoteAgentInfo.from_dict(data)
            except Exception:
                return None

    async def wait_for_agent(
        self,
        agent_id: str,
        timeout: float = 30.0,
        poll_interval: float = 2.0,
    ) -> RemoteAgentInfo:
        """
        Wait for agent to come online.

        Raises:
            TimeoutError: If agent doesn't come online within timeout.
        """
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
    """
    discovery = AgentDiscovery(api_key)
    return await discovery.get_online_agents()
