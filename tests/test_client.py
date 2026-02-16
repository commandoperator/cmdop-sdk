"""
Tests for CMDOP SDK client classes.
"""

import pytest

from cmdop import AsyncCMDOPClient, CMDOPClient
from cmdop.transport.remote import RemoteTransport


class TestCMDOPClient:
    """Tests for CMDOPClient."""

    def test_remote_creation(self):
        """Test client creation via remote()."""
        client = CMDOPClient.remote(api_key="cmdop_live_testkey123456789")
        assert client.mode == "remote"
        assert client.is_connected is False  # Not connected until first call
        client.close()

    def test_from_transport(self):
        """Test client creation from transport."""
        transport = RemoteTransport(api_key="cmdop_live_testkey123456789")
        client = CMDOPClient.from_transport(transport)
        assert client.transport is transport
        client.close()

    def test_terminal_namespace(self):
        """Test terminal service namespace."""
        client = CMDOPClient.remote(api_key="cmdop_live_testkey123456789")
        terminal = client.terminal
        assert terminal is not None
        # Should return same instance on repeated access
        assert client.terminal is terminal
        client.close()

    def test_files_namespace(self):
        """Test files service namespace."""
        client = CMDOPClient.remote(api_key="cmdop_live_testkey123456789")
        files = client.files
        assert files is not None
        assert client.files is files
        client.close()

    def test_local_no_agent(self):
        """Test that local() raises AgentNotRunningError when no agent."""
        from cmdop.exceptions import AgentNotRunningError

        with pytest.raises(AgentNotRunningError):
            CMDOPClient.local(discovery_paths=["/nonexistent/path"], use_defaults=False)

    def test_context_manager(self):
        """Test context manager support."""
        with CMDOPClient.remote(api_key="cmdop_live_testkey123456789") as client:
            assert client is not None
        # Should be closed after exit

    def test_repr(self):
        """Test string representation."""
        client = CMDOPClient.remote(api_key="cmdop_live_testkey123456789")
        repr_str = repr(client)
        assert "CMDOPClient" in repr_str
        assert "remote" in repr_str
        client.close()


class TestAsyncCMDOPClient:
    """Tests for AsyncCMDOPClient."""

    def test_remote_creation(self):
        """Test async client creation via remote()."""
        client = AsyncCMDOPClient.remote(api_key="cmdop_live_testkey123456789")
        assert client.mode == "remote"

    def test_terminal_namespace(self):
        """Test terminal service namespace."""
        client = AsyncCMDOPClient.remote(api_key="cmdop_live_testkey123456789")
        terminal = client.terminal
        assert terminal is not None
        assert client.terminal is terminal

    def test_files_namespace(self):
        """Test files service namespace."""
        client = AsyncCMDOPClient.remote(api_key="cmdop_live_testkey123456789")
        files = client.files
        assert files is not None
        assert client.files is files

    def test_local_no_agent(self):
        """Test that local() raises AgentNotRunningError when no agent."""
        from cmdop.exceptions import AgentNotRunningError

        with pytest.raises(AgentNotRunningError):
            AsyncCMDOPClient.local(discovery_paths=["/nonexistent/path"], use_defaults=False)

    def test_repr(self):
        """Test string representation."""
        client = AsyncCMDOPClient.remote(api_key="cmdop_live_testkey123456789")
        repr_str = repr(client)
        assert "AsyncCMDOPClient" in repr_str
        assert "remote" in repr_str
