"""
Tests for local transport (discovery, auth, LocalTransport).
"""

import json
import os
import platform
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from cmdop.exceptions import AgentNotRunningError, StalePortFileError
from cmdop.transport.auth import (
    FileTokenAuth,
    SecurityWarning,
    get_local_auth_metadata,
    supports_peercred,
)
from cmdop.transport.discovery import (
    AgentInfo,
    DiscoveryResult,
    TransportType,
    check_process_running,
    discover_agent,
    get_default_discovery_paths,
    read_discovery_file,
    require_agent,
)
from cmdop.transport.local import LocalTransport


class TestAgentInfo:
    """Tests for AgentInfo dataclass."""

    def test_from_dict(self):
        """Test creating AgentInfo from dictionary."""
        data = {
            "version": "1.0.30",
            "pid": 12345,
            "transport": "unix",
            "address": "/tmp/cmdop.sock",
            "token_path": None,
            "started_at": "2024-01-15T10:30:00Z",
        }
        info = AgentInfo.from_dict(data)

        assert info.version == "1.0.30"
        assert info.pid == 12345
        assert info.transport == TransportType.UNIX_SOCKET
        assert info.address == "/tmp/cmdop.sock"
        assert info.token_path is None

    def test_from_dict_with_token(self):
        """Test AgentInfo with token path."""
        data = {
            "version": "1.0.30",
            "pid": 12345,
            "transport": "tcp",
            "address": "localhost:50052",
            "token_path": "~/.cmdop/token",
            "started_at": "2024-01-15T10:30:00Z",
        }
        info = AgentInfo.from_dict(data)

        assert info.transport == TransportType.TCP
        assert info.token_path == "~/.cmdop/token"


class TestDiscoveryPaths:
    """Tests for discovery path logic."""

    def test_default_paths_unix(self):
        """Test default paths on Unix systems."""
        if platform.system() == "Windows":
            pytest.skip("Unix-specific test")

        paths = get_default_discovery_paths()
        assert len(paths) >= 1

        # Should include home directory path
        home_path = Path.home() / ".cmdop" / "agent.info"
        assert home_path in paths

    def test_env_override(self):
        """Test environment variable override."""
        with patch.dict(os.environ, {"CMDOP_AGENT_INFO": "/custom/path"}):
            paths = get_default_discovery_paths()
            assert paths[0] == Path("/custom/path")


class TestReadDiscoveryFile:
    """Tests for reading discovery file."""

    def test_read_valid_file(self):
        """Test reading valid discovery file."""
        data = {
            "version": "1.0.30",
            "pid": os.getpid(),  # Use current process
            "transport": "unix",
            "address": "/tmp/test.sock",
            "started_at": "2024-01-15T10:30:00Z",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            info = read_discovery_file(path)
            assert info is not None
            assert info.version == "1.0.30"
            assert info.pid == os.getpid()
        finally:
            path.unlink()

    def test_read_missing_file(self):
        """Test reading non-existent file."""
        path = Path("/nonexistent/file.json")
        info = read_discovery_file(path)
        assert info is None

    def test_read_invalid_json(self):
        """Test reading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json")
            path = Path(f.name)

        try:
            info = read_discovery_file(path)
            assert info is None
        finally:
            path.unlink()


class TestDiscoverAgent:
    """Tests for agent discovery."""

    def test_no_agent(self):
        """Test when no agent is running."""
        result = discover_agent(custom_paths=["/nonexistent/path"], use_defaults=False)
        assert not result.found
        assert result.error is not None

    def test_stale_file(self):
        """Test detection of stale discovery file."""
        # Create discovery file with non-existent PID
        data = {
            "version": "1.0.30",
            "pid": 999999,  # Non-existent PID
            "transport": "unix",
            "address": "/tmp/nonexistent.sock",
            "started_at": "2024-01-15T10:30:00Z",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            result = discover_agent(custom_paths=[path], verify_alive=True)
            assert not result.found
            assert "stale" in result.error.lower() or "not running" in result.error.lower()
        finally:
            path.unlink()


class TestRequireAgent:
    """Tests for require_agent function."""

    def test_raises_not_running(self):
        """Test that AgentNotRunningError is raised when no agent."""
        with pytest.raises(AgentNotRunningError):
            require_agent(custom_paths=["/nonexistent/path"], use_defaults=False)


class TestCheckProcessRunning:
    """Tests for process checking."""

    def test_current_process(self):
        """Test that current process is detected as running."""
        assert check_process_running(os.getpid()) is True

    def test_nonexistent_process(self):
        """Test that non-existent process is detected."""
        # Use a very high PID that's unlikely to exist
        assert check_process_running(999999999) is False


class TestFileTokenAuth:
    """Tests for file token authentication."""

    def test_read_token(self):
        """Test reading token from file."""
        token = "a" * 64  # 64 char token

        with tempfile.NamedTemporaryFile(mode="w", suffix=".token", delete=False) as f:
            f.write(token)
            path = Path(f.name)

        # Set secure permissions
        if platform.system() != "Windows":
            os.chmod(path, 0o600)

        try:
            auth = FileTokenAuth(path)
            assert auth.token == token
            assert len(auth.metadata()) == 1
            assert auth.metadata()[0][0] == "authorization"
            assert token in auth.metadata()[0][1]
        finally:
            path.unlink()

    def test_missing_file(self):
        """Test error when token file doesn't exist."""
        from cmdop.exceptions import AuthenticationError

        with pytest.raises(AuthenticationError) as exc:
            FileTokenAuth("/nonexistent/token")
        assert "not found" in str(exc.value).lower()

    def test_short_token(self):
        """Test error when token is too short."""
        from cmdop.exceptions import AuthenticationError

        with tempfile.NamedTemporaryFile(mode="w", suffix=".token", delete=False) as f:
            f.write("short")  # Less than 32 chars
            path = Path(f.name)

        try:
            with pytest.raises(AuthenticationError) as exc:
                FileTokenAuth(path)
            assert "too short" in str(exc.value).lower()
        finally:
            path.unlink()

    def test_insecure_permissions_warning(self):
        """Test warning for insecure permissions."""
        if platform.system() == "Windows":
            pytest.skip("Unix-specific test")

        token = "a" * 64

        with tempfile.NamedTemporaryFile(mode="w", suffix=".token", delete=False) as f:
            f.write(token)
            path = Path(f.name)

        # Set insecure permissions (world-readable)
        os.chmod(path, 0o644)

        try:
            with pytest.warns(SecurityWarning):
                FileTokenAuth(path)
        finally:
            path.unlink()


class TestSupportsPeercred:
    """Tests for platform detection."""

    def test_unix_support(self):
        """Test SO_PEERCRED support detection."""
        result = supports_peercred()

        if platform.system() in ("Linux", "Darwin"):
            assert result is True
        else:
            assert result is False


class TestLocalTransport:
    """Tests for LocalTransport class."""

    def test_mode(self):
        """Test transport mode."""
        info = AgentInfo(
            version="1.0.0",
            pid=12345,
            transport=TransportType.UNIX_SOCKET,
            address="/tmp/test.sock",
            token_path=None,
            started_at=datetime.now(timezone.utc),
        )
        transport = LocalTransport(agent_info=info)
        assert transport.mode == "local"

    def test_from_address(self):
        """Test creating transport from address."""
        transport = LocalTransport.from_address(
            address="/tmp/test.sock",
            transport_type=TransportType.UNIX_SOCKET,
        )
        assert transport.address == "/tmp/test.sock"
        assert transport.transport_type == TransportType.UNIX_SOCKET

    def test_repr(self):
        """Test string representation."""
        info = AgentInfo(
            version="1.0.0",
            pid=12345,
            transport=TransportType.UNIX_SOCKET,
            address="/tmp/test.sock",
            token_path=None,
            started_at=datetime.now(timezone.utc),
        )
        transport = LocalTransport(agent_info=info)
        repr_str = repr(transport)

        assert "LocalTransport" in repr_str
        assert "unix" in repr_str
        assert "/tmp/test.sock" in repr_str

    def test_discover_no_agent(self):
        """Test discover raises when no agent."""
        with pytest.raises(AgentNotRunningError):
            LocalTransport.discover(custom_paths=["/nonexistent/path"], use_defaults=False)


class TestLocalAuthMetadata:
    """Tests for local auth metadata generation."""

    def test_unix_no_metadata(self):
        """Test that Unix socket auth returns no explicit metadata."""
        if platform.system() == "Windows":
            pytest.skip("Unix-specific test")

        # On Unix with SO_PEERCRED, no explicit auth needed
        metadata = get_local_auth_metadata(token_path=None)
        assert metadata == []

    def test_with_token_path(self):
        """Test metadata generation with token path."""
        token = "a" * 64

        with tempfile.NamedTemporaryFile(mode="w", suffix=".token", delete=False) as f:
            f.write(token)
            path = Path(f.name)

        if platform.system() != "Windows":
            os.chmod(path, 0o600)

        try:
            metadata = get_local_auth_metadata(token_path=path)
            assert len(metadata) == 1
            assert metadata[0][0] == "authorization"
        finally:
            path.unlink()
