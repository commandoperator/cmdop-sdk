"""
Tests for remote agent discovery module (httpx REST client).
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from cmdop.discovery import (
    AgentDiscovery,
    AgentStatus,
    RemoteAgentInfo,
    get_online_agents,
    list_agents,
)
from cmdop.exceptions import InvalidAPIKeyError, PermissionDeniedError


class TestRemoteAgentInfo:
    """Tests for RemoteAgentInfo dataclass."""

    def test_from_dict_full(self):
        """Test creating RemoteAgentInfo from full API response."""
        data = {
            "agent_id": "agent-123",
            "name": "My Agent",
            "hostname": "server.local",
            "platform": "linux",
            "version": "1.0.0",
            "status": "online",
            "last_seen": "2025-12-31T12:00:00Z",
            "workspace_id": "ws-456",
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
            "agent_id": "agent-123",
            "status": "offline",
        }

        agent = RemoteAgentInfo.from_dict(data)

        assert agent.agent_id == "agent-123"
        assert agent.name == "Unknown"  # fallback
        assert agent.hostname == ""
        assert agent.status == AgentStatus.OFFLINE
        assert agent.is_online is False
        assert agent.last_seen is None
        assert agent.workspace_id is None
        assert agent.labels is None

    def test_from_dict_uses_hostname_as_name_fallback(self):
        """Test that hostname is used as name fallback."""
        data = {
            "agent_id": "agent-123",
            "hostname": "server.local",
            "status": "online",
        }

        agent = RemoteAgentInfo.from_dict(data)

        assert agent.name == "server.local"

    def test_agent_status_enum(self):
        """Test AgentStatus enum values."""
        assert AgentStatus.ONLINE.value == "online"
        assert AgentStatus.OFFLINE.value == "offline"
        assert AgentStatus.BUSY.value == "busy"

    def test_is_online_property(self):
        """Test is_online property for different statuses."""
        online_agent = RemoteAgentInfo.from_dict({
            "agent_id": "1",
            "status": "online",
        })
        offline_agent = RemoteAgentInfo.from_dict({
            "agent_id": "2",
            "status": "offline",
        })
        busy_agent = RemoteAgentInfo.from_dict({
            "agent_id": "3",
            "status": "busy",
        })

        assert online_agent.is_online is True
        assert offline_agent.is_online is False
        assert busy_agent.is_online is False


class TestAgentDiscovery:
    """Tests for AgentDiscovery client."""

    @pytest.fixture
    def discovery(self):
        """Create AgentDiscovery instance for testing."""
        return AgentDiscovery(api_key="test_api_key")

    @pytest.fixture
    def mock_response_agents(self):
        """Mock API response with multiple agents."""
        return {
            "agents": [
                {
                    "agent_id": "agent-1",
                    "name": "Agent One",
                    "hostname": "server1.local",
                    "platform": "linux",
                    "version": "1.0.0",
                    "status": "online",
                },
                {
                    "agent_id": "agent-2",
                    "name": "Agent Two",
                    "hostname": "server2.local",
                    "platform": "darwin",
                    "version": "1.0.1",
                    "status": "offline",
                },
            ]
        }

    @pytest.mark.asyncio
    async def test_list_agents_success(self, discovery, mock_response_agents):
        """Test successful list_agents call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_agents
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            agents = await discovery.list_agents()

            assert len(agents) == 2
            assert agents[0].agent_id == "agent-1"
            assert agents[0].is_online is True
            assert agents[1].agent_id == "agent-2"
            assert agents[1].is_online is False

    @pytest.mark.asyncio
    async def test_list_agents_with_results_key(self, discovery):
        """Test list_agents with 'results' key instead of 'agents'."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"agent_id": "agent-1", "status": "online"},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            agents = await discovery.list_agents()

            assert len(agents) == 1

    @pytest.mark.asyncio
    async def test_list_agents_invalid_api_key(self, discovery):
        """Test list_agents with invalid API key (401)."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            with pytest.raises(InvalidAPIKeyError):
                await discovery.list_agents()

    @pytest.mark.asyncio
    async def test_list_agents_permission_denied(self, discovery):
        """Test list_agents with permission denied (403)."""
        mock_response = MagicMock()
        mock_response.status_code = 403

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            with pytest.raises(PermissionDeniedError):
                await discovery.list_agents()

    @pytest.mark.asyncio
    async def test_get_online_agents(self, discovery, mock_response_agents):
        """Test get_online_agents filters offline agents."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_agents
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            agents = await discovery.get_online_agents()

            assert len(agents) == 1
            assert agents[0].agent_id == "agent-1"
            assert agents[0].is_online is True

    @pytest.mark.asyncio
    async def test_get_agent_found(self, discovery):
        """Test get_agent returns agent when found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agent_id": "agent-123",
            "name": "My Agent",
            "status": "online",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            agent = await discovery.get_agent("agent-123")

            assert agent is not None
            assert agent.agent_id == "agent-123"

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, discovery):
        """Test get_agent returns None when not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            agent = await discovery.get_agent("nonexistent")

            assert agent is None

    def test_headers_contain_auth(self, discovery):
        """Test that headers contain authorization."""
        headers = discovery._headers

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_api_key"
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.mark.asyncio
    async def test_list_agents_function(self):
        """Test list_agents convenience function."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"agents": []}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            agents = await list_agents("test_key")

            assert agents == []

    @pytest.mark.asyncio
    async def test_get_online_agents_function(self):
        """Test get_online_agents convenience function."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agents": [
                {"agent_id": "1", "status": "online"},
                {"agent_id": "2", "status": "offline"},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            agents = await get_online_agents("test_key")

            assert len(agents) == 1
            assert agents[0].agent_id == "1"
