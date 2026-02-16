"""
Base transport interface for CMDOP SDK.

Defines abstract interface that all transports must implement.
Supports both sync and async patterns.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import grpc
    import grpc.aio

    from cmdop.models.config import ConnectionConfig


class TransportState(str, Enum):
    """Transport connection state."""

    IDLE = "idle"
    CONNECTING = "connecting"
    READY = "ready"
    TRANSIENT_FAILURE = "transient_failure"
    SHUTDOWN = "shutdown"


class BaseTransport(ABC):
    """
    Abstract base class for all transports.

    Transports are responsible for:
    - Creating and managing gRPC channels
    - Authentication (API keys, tokens, SO_PEERCRED)
    - Connection lifecycle (connect, reconnect, close)
    - Health monitoring

    Subclasses must implement:
    - _create_channel(): Create the underlying gRPC channel
    - _get_metadata(): Return auth metadata for requests
    - mode: Return transport mode name
    """

    def __init__(self, config: ConnectionConfig | None = None) -> None:
        from cmdop.models.config import DEFAULT_CONFIG

        self._config = config or DEFAULT_CONFIG
        self._channel: grpc.Channel | None = None
        self._async_channel: grpc.aio.Channel | None = None
        self._state = TransportState.IDLE

    @property
    def config(self) -> ConnectionConfig:
        """Get transport configuration."""
        return self._config

    @property
    def state(self) -> TransportState:
        """Get current transport state."""
        return self._state

    @property
    def is_connected(self) -> bool:
        """Check if transport is connected and ready."""
        return self._state == TransportState.READY

    @property
    @abstractmethod
    def mode(self) -> str:
        """Get transport mode name (e.g., 'remote', 'local')."""
        ...

    @abstractmethod
    def _create_channel(self) -> grpc.Channel:
        """Create synchronous gRPC channel. Subclasses must implement."""
        ...

    @abstractmethod
    def _create_async_channel(self) -> grpc.aio.Channel:
        """Create asynchronous gRPC channel. Subclasses must implement."""
        ...

    @abstractmethod
    def _get_metadata(self) -> list[tuple[str, str]]:
        """Get authentication metadata for requests."""
        ...

    def get_channel(self) -> grpc.Channel:
        """
        Get or create synchronous gRPC channel.

        Returns:
            Connected gRPC channel.

        Raises:
            ConnectionError: If connection fails.
        """
        if self._channel is None:
            self._state = TransportState.CONNECTING
            try:
                self._channel = self._create_channel()
                self._state = TransportState.READY
            except Exception as e:
                self._state = TransportState.TRANSIENT_FAILURE
                raise ConnectionError(f"Failed to create channel: {e}") from e
        return self._channel

    def get_async_channel(self) -> grpc.aio.Channel:
        """
        Get or create asynchronous gRPC channel.

        Returns:
            Connected async gRPC channel.

        Raises:
            ConnectionError: If connection fails.
        """
        if self._async_channel is None:
            self._state = TransportState.CONNECTING
            try:
                self._async_channel = self._create_async_channel()
                self._state = TransportState.READY
            except Exception as e:
                self._state = TransportState.TRANSIENT_FAILURE
                raise ConnectionError(f"Failed to create async channel: {e}") from e
        return self._async_channel

    @property
    def channel(self) -> grpc.Channel:
        """Alias for get_channel()."""
        return self.get_channel()

    @property
    def async_channel(self) -> grpc.aio.Channel:
        """Alias for get_async_channel()."""
        return self.get_async_channel()

    @property
    def metadata(self) -> list[tuple[str, str]]:
        """Get authentication metadata."""
        return self._get_metadata()

    def close(self) -> None:
        """Close transport and release resources."""
        if self._channel is not None:
            self._channel.close()
            self._channel = None
        if self._async_channel is not None:
            # Note: async channel should be closed with await
            # This is a sync fallback
            self._async_channel.close()
            self._async_channel = None
        self._state = TransportState.SHUTDOWN

    async def aclose(self) -> None:
        """Async close transport."""
        if self._async_channel is not None:
            await self._async_channel.close()
            self._async_channel = None
        if self._channel is not None:
            self._channel.close()
            self._channel = None
        self._state = TransportState.SHUTDOWN

    def __enter__(self) -> BaseTransport:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> BaseTransport:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.aclose()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} mode={self.mode} state={self.state.value}>"
