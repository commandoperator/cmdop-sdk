"""
Tests for CMDOP SDK Pydantic models.
"""

import pytest
from pydantic import ValidationError

from cmdop.models.config import ConnectionConfig, KeepaliveConfig, RetryConfig
from cmdop.models.files import FileEntry, FileInfo, FileType
from cmdop.models.terminal import (
    CreateSessionRequest,
    ResizeRequest,
    SessionInfo,
    SessionMode,
    SessionState,
)


class TestKeepaliveConfig:
    """Tests for KeepaliveConfig model."""

    def test_defaults(self):
        """Test default values."""
        config = KeepaliveConfig()
        assert config.time_ms == 30_000
        assert config.timeout_ms == 5_000
        assert config.permit_without_calls is True

    def test_custom_values(self):
        """Test custom values."""
        config = KeepaliveConfig(time_ms=30_000, timeout_ms=10_000)
        assert config.time_ms == 30_000
        assert config.timeout_ms == 10_000

    def test_validation_min(self):
        """Test minimum value validation."""
        with pytest.raises(ValidationError):
            KeepaliveConfig(time_ms=100)  # Below minimum

    def test_validation_max(self):
        """Test maximum value validation."""
        with pytest.raises(ValidationError):
            KeepaliveConfig(time_ms=500_000)  # Above maximum

    def test_frozen(self):
        """Test that config is immutable."""
        config = KeepaliveConfig()
        with pytest.raises(ValidationError):
            config.time_ms = 20_000


class TestRetryConfig:
    """Tests for RetryConfig model."""

    def test_defaults(self):
        """Test default values."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.initial_backoff_seconds == 1.0
        assert config.backoff_multiplier == 2.0
        assert config.jitter_fraction == 0.1

    def test_retryable_codes(self):
        """Test default retryable codes."""
        config = RetryConfig()
        assert "UNAVAILABLE" in config.retryable_codes
        assert "RESOURCE_EXHAUSTED" in config.retryable_codes


class TestConnectionConfig:
    """Tests for ConnectionConfig model."""

    def test_defaults(self):
        """Test default values."""
        config = ConnectionConfig()
        assert config.connect_timeout_seconds == 10.0
        assert config.request_timeout_seconds == 30.0
        assert config.max_message_size_mb == 50

    def test_grpc_options(self):
        """Test gRPC options generation."""
        config = ConnectionConfig()
        options = config.grpc_options

        # Should contain keepalive settings
        option_dict = dict(options)
        assert "grpc.keepalive_time_ms" in option_dict
        assert "grpc.max_send_message_length" in option_dict

    def test_nested_config(self):
        """Test nested config objects."""
        config = ConnectionConfig(
            keepalive=KeepaliveConfig(time_ms=5000),
            retry=RetryConfig(max_attempts=5),
        )
        assert config.keepalive.time_ms == 5000
        assert config.retry.max_attempts == 5


class TestCreateSessionRequest:
    """Tests for CreateSessionRequest model."""

    def test_defaults(self):
        """Test default values."""
        request = CreateSessionRequest()
        assert request.shell == "/bin/bash"
        assert request.cols == 80
        assert request.rows == 24
        assert request.mode == SessionMode.EXCLUSIVE

    def test_custom_values(self):
        """Test custom values."""
        request = CreateSessionRequest(
            shell="/bin/zsh",
            cols=120,
            rows=40,
            env={"TERM": "xterm-256color"},
            working_dir="/home/user",
        )
        assert request.shell == "/bin/zsh"
        assert request.cols == 120
        assert request.env["TERM"] == "xterm-256color"

    def test_cols_validation(self):
        """Test columns validation."""
        with pytest.raises(ValidationError):
            CreateSessionRequest(cols=5)  # Below minimum

        with pytest.raises(ValidationError):
            CreateSessionRequest(cols=600)  # Above maximum


class TestResizeRequest:
    """Tests for ResizeRequest model."""

    def test_valid_resize(self):
        """Test valid resize request."""
        request = ResizeRequest(cols=200, rows=50)
        assert request.cols == 200
        assert request.rows == 50

    def test_validation(self):
        """Test validation."""
        with pytest.raises(ValidationError):
            ResizeRequest(cols=5, rows=50)  # cols below min


class TestFileEntry:
    """Tests for FileEntry model."""

    def test_file_entry(self):
        """Test file entry creation."""
        entry = FileEntry(
            name="test.txt",
            path="/home/user/test.txt",
            type=FileType.FILE,
            size=1024,
        )
        assert entry.name == "test.txt"
        assert entry.type == FileType.FILE
        assert entry.is_hidden is False

    def test_hidden_file(self):
        """Test hidden file detection."""
        entry = FileEntry(
            name=".bashrc",
            path="/home/user/.bashrc",
            type=FileType.FILE,
            is_hidden=True,
        )
        assert entry.is_hidden is True


class TestFileType:
    """Tests for FileType enum."""

    def test_values(self):
        """Test enum values."""
        assert FileType.FILE == "file"
        assert FileType.DIRECTORY == "directory"
        assert FileType.SYMLINK == "symlink"


class TestSessionState:
    """Tests for SessionState enum."""

    def test_values(self):
        """Test enum values."""
        assert SessionState.ACTIVE == "active"
        assert SessionState.CLOSED == "closed"
        assert SessionState.CREATING == "creating"
