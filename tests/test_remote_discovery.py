"""
Tests for remote agent discovery module (uses CMDOPAPI machines client).
"""

from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from cmdop.discovery import (
    AgentDiscovery,
    AgentStatus,
    RemoteAgentInfo,
    get_online_agents,
    list_agents,
)


def _make_machine(**kwargs):
    """Create a mock machine object with model_dump()."""
    defaults = {
        "id": "",
        "name": "Unknown",
        "hostname": "",
        "os": "",
        "agent_version": "",
        "status": "offline",
        "is_online": False,
        "last_seen": None,
        "workspace": None,
        "labels": None,
    }
    defaults.update(kwargs)
    m = MagicMock()
    m.model_dump.return_value = defaults
    return m


def _make_paginated(machines, has_next=False):
    """Create a mock paginated response."""
    result = MagicMock()
    result.results = machines
    result.has_next = has_next
    return result


class TestRemoteAgentInfo:
    """Tests for RemoteAgentInfo dataclass."""

    def test_from_dict_full(self):
        """Test creating RemoteAgentInfo from full API response."""
        data = {
            "id": "agent-123",
            "name": "My Agent",
            "hostname": "server.local",
            "os": "linux",
            "agent_version": "1.0.0",
            "status": "online",
            "is_online": True,
            "last_seen": "2025-12-31T12:00:00Z",
            "workspace": "ws-456",
            "labels": {"env": "prod"},
        }

        agent = RemoteAgentInfo.from_dict(data)

        assert agent.agent_id == "agent-123"
        assert agent.name == "My Agent"
        assert agent.hostname == "server.local"
        assert agent.platform == "linux"
        assert agent.version == "1.0.0"
        assert agent.status == AgentStatus.ONLINE
        assert agent.last_seen is not None
        assert agent.workspace_id == "ws-456"
        assert agent.labels == {"env": "prod"}
        assert agent.is_online is True

    def test_from_dict_minimal(self):
        """Test creating RemoteAgentInfo with minimal data."""
        data = {
            "id": "agent-123",
            "status": "offline",
        }

        agent = RemoteAgentInfo.from_dict(data)

        assert agent.agent_id == "agent-123"
        assert agent.name == "Unknown"
        assert agent.hostname == ""
        assert agent.status == AgentStatus.OFFLINE
        assert agent.is_online is False
        assert agent.last_seen is None
        assert agent.workspace_id is None
        assert agent.labels is None

    def test_from_dict_uses_hostname_as_name_fallback(self):
        """Test that hostname is used as name fallback."""
        data = {
            "id": "agent-123",
            "hostname": "server.local",
            "is_online": True,
        }

        agent = RemoteAgentInfo.from_dict(data)

        assert agent.name == "server.local"

    def test_from_dict_is_online_overrides_status(self):
        """Test that is_online=True sets status to online."""
        data = {
            "id": "agent-123",
            "status": "offline",
            "is_online": True,
        }

        agent = RemoteAgentInfo.from_dict(data)
        assert agent.status == AgentStatus.ONLINE

    def test_agent_status_enum(self):
        """Test AgentStatus enum values."""
        assert AgentStatus.ONLINE.value == "online"
        assert AgentStatus.OFFLINE.value == "offline"
        assert AgentStatus.BUSY.value == "busy"

    def test_is_online_property(self):
        """Test is_online property for different statuses."""
        online_agent = RemoteAgentInfo.from_dict({"id": "1", "is_online": True})
        offline_agent = RemoteAgentInfo.from_dict({"id": "2", "status": "offline"})
        busy_agent = RemoteAgentInfo.from_dict({"id": "3", "status": "busy"})

        assert online_agent.is_online is True
        assert offline_agent.is_online is False
        assert busy_agent.is_online is False


class TestAgentDiscovery:
    """Tests for AgentDiscovery client."""

    @pytest.fixture
    def discovery(self):
        """Create AgentDiscovery instance for testing."""
        return AgentDiscovery(api_key="cmdop_test_api_key")

    @pytest.mark.asyncio
    async def test_list_agents_success(self, discovery):
        """Test successful list_agents call."""
        machines = [
            _make_machine(id="agent-1", name="Agent One", hostname="server1.local",
                          os="linux", agent_version="1.0.0", is_online=True, status="online"),
            _make_machine(id="agent-2", name="Agent Two", hostname="server2.local",
                          os="darwin", agent_version="1.0.1", is_online=False, status="offline"),
        ]
        mock_api = AsyncMock()
        mock_api.machines.list.return_value = _make_paginated(machines)
        mock_api.__aenter__ = AsyncMock(return_value=mock_api)
        mock_api.__aexit__ = AsyncMock(return_value=None)

        with patch.object(discovery, "_create_api", return_value=mock_api):
            agents = await discovery.list_agents()

        assert len(agents) == 2
        assert agents[0].agent_id == "agent-1"
        assert agents[0].is_online is True
        assert agents[1].agent_id == "agent-2"
        assert agents[1].is_online is False

    @pytest.mark.asyncio
    async def test_list_agents_pagination(self, discovery):
        """Test list_agents fetches all pages."""
        page1 = [_make_machine(id="agent-1", is_online=True, status="online")]
        page2 = [_make_machine(id="agent-2", is_online=False, status="offline")]

        mock_api = AsyncMock()
        mock_api.machines.list.side_effect = [
            _make_paginated(page1, has_next=True),
            _make_paginated(page2, has_next=False),
        ]
        mock_api.__aenter__ = AsyncMock(return_value=mock_api)
        mock_api.__aexit__ = AsyncMock(return_value=None)

        with patch.object(discovery, "_create_api", return_value=mock_api):
            agents = await discovery.list_agents()

        assert len(agents) == 2
        assert mock_api.machines.list.call_count == 2

    @pytest.mark.asyncio
    async def test_get_online_agents(self, discovery):
        """Test get_online_agents filters offline agents."""
        machines = [
            _make_machine(id="agent-1", is_online=True, status="online"),
            _make_machine(id="agent-2", is_online=False, status="offline"),
        ]
        mock_api = AsyncMock()
        mock_api.machines.list.return_value = _make_paginated(machines)
        mock_api.__aenter__ = AsyncMock(return_value=mock_api)
        mock_api.__aexit__ = AsyncMock(return_value=None)

        with patch.object(discovery, "_create_api", return_value=mock_api):
            agents = await discovery.get_online_agents()

        assert len(agents) == 1
        assert agents[0].agent_id == "agent-1"
        assert agents[0].is_online is True

    @pytest.mark.asyncio
    async def test_get_agent_found(self, discovery):
        """Test get_agent returns agent when found."""
        machine = MagicMock()
        machine.model_dump.return_value = {
            "id": "agent-123",
            "name": "My Agent",
            "hostname": "server.local",
            "os": "linux",
            "is_online": True,
            "status": "online",
        }

        mock_api = AsyncMock()
        mock_api.machines.get.return_value = machine
        mock_api.__aenter__ = AsyncMock(return_value=mock_api)
        mock_api.__aexit__ = AsyncMock(return_value=None)

        with patch.object(discovery, "_create_api", return_value=mock_api):
            agent = await discovery.get_agent("agent-123")

        assert agent is not None
        assert agent.agent_id == "agent-123"

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, discovery):
        """Test get_agent returns None when not found."""
        mock_api = AsyncMock()
        mock_api.machines.get.side_effect = Exception("Not found")
        mock_api.__aenter__ = AsyncMock(return_value=mock_api)
        mock_api.__aexit__ = AsyncMock(return_value=None)

        with patch.object(discovery, "_create_api", return_value=mock_api):
            agent = await discovery.get_agent("nonexistent")

        assert agent is None


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.mark.asyncio
    async def test_list_agents_function(self):
        """Test list_agents convenience function."""
        mock_api = AsyncMock()
        mock_api.machines.list.return_value = _make_paginated([])
        mock_api.__aenter__ = AsyncMock(return_value=mock_api)
        mock_api.__aexit__ = AsyncMock(return_value=None)

        with patch("cmdop.discovery.CMDOPAPI", return_value=mock_api):
            agents = await list_agents("cmdop_test_key")

        assert agents == []

    @pytest.mark.asyncio
    async def test_get_online_agents_function(self):
        """Test get_online_agents convenience function."""
        machines = [
            _make_machine(id="1", is_online=True, status="online"),
            _make_machine(id="2", is_online=False, status="offline"),
        ]
        mock_api = AsyncMock()
        mock_api.machines.list.return_value = _make_paginated(machines)
        mock_api.__aenter__ = AsyncMock(return_value=mock_api)
        mock_api.__aexit__ = AsyncMock(return_value=None)

        with patch("cmdop.discovery.CMDOPAPI", return_value=mock_api):
            agents = await get_online_agents("cmdop_test_key")

        assert len(agents) == 1
        assert agents[0].agent_id == "1"
