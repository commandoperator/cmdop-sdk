"""
Terminal session models for CMDOP SDK.

Models for creating, managing, and streaming terminal sessions.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class SessionStatus(str, Enum):
    """
    Terminal session connection status.

    Maps to proto SessionStatus from common_types.proto.
    """

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PENDING = "pending"
    BACKGROUND = "background"
    ERROR = "error"

    @classmethod
    def is_active(cls, status: str) -> bool:
        """Check if status indicates an active session."""
        return status == cls.CONNECTED.value


class SessionState(str, Enum):
    """Terminal session lifecycle state."""

    CREATING = "creating"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    ERROR = "error"


class SessionMode(str, Enum):
    """Session access mode."""

    EXCLUSIVE = "exclusive"  # Single owner, full control
    SHARED = "shared"  # Multiple viewers, single writer
    READONLY = "readonly"  # View only, no input


class SignalType(str, Enum):
    """Unix signals for terminal control."""

    SIGINT = "SIGINT"  # Ctrl+C (2)
    SIGTERM = "SIGTERM"  # Terminate (15)
    SIGKILL = "SIGKILL"  # Force kill (9)
    SIGSTOP = "SIGSTOP"  # Suspend (19)
    SIGCONT = "SIGCONT"  # Resume (18)
    SIGHUP = "SIGHUP"  # Hangup (1)


class CreateSessionRequest(BaseModel):
    """Request to create new terminal session."""

    model_config = ConfigDict(extra="forbid")

    shell: str = "/bin/bash"
    """Shell executable path."""

    cols: Annotated[int, Field(ge=10, le=500)] = 80
    """Terminal width in columns."""

    rows: Annotated[int, Field(ge=5, le=200)] = 24
    """Terminal height in rows."""

    env: dict[str, str] = Field(default_factory=dict)
    """Additional environment variables."""

    working_dir: str | None = None
    """Initial working directory. None = home dir."""

    mode: SessionMode = SessionMode.EXCLUSIVE
    """Session access mode."""


class SessionInfo(BaseModel):
    """Terminal session information."""

    model_config = ConfigDict(extra="forbid")

    session_id: str
    """Unique session UUID."""

    state: SessionState
    """Current session state."""

    mode: SessionMode
    """Session access mode."""

    shell: str
    """Shell executable path."""

    pid: int | None = None
    """Shell process ID (if active)."""

    cols: int
    """Current terminal width."""

    rows: int
    """Current terminal height."""

    working_dir: str | None = None
    """Current working directory."""

    created_at: datetime
    """Session creation timestamp."""

    connected_clients: int = 1
    """Number of attached clients."""


class ResizeRequest(BaseModel):
    """Request to resize terminal window."""

    model_config = ConfigDict(extra="forbid")

    cols: Annotated[int, Field(ge=10, le=500)]
    """New terminal width in columns."""

    rows: Annotated[int, Field(ge=5, le=200)]
    """New terminal height in rows."""


class OutputChunk(BaseModel):
    """Chunk of terminal output from stream."""

    model_config = ConfigDict(extra="forbid")

    session_id: str
    """Source session UUID."""

    data: bytes
    """Raw output bytes from PTY."""

    timestamp: datetime
    """When output was captured."""

    @property
    def text(self) -> str:
        """Decode data as UTF-8 string."""
        return self.data.decode("utf-8", errors="replace")

    def __str__(self) -> str:
        return self.text


class HistoryRequest(BaseModel):
    """Request terminal output history."""

    model_config = ConfigDict(extra="forbid")

    lines: Annotated[int, Field(ge=1, le=10000)] = 1000
    """Number of lines to retrieve."""

    offset: Annotated[int, Field(ge=0)] = 0
    """Start offset for pagination."""


class HistoryResponse(BaseModel):
    """Terminal output history response."""

    model_config = ConfigDict(extra="forbid")

    session_id: str
    """Session UUID."""

    data: bytes
    """Historical output data."""

    total_lines: int
    """Total lines available."""

    has_more: bool
    """More lines available for pagination."""


class SessionListItem(BaseModel):
    """Session info for listing (v2.14.0)."""

    model_config = ConfigDict(extra="forbid")

    session_id: str
    """Session UUID."""

    machine_hostname: str
    """Machine hostname."""

    machine_name: str
    """Machine display name."""

    status: str
    """Session status: connected, disconnected, grace_period."""

    os: str
    """Operating system: macos, linux, windows."""

    agent_version: str
    """Agent version string."""

    heartbeat_age_seconds: int
    """Seconds since last heartbeat."""

    has_shell: bool
    """Whether machine has shell access."""

    shell: str
    """Shell path (/bin/bash, etc.)."""

    working_directory: str
    """Current working directory."""

    connected_at: datetime | None = None
    """Connection timestamp."""

    @property
    def is_alive(self) -> bool:
        """Check if session is alive (connected and heartbeat < 60s)."""
        return self.status == "connected" and self.heartbeat_age_seconds < 60


class SessionListResponse(BaseModel):
    """Response from list_sessions (v2.14.0)."""

    model_config = ConfigDict(extra="forbid")

    sessions: list[SessionListItem]
    """List of sessions."""

    total: int
    """Total count for pagination."""

    workspace_name: str
    """Workspace name."""
