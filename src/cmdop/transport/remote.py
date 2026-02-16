"""
Remote transport for CMDOP SDK.

Connects to CMDOP cloud relay via gRPC over TLS.
Uses API key authentication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import grpc
import grpc.aio

from cmdop.transport.base import BaseTransport

if TYPE_CHECKING:
    from cmdop.models.config import ConnectionConfig


# Default cloud relay endpoint
DEFAULT_SERVER = "grpc.cmdop.com:443"


class RemoteTransport(BaseTransport):
    """
    Remote transport via CMDOP cloud relay.

    Connects to grpc.cmdop.com (or custom server) using TLS.
    Authenticates with API key in request metadata.

    Args:
        api_key: CMDOP API key (cmd_xxx)
        server: Cloud relay endpoint. Default: grpc.cmdop.com:443
        agent_id: Target agent UUID. Uses default agent if None.
        config: Connection configuration.
        insecure: Use insecure connection (no TLS). For local dev only.

    Example:
        >>> transport = RemoteTransport(api_key="cmd_xxx")
        >>> channel = transport.channel
        >>> stub = TerminalServiceStub(channel)
    """

    def __init__(
        self,
        api_key: str,
        server: str = DEFAULT_SERVER,
        agent_id: str | None = None,
        config: ConnectionConfig | None = None,
        insecure: bool = False,
    ) -> None:
        super().__init__(config)
        self._api_key = api_key
        self._server = server
        self._agent_id = agent_id
        self._insecure = insecure

        # Validate API key format
        valid_prefixes = ("cmdop_live_", "cmdop_test_", "cmd_")
        if not api_key.startswith(valid_prefixes):
            raise ValueError(
                f"API key must start with one of: {', '.join(valid_prefixes)}"
            )

    @property
    def mode(self) -> str:
        """Transport mode identifier."""
        return "remote"

    @property
    def server(self) -> str:
        """Get server endpoint."""
        return self._server

    @property
    def agent_id(self) -> str | None:
        """Get target agent ID."""
        return self._agent_id

    def _get_metadata(self) -> list[tuple[str, str]]:
        """Get authentication metadata for requests."""
        metadata = [("authorization", f"Bearer {self._api_key}")]
        if self._agent_id:
            metadata.append(("x-cmdop-agent-id", self._agent_id))
        return metadata

    def _create_channel(self) -> grpc.Channel:
        """Create synchronous gRPC channel."""
        options = self._config.grpc_options

        if self._insecure:
            # Insecure channel for local development
            return grpc.insecure_channel(
                target=self._server,
                options=options,
            )

        # Secure channel with TLS
        credentials = grpc.ssl_channel_credentials()
        return grpc.secure_channel(
            target=self._server,
            credentials=credentials,
            options=options,
        )

    def _create_async_channel(self) -> grpc.aio.Channel:
        """Create asynchronous gRPC channel."""
        options = self._config.grpc_options

        if self._insecure:
            # Insecure channel for local development
            return grpc.aio.insecure_channel(
                target=self._server,
                options=options,
            )

        # Secure channel with TLS
        credentials = grpc.ssl_channel_credentials()
        return grpc.aio.secure_channel(
            target=self._server,
            credentials=credentials,
            options=options,
        )

    def __repr__(self) -> str:
        agent = f" agent={self._agent_id}" if self._agent_id else ""
        return f"<RemoteTransport server={self._server}{agent} state={self.state.value}>"


def create_remote_transport(
    api_key: str,
    server: str = DEFAULT_SERVER,
    agent_id: str | None = None,
    config: ConnectionConfig | None = None,
) -> RemoteTransport:
    """
    Factory function to create remote transport.

    Args:
        api_key: CMDOP API key
        server: Cloud relay endpoint
        agent_id: Target agent UUID
        config: Connection configuration

    Returns:
        Configured RemoteTransport instance
    """
    return RemoteTransport(
        api_key=api_key,
        server=server,
        agent_id=agent_id,
        config=config,
    )
