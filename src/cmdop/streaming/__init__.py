"""
Streaming support for CMDOP SDK.

Provides bidirectional gRPC streaming for terminal sessions.

Usage:
    >>> from cmdop import AsyncCMDOPClient
    >>>
    >>> async with AsyncCMDOPClient.local() as client:
    ...     stream = await client.terminal.stream()
    ...     stream.on_output(lambda data: print(data.decode(), end=""))
    ...     await stream.send_input(b"ls -la\\n")
    ...     await asyncio.sleep(1)
    ...     await stream.close()
"""

from cmdop.streaming.base import (
    StreamCallback,
    StreamEvent,
    StreamState,
)
from cmdop.streaming.handlers import (
    OutputHandler,
    StatusHandler,
)
from cmdop.streaming.terminal import (
    TerminalStream,
)

__all__ = [
    # Base types
    "StreamState",
    "StreamEvent",
    "StreamCallback",
    # Handlers
    "OutputHandler",
    "StatusHandler",
    # Terminal
    "TerminalStream",
]
