"""
Local transport for CMDOP SDK.

Connects directly to local cmdop_go agent via Unix socket (Linux/macOS)
or Named Pipe (Windows). Provides 30-100x lower latency than cloud relay.
"""

from __future__ import annotations

import platform
from pathlib import Path
from typing import TYPE_CHECKING

import grpc
import grpc.aio

from cmdop.exceptions import AgentNotRunningError
from cmdop.transport.auth import get_local_auth_metadata, supports_peercred
from cmdop.transport.base import BaseTransport
from cmdop.transport.discovery import (
    AgentInfo,
    TransportType,
    discover_agent,
    require_agent,
)

if TYPE_CHECKING:
    from cmdop.models.config import ConnectionConfig


class LocalTransport(BaseTransport):
    """
    Local transport via Unix socket or Named Pipe.

    Connects directly to cmdop_go agent running on the same machine.
    Uses SO_PEERCRED for authentication on Linux, file token on Windows.

    Performance:
    - Latency: <5ms for unary calls (vs 150-300ms via cloud)
    - Throughput: Limited only by local IPC speed
    - No network dependency

    Args:
        agent_info: Agent connection info (from discovery)
        config: Connection configuration
        token_path: Override token path for auth (Windows/containers)

    Example:
        >>> # Auto-discover agent
        >>> transport = LocalTransport.discover()
        >>> channel = transport.channel
        >>>
        >>> # Or with explicit info
        >>> info = AgentInfo(...)
        >>> transport = LocalTransport(agent_info=info)
    """

    def __init__(
        self,
        agent_info: AgentInfo,
        config: ConnectionConfig | None = None,
        token_path: str | Path | None = None,
    ) -> None:
        super().__init__(config)
        self._agent_info = agent_info
        self._token_path = token_path
        self._discovery_path: Path | None = None

    @classmethod
    def discover(
        cls,
        config: ConnectionConfig | None = None,
        custom_paths: list[Path | str] | None = None,
        use_defaults: bool = True,
    ) -> LocalTransport:
        """
        Create transport by auto-discovering local agent.

        Searches for agent discovery file in standard locations
        and verifies agent is responding.

        Args:
            config: Connection configuration
            custom_paths: Additional discovery paths to check
            use_defaults: Whether to include default discovery paths

        Returns:
            Connected LocalTransport

        Raises:
            AgentNotRunningError: No agent found
            StalePortFileError: Discovery file exists but agent dead
        """
        agent_info, discovery_path = require_agent(custom_paths, use_defaults=use_defaults)

        transport = cls(agent_info=agent_info, config=config)
        transport._discovery_path = discovery_path

        return transport

    @classmethod
    def from_address(
        cls,
        address: str,
        transport_type: TransportType = TransportType.UNIX_SOCKET,
        config: ConnectionConfig | None = None,
        token_path: str | Path | None = None,
    ) -> LocalTransport:
        """
        Create transport with explicit address.

        Useful for testing or custom configurations.

        Args:
            address: Socket path, pipe name, or host:port
            transport_type: Type of transport
            config: Connection configuration
            token_path: Path to auth token (for file token auth)

        Returns:
            LocalTransport configured for the address
        """
        from datetime import datetime, timezone

        # Create minimal AgentInfo
        info = AgentInfo(
            version="unknown",
            pid=0,
            transport=transport_type,
            address=address,
            token_path=str(token_path) if token_path else None,
            started_at=datetime.now(timezone.utc),
        )

        return cls(agent_info=info, config=config, token_path=token_path)

    @property
    def mode(self) -> str:
        """Transport mode identifier."""
        return "local"

    @property
    def agent_info(self) -> AgentInfo:
        """Get agent connection info."""
        return self._agent_info

    @property
    def address(self) -> str:
        """Get connection address."""
        return self._agent_info.address

    @property
    def transport_type(self) -> TransportType:
        """Get transport type."""
        return self._agent_info.transport

    @property
    def discovery_path(self) -> Path | None:
        """Get path where agent was discovered."""
        return self._discovery_path

    def _get_metadata(self) -> list[tuple[str, str]]:
        """Get authentication metadata for requests."""
        # Determine token path
        token_path = self._token_path or self._agent_info.token_path

        # On Unix with socket, SO_PEERCRED is used by server
        # so we only need explicit auth for Windows/TCP
        if self._agent_info.transport == TransportType.UNIX_SOCKET:
            if supports_peercred():
                return []  # Server uses SO_PEERCRED

        return get_local_auth_metadata(token_path)

    def _get_target(self) -> str:
        """Get gRPC target string for channel."""
        transport = self._agent_info.transport
        address = self._agent_info.address

        if transport == TransportType.UNIX_SOCKET:
            # Unix socket: prefix with unix:
            return f"unix:{address}"

        elif transport == TransportType.TCP:
            # TCP: use address directly
            return address

        elif transport == TransportType.NAMED_PIPE:
            # Windows named pipe: not directly supported by grpcio
            # Would need custom implementation or TCP fallback
            raise NotImplementedError(
                "Named pipe transport not yet supported. "
                "Use TCP transport on Windows for now."
            )

        raise ValueError(f"Unknown transport type: {transport}")

    def _create_channel(self) -> grpc.Channel:
        """Create synchronous gRPC channel."""
        target = self._get_target()
        options = self._config.grpc_options

        # Local connections don't need TLS
        return grpc.insecure_channel(target, options=options)

    def _create_async_channel(self) -> grpc.aio.Channel:
        """Create asynchronous gRPC channel."""
        target = self._get_target()
        options = self._config.grpc_options

        return grpc.aio.insecure_channel(target, options=options)

    def __repr__(self) -> str:
        transport = self._agent_info.transport.value
        address = self._agent_info.address
        return f"<LocalTransport {transport}:{address} state={self.state.value}>"


def create_local_transport(
    config: ConnectionConfig | None = None,
    discovery_paths: list[Path | str] | None = None,
) -> LocalTransport:
    """
    Factory function to create local transport.

    Convenience wrapper around LocalTransport.discover().

    Args:
        config: Connection configuration
        discovery_paths: Custom paths to check for agent

    Returns:
        Configured LocalTransport instance

    Raises:
        AgentNotRunningError: No agent found
        StalePortFileError: Agent crashed
    """
    return LocalTransport.discover(
        config=config,
        custom_paths=discovery_paths,
    )
