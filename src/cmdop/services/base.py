"""
Base service class for CMDOP SDK.

Provides common functionality for all services.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from cmdop.exceptions import from_grpc_error

if TYPE_CHECKING:
    import grpc
    import grpc.aio

    from cmdop.transport.base import BaseTransport

T = TypeVar("T")


class BaseService:
    """
    Base class for all services.

    Provides:
    - Access to transport and channels
    - gRPC error handling
    - Metadata injection for authenticated requests
    """

    def __init__(self, transport: BaseTransport) -> None:
        self._transport = transport

    @property
    def transport(self) -> BaseTransport:
        """Get underlying transport."""
        return self._transport

    @property
    def _channel(self) -> grpc.Channel:
        """Get sync gRPC channel."""
        return self._transport.channel

    @property
    def _async_channel(self) -> grpc.aio.Channel:
        """Get async gRPC channel."""
        return self._transport.async_channel

    @property
    def _metadata(self) -> list[tuple[str, str]]:
        """Get auth metadata for requests."""
        return self._transport.metadata

    @property
    def _timeout(self) -> float:
        """Get default request timeout."""
        return self._transport.config.request_timeout_seconds

    def _handle_error(self, error: Exception) -> Exception:
        """Convert gRPC error to SDK exception."""
        import grpc

        if isinstance(error, grpc.RpcError):
            return from_grpc_error(error)
        return error

    def _call_sync(
        self,
        method: Any,
        request: Any,
        timeout: float | None = None,
    ) -> Any:
        """
        Execute synchronous gRPC call with error handling.

        Args:
            method: gRPC stub method to call
            request: Protobuf request message
            timeout: Request timeout (uses default if None)

        Returns:
            Protobuf response message

        Raises:
            CMDOPError: On gRPC errors
        """
        try:
            return method(
                request,
                metadata=self._metadata,
                timeout=timeout or self._timeout,
            )
        except Exception as e:
            raise self._handle_error(e) from None  # Suppress chain

    async def _call_async(
        self,
        method: Any,
        request: Any,
        timeout: float | None = None,
    ) -> Any:
        """
        Execute asynchronous gRPC call with error handling.

        Args:
            method: gRPC stub method to call
            request: Protobuf request message
            timeout: Request timeout (uses default if None)

        Returns:
            Protobuf response message

        Raises:
            CMDOPError: On gRPC errors
        """
        try:
            return await method(
                request,
                metadata=self._metadata,
                timeout=timeout or self._timeout,
            )
        except Exception as e:
            raise self._handle_error(e) from None  # Suppress chain
