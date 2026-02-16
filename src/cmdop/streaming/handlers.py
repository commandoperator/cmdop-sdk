"""
Message handlers for streaming.

Provides typed handlers for different message types.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Coroutine

# Type aliases for handler functions
OutputHandler = Callable[[bytes], Coroutine[Any, Any, None] | None]
"""Handler for terminal output. Receives raw bytes."""

StatusHandler = Callable[[str, str], Coroutine[Any, Any, None] | None]
"""Handler for status changes. Receives (old_status, new_status)."""

ErrorHandler = Callable[[str, str, bool], Coroutine[Any, Any, None] | None]
"""Handler for errors. Receives (error_code, message, is_fatal)."""

CommandCompleteHandler = Callable[[str, int, int], Coroutine[Any, Any, None] | None]
"""Handler for command completion. Receives (command_id, exit_code, duration_ms)."""

HistoryHandler = Callable[[list[str], int], Coroutine[Any, Any, None] | None]
"""Handler for history data. Receives (commands, total)."""

DisconnectHandler = Callable[[str], Coroutine[Any, Any, None] | None]
"""Handler for disconnection. Receives reason."""


@dataclass
class OutputData:
    """Terminal output data."""

    data: bytes
    """Raw output bytes."""

    is_stderr: bool = False
    """True if from stderr."""

    sequence: int = 0
    """Sequence number for ordering."""

    @property
    def text(self) -> str:
        """Decode output as UTF-8 text."""
        return self.data.decode("utf-8", errors="replace")


@dataclass
class StatusData:
    """Status change data."""

    old_status: str
    """Previous status."""

    new_status: str
    """New status."""

    reason: str = ""
    """Reason for status change."""

    working_directory: str = ""
    """Current working directory."""


@dataclass
class ErrorData:
    """Error report data."""

    error_code: str
    """Error code."""

    message: str
    """Error message."""

    is_fatal: bool = False
    """If true, session will close."""

    can_retry: bool = False
    """If true, operation can be retried."""

    suggestions: list[str] | None = None
    """User-friendly suggestions for resolution."""


@dataclass
class CommandCompleteData:
    """Command completion data."""

    command_id: str
    """Command that completed."""

    exit_code: int
    """Exit code."""

    duration_ms: int
    """Execution time in milliseconds."""


@dataclass
class HistoryData:
    """Shell history data."""

    commands: list[str]
    """List of commands from history."""

    total: int
    """Total count in history file."""

    source: str = ""
    """Source: "bash_history", "zsh_history", etc."""
