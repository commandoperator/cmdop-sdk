"""
Terminal service for CMDOP SDK.

Provides terminal session management: create, attach, send input, resize, close.
Supports both sync and async patterns.

Streaming:
    >>> async with client.terminal.stream() as stream:
    ...     stream.on_output(lambda data: print(data.decode(), end=""))
    ...     await stream.send_input(b"ls -la\\n")

TUI Support:
    >>> from cmdop.services.terminal.tui import ssh_connect
    >>> await ssh_connect("my-server", api_key="xxx")
"""

from cmdop.services.terminal.service import (
    AsyncTerminalService,
    TerminalService,
)

__all__ = [
    "TerminalService",
    "AsyncTerminalService",
]
