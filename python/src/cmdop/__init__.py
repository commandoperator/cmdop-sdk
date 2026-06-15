"""cmdop — async-first Python SDK for CMDOP.

A **thin** client: it spawns the baked-in ``cmdop-core`` Go binary and speaks a
protobuf-length-delimited ``Envelope`` protocol over its stdio. All the relay
logic (REST, the ``/ask`` SSE stream, pin/confirm side-channels, retries, error
mapping) lives in the Go core; this package is the typed surface + transport.

    from cmdop import Client

    async with Client(token="...") as c:
        page = await c.machines.list(presence="online")
        text = await c.machines.ask(machine_id, "uptime").collect()
"""

from __future__ import annotations

from cmdop import errors, types
from cmdop.client import Client
from cmdop.config import ClientConfig
from cmdop.errors import (
    AgentStreamError,
    AuthError,
    CmdopError,
    ConflictError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    TimeoutError,
    UnavailableError,
    ValidationError,
    map_core_error,
)
from cmdop.streaming import (
    AskFrame,
    ConfirmRequiredFrame,
    DoneFrame,
    ErrorFrame,
    EventFrame,
    FrameStream,
    PinDeniedFrame,
    PinRequiredFrame,
    UnknownFrame,
)

# semver (X.Y.Z, starts 0.1.0). Python + Node ship in lockstep.
__version__ = "1.0.1"

# The streaming object machines.ask() returns. Aliased to mirror the archived
# wrapper's ``AskStream`` name (the type the SDK's docs/examples reference).
AskStream = FrameStream

__all__ = [
    "AgentStreamError",
    "AskFrame",
    "AskStream",
    "AuthError",
    "Client",
    "ClientConfig",
    "CmdopError",
    "ConflictError",
    "ConfirmRequiredFrame",
    "ConnectionError",
    "DoneFrame",
    "ErrorFrame",
    "EventFrame",
    "FrameStream",
    "NotFoundError",
    "PermissionError",
    "PinDeniedFrame",
    "PinRequiredFrame",
    "RateLimitError",
    "ServerError",
    "TimeoutError",
    "UnavailableError",
    "UnknownFrame",
    "ValidationError",
    "__version__",
    "errors",
    "map_core_error",
    "types",
]
