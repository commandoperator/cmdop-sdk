"""
Base types for streaming support.

Defines stream states, events, and callback types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine


class StreamState(str, Enum):
    """Stream connection state."""

    IDLE = "idle"
    """Stream not started."""

    CONNECTING = "connecting"
    """Establishing connection."""

    REGISTERING = "registering"
    """Sending registration message."""

    CONNECTED = "connected"
    """Stream active and ready."""

    RECONNECTING = "reconnecting"
    """Attempting to reconnect after failure."""

    CLOSING = "closing"
    """Graceful shutdown in progress."""

    CLOSED = "closed"
    """Stream closed."""

    ERROR = "error"
    """Stream failed with error."""


class StreamEvent(str, Enum):
    """Stream event types for callbacks."""

    OUTPUT = "output"
    """Terminal output received."""

    STATUS = "status"
    """Session status changed."""

    ERROR = "error"
    """Error occurred."""

    CONNECTED = "connected"
    """Stream connected."""

    DISCONNECTED = "disconnected"
    """Stream disconnected."""

    COMMAND_COMPLETE = "command_complete"
    """Command execution completed."""

    HISTORY = "history"
    """History data received."""

    KEEPALIVE = "keepalive"
    """Keepalive ping/pong."""


# Callback type: async function that receives event data
StreamCallback = Callable[[StreamEvent, Any], Coroutine[Any, Any, None]]


@dataclass
class StreamMetrics:
    """Metrics for stream monitoring."""

    bytes_sent: int = 0
    """Total bytes sent."""

    bytes_received: int = 0
    """Total bytes received."""

    messages_sent: int = 0
    """Total messages sent."""

    messages_received: int = 0
    """Total messages received."""

    keepalive_count: int = 0
    """Number of keepalive pings sent."""

    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """Timestamp of last activity."""

    reconnect_count: int = 0
    """Number of reconnection attempts."""

    errors: int = 0
    """Number of errors encountered."""

    def record_sent(self, size: int) -> None:
        """Record sent message."""
        self.bytes_sent += size
        self.messages_sent += 1
        self.last_activity = datetime.now(timezone.utc)

    def record_received(self, size: int) -> None:
        """Record received message."""
        self.bytes_received += size
        self.messages_received += 1
        self.last_activity = datetime.now(timezone.utc)

    def record_keepalive(self) -> None:
        """Record keepalive ping."""
        self.keepalive_count += 1
        self.last_activity = datetime.now(timezone.utc)

    def record_error(self) -> None:
        """Record error."""
        self.errors += 1

    def record_reconnect(self) -> None:
        """Record reconnection attempt."""
        self.reconnect_count += 1
