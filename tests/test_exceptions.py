"""
Tests for CMDOP SDK exceptions.
"""

import pytest

from cmdop.exceptions import (
    AgentNotRunningError,
    AgentOfflineError,
    AuthenticationError,
    CMDOPError,
    ConnectionTimeoutError,
    FeatureNotAvailableError,
    FileNotFoundError,
    FilePermissionError,
    FileTooLargeError,
    InvalidAPIKeyError,
    PermissionDeniedError,
    RateLimitError,
    SessionClosedError,
    SessionNotFoundError,
    StalePortFileError,
)


class TestCMDOPError:
    """Tests for base CMDOPError."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = CMDOPError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"

    def test_error_with_cause(self):
        """Test error with cause (cause is stored but not shown in str)."""
        cause = ValueError("Original error")
        error = CMDOPError("Wrapped error", cause=cause)
        # Cause is stored internally but not shown in __str__ (suppressed chain display)
        assert error._original_cause is cause
        assert str(error) == "Wrapped error"


class TestConnectionErrors:
    """Tests for connection-related exceptions."""

    def test_agent_not_running(self):
        """Test AgentNotRunningError."""
        error = AgentNotRunningError()
        assert "not running" in str(error).lower()

    def test_stale_port_file(self):
        """Test StalePortFileError."""
        error = StalePortFileError("/tmp/agent.info")
        assert error.discovery_path == "/tmp/agent.info"
        assert "/tmp/agent.info" in str(error)

    def test_connection_timeout(self):
        """Test ConnectionTimeoutError."""
        error = ConnectionTimeoutError(30.0)
        assert error.timeout_seconds == 30.0
        assert "30" in str(error)


class TestAuthenticationErrors:
    """Tests for authentication exceptions."""

    def test_invalid_api_key(self):
        """Test InvalidAPIKeyError."""
        error = InvalidAPIKeyError("Key rejected")
        assert "Key rejected" in str(error)

    def test_permission_denied_basic(self):
        """Test basic PermissionDeniedError."""
        error = PermissionDeniedError("Access denied")
        assert "Access denied" in str(error)

    def test_permission_denied_with_uids(self):
        """Test PermissionDeniedError with UIDs."""
        error = PermissionDeniedError(
            "UID mismatch",
            agent_uid=1000,
            caller_uid=1001,
        )
        assert error.agent_uid == 1000
        assert error.caller_uid == 1001
        assert "1000" in str(error)
        assert "1001" in str(error)


class TestAgentErrors:
    """Tests for agent-related exceptions."""

    def test_agent_offline_basic(self):
        """Test basic AgentOfflineError."""
        error = AgentOfflineError()
        assert "offline" in str(error).lower()

    def test_agent_offline_with_id(self):
        """Test AgentOfflineError with agent ID."""
        error = AgentOfflineError("agent-123")
        assert error.agent_id == "agent-123"
        assert "agent-123" in str(error)

    def test_feature_not_available(self):
        """Test FeatureNotAvailableError."""
        error = FeatureNotAvailableError("tunnels", "local")
        assert error.feature == "tunnels"
        assert error.mode == "local"
        assert "tunnels" in str(error)
        assert "local" in str(error)


class TestSessionErrors:
    """Tests for session-related exceptions."""

    def test_session_not_found(self):
        """Test SessionNotFoundError."""
        error = SessionNotFoundError("sess-123")
        assert error.session_id == "sess-123"
        assert "sess-123" in str(error)

    def test_session_closed(self):
        """Test SessionClosedError."""
        error = SessionClosedError("sess-456")
        assert error.session_id == "sess-456"


class TestFileErrors:
    """Tests for file-related exceptions."""

    def test_file_not_found(self):
        """Test FileNotFoundError."""
        error = FileNotFoundError("/path/to/file")
        assert error.path == "/path/to/file"
        assert "/path/to/file" in str(error)

    def test_file_permission(self):
        """Test FilePermissionError."""
        error = FilePermissionError("/etc/passwd", "write")
        assert error.path == "/etc/passwd"
        assert error.operation == "write"

    def test_file_too_large(self):
        """Test FileTooLargeError."""
        error = FileTooLargeError("/large/file", 100_000_000, 50_000_000)
        assert error.size_bytes == 100_000_000
        assert error.max_bytes == 50_000_000


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_basic(self):
        """Test basic RateLimitError."""
        error = RateLimitError()
        assert "rate limit" in str(error).lower()

    def test_with_retry_after(self):
        """Test RateLimitError with retry_after."""
        error = RateLimitError(retry_after_seconds=60.0)
        assert error.retry_after_seconds == 60.0
        assert "60" in str(error)
