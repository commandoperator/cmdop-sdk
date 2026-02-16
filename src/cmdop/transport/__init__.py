"""
CMDOP Transport Layer.

Abstracts gRPC channel creation for different connection modes.
Provides BaseTransport interface and concrete implementations.

Transports:
- RemoteTransport: Cloud relay via gRPC/TLS
- LocalTransport: Direct IPC via Unix socket or Named Pipe
"""

from cmdop.transport.base import BaseTransport, TransportState
from cmdop.transport.discovery import (
    AgentInfo,
    DiscoveryResult,
    TransportType,
    discover_agent,
    require_agent,
)
from cmdop.transport.local import LocalTransport, create_local_transport
from cmdop.transport.remote import RemoteTransport, create_remote_transport

__all__ = [
    # Base
    "BaseTransport",
    "TransportState",
    # Remote
    "RemoteTransport",
    "create_remote_transport",
    # Local
    "LocalTransport",
    "create_local_transport",
    # Discovery
    "AgentInfo",
    "DiscoveryResult",
    "TransportType",
    "discover_agent",
    "require_agent",
]
