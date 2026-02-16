"""
Pytest configuration and fixtures for CMDOP SDK tests.
"""

import pytest

from cmdop.models.config import ConnectionConfig, KeepaliveConfig, RetryConfig
from cmdop.transport.base import BaseTransport, TransportState


class MockTransport(BaseTransport):
    """Mock transport for testing without real gRPC connection."""

    def __init__(self, config: ConnectionConfig | None = None) -> None:
        super().__init__(config)
        self._state = TransportState.READY

    @property
    def mode(self) -> str:
        return "mock"

    def _create_channel(self):
        """Return mock channel."""
        return None

    def _create_async_channel(self):
        """Return mock async channel."""
        return None

    def _get_metadata(self) -> list[tuple[str, str]]:
        return [("authorization", "Bearer mock_token")]


@pytest.fixture
def mock_transport() -> MockTransport:
    """Provide mock transport for testing."""
    return MockTransport()


@pytest.fixture
def connection_config() -> ConnectionConfig:
    """Provide default connection config."""
    return ConnectionConfig()


@pytest.fixture
def custom_config() -> ConnectionConfig:
    """Provide custom connection config."""
    return ConnectionConfig(
        connect_timeout_seconds=5.0,
        request_timeout_seconds=15.0,
        keepalive=KeepaliveConfig(
            time_ms=5000,
            timeout_ms=2000,
        ),
        retry=RetryConfig(
            max_attempts=5,
            initial_backoff_seconds=0.5,
        ),
    )


# ============================================================================
# Transport Mode Mocks (for streaming tests)
# ============================================================================


class MockLocalTransport:
    """Mock local transport for testing."""

    @property
    def mode(self) -> str:
        return "local"

    def get_async_channel(self):
        from unittest.mock import MagicMock
        return MagicMock()

    @property
    def metadata(self):
        return []


class MockRemoteTransport:
    """Mock remote transport for testing."""

    @property
    def mode(self) -> str:
        return "remote"

    def get_async_channel(self):
        from unittest.mock import MagicMock
        return MagicMock()

    @property
    def metadata(self):
        return [("authorization", "Bearer test_token")]


@pytest.fixture
def local_transport():
    """Create a mock local transport."""
    return MockLocalTransport()


@pytest.fixture
def remote_transport():
    """Create a mock remote transport."""
    return MockRemoteTransport()


# ============================================================================
# Settings Fixtures
# ============================================================================


@pytest.fixture
def reset_sdk_settings():
    """Reset SDK settings before and after test."""
    from cmdop.config import reset_settings

    reset_settings()
    yield
    reset_settings()


# ============================================================================
# HTTP Mocks for Discovery
# ============================================================================


@pytest.fixture
def mock_httpx_response():
    """Create a factory for mock httpx responses."""
    from unittest.mock import AsyncMock

    def _create_response(status_code: int = 200, json_data: dict | None = None):
        response = AsyncMock()
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.raise_for_status = AsyncMock()
        return response

    return _create_response


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_agent_data():
    """Sample agent data from API response."""
    return {
        "agent_id": "agent-test-123",
        "name": "Test Agent",
        "hostname": "test-server.local",
        "platform": "linux",
        "version": "1.0.0",
        "status": "online",
        "last_seen": "2025-12-31T12:00:00Z",
        "workspace_id": "ws-456",
        "labels": {"env": "test", "region": "us-east"},
    }


@pytest.fixture
def sample_agents_response(sample_agent_data):
    """Sample agents list API response."""
    return {
        "agents": [
            sample_agent_data,
            {
                "agent_id": "agent-test-456",
                "name": "Offline Agent",
                "hostname": "offline-server.local",
                "platform": "darwin",
                "version": "1.0.1",
                "status": "offline",
            },
        ]
    }
