"""
Tests for CMDOP SDK transport layer.
"""

import pytest

from cmdop.models.config import ConnectionConfig
from cmdop.transport.base import TransportState
from cmdop.transport.remote import RemoteTransport


class TestRemoteTransport:
    """Tests for RemoteTransport."""

    def test_creation(self):
        """Test transport creation."""
        transport = RemoteTransport(api_key="cmdop_live_testkey123456789")
        assert transport.mode == "remote"
        assert transport.server == "grpc.cmdop.com:443"
        assert transport.state == TransportState.IDLE

    def test_custom_server(self):
        """Test custom server endpoint."""
        transport = RemoteTransport(
            api_key="cmdop_test_testkey123456789",
            server="custom.server.com:443",
        )
        assert transport.server == "custom.server.com:443"

    def test_with_agent_id(self):
        """Test with specific agent ID."""
        transport = RemoteTransport(
            api_key="cmdop_live_testkey123456789",
            agent_id="550e8400-e29b-41d4-a716-446655440000",
        )
        assert transport.agent_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_invalid_api_key(self):
        """Test invalid API key format."""
        with pytest.raises(ValueError) as exc:
            RemoteTransport(api_key="invalid_key")
        assert "must start with" in str(exc.value)

    def test_metadata(self):
        """Test metadata generation."""
        transport = RemoteTransport(api_key="cmdop_live_testkey123456789")
        metadata = transport.metadata

        # Should contain authorization header
        auth_headers = [h for h in metadata if h[0] == "authorization"]
        assert len(auth_headers) == 1
        assert auth_headers[0][1].startswith("Bearer ")

    def test_metadata_with_agent_id(self):
        """Test metadata includes agent ID when set."""
        transport = RemoteTransport(
            api_key="cmdop_live_testkey123456789",
            agent_id="test-agent-id",
        )
        metadata = transport.metadata

        agent_headers = [h for h in metadata if h[0] == "x-cmdop-agent-id"]
        assert len(agent_headers) == 1
        assert agent_headers[0][1] == "test-agent-id"

    def test_with_config(self):
        """Test with custom configuration."""
        config = ConnectionConfig(
            connect_timeout_seconds=5.0,
            request_timeout_seconds=15.0,
        )
        transport = RemoteTransport(
            api_key="cmdop_live_testkey123456789",
            config=config,
        )
        assert transport.config.connect_timeout_seconds == 5.0

    def test_repr(self):
        """Test string representation."""
        transport = RemoteTransport(api_key="cmdop_live_testkey123456789")
        repr_str = repr(transport)
        assert "RemoteTransport" in repr_str
        assert "grpc.cmdop.com" in repr_str

    def test_context_manager(self):
        """Test context manager support."""
        with RemoteTransport(api_key="cmdop_live_testkey123456789") as transport:
            assert transport.state in (TransportState.IDLE, TransportState.READY)
        assert transport.state == TransportState.SHUTDOWN


class TestTransportState:
    """Tests for TransportState enum."""

    def test_values(self):
        """Test state values."""
        assert TransportState.IDLE == "idle"
        assert TransportState.CONNECTING == "connecting"
        assert TransportState.READY == "ready"
        assert TransportState.SHUTDOWN == "shutdown"
