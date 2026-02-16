"""
Tests for CMDOP SDK Base service class.
"""

from unittest.mock import MagicMock, patch

import grpc
import pytest

from cmdop.services.base import BaseService
from cmdop.exceptions import (
    CMDOPError,
    AgentOfflineError,
    InvalidAPIKeyError,
    SessionNotFoundError,
    RateLimitError,
    ConnectionTimeoutError,
)


class MockChannel:
    """Mock gRPC channel for testing."""
    pass


class MockAsyncChannel:
    """Mock async gRPC channel for testing."""
    pass


class MockConfig:
    """Mock connection config."""

    def __init__(self):
        self.request_timeout_seconds = 30.0


class MockTransport:
    """Mock transport for testing services."""

    def __init__(self):
        self._channel = MockChannel()
        self._async_channel = MockAsyncChannel()
        self._config = MockConfig()
        self._metadata = [("authorization", "Bearer test_token")]
        self._mode = "test"

    @property
    def channel(self):
        return self._channel

    @property
    def async_channel(self):
        return self._async_channel

    @property
    def metadata(self):
        return self._metadata

    @property
    def config(self):
        return self._config

    @property
    def mode(self):
        return self._mode


class MockRpcError(grpc.RpcError):
    """Mock RpcError that can be properly caught."""

    def __init__(self, code, details=""):
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class TestBaseServiceCreation:
    """Test BaseService initialization."""

    def test_service_creation(self):
        """Test service can be created with transport."""
        transport = MockTransport()
        service = BaseService(transport)
        assert service._transport == transport

    def test_transport_property(self):
        """Test transport property."""
        transport = MockTransport()
        service = BaseService(transport)
        assert service.transport == transport

    def test_channel_property(self):
        """Test _channel property returns sync channel."""
        transport = MockTransport()
        service = BaseService(transport)
        assert service._channel == transport.channel

    def test_async_channel_property(self):
        """Test _async_channel property returns async channel."""
        transport = MockTransport()
        service = BaseService(transport)
        assert service._async_channel == transport.async_channel

    def test_metadata_property(self):
        """Test _metadata property returns auth metadata."""
        transport = MockTransport()
        service = BaseService(transport)
        assert service._metadata == [("authorization", "Bearer test_token")]

    def test_timeout_property(self):
        """Test _timeout property returns request timeout."""
        transport = MockTransport()
        service = BaseService(transport)
        assert service._timeout == 30.0


class TestBaseServiceCallSync:
    """Test BaseService._call_sync method."""

    def test_call_sync_success(self):
        """Test successful sync call."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_method = MagicMock()
        mock_method.return_value = "response"

        mock_request = MagicMock()

        result = service._call_sync(mock_method, mock_request)

        assert result == "response"
        mock_method.assert_called_once_with(
            mock_request,
            metadata=[("authorization", "Bearer test_token")],
            timeout=30.0,
        )

    def test_call_sync_custom_timeout(self):
        """Test sync call with custom timeout."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_method = MagicMock()
        mock_method.return_value = "response"

        mock_request = MagicMock()

        result = service._call_sync(mock_method, mock_request, timeout=60.0)

        mock_method.assert_called_once_with(
            mock_request,
            metadata=[("authorization", "Bearer test_token")],
            timeout=60.0,
        )

    def test_call_sync_grpc_error_unauthenticated(self):
        """Test sync call handles UNAUTHENTICATED error."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.UNAUTHENTICATED, "Invalid API key")

        mock_method = MagicMock()
        mock_method.side_effect = mock_error

        mock_request = MagicMock()

        with pytest.raises(InvalidAPIKeyError):
            service._call_sync(mock_method, mock_request)

    def test_call_sync_grpc_error_unavailable(self):
        """Test sync call handles UNAVAILABLE error."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.UNAVAILABLE, "Service unavailable")

        mock_method = MagicMock()
        mock_method.side_effect = mock_error

        mock_request = MagicMock()

        with pytest.raises(AgentOfflineError):
            service._call_sync(mock_method, mock_request)

    def test_call_sync_grpc_error_not_found(self):
        """Test sync call handles NOT_FOUND error."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.NOT_FOUND, "Session not found")

        mock_method = MagicMock()
        mock_method.side_effect = mock_error

        mock_request = MagicMock()

        with pytest.raises(SessionNotFoundError):
            service._call_sync(mock_method, mock_request)

    def test_call_sync_grpc_error_resource_exhausted(self):
        """Test sync call handles RESOURCE_EXHAUSTED error."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.RESOURCE_EXHAUSTED, "Rate limit exceeded")

        mock_method = MagicMock()
        mock_method.side_effect = mock_error

        mock_request = MagicMock()

        with pytest.raises(RateLimitError):
            service._call_sync(mock_method, mock_request)

    def test_call_sync_grpc_error_deadline_exceeded(self):
        """Test sync call handles DEADLINE_EXCEEDED error."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.DEADLINE_EXCEEDED, "Request timeout")

        mock_method = MagicMock()
        mock_method.side_effect = mock_error

        mock_request = MagicMock()

        with pytest.raises(ConnectionTimeoutError):
            service._call_sync(mock_method, mock_request)

    def test_call_sync_non_grpc_error(self):
        """Test sync call re-raises non-gRPC errors."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_method = MagicMock()
        mock_method.side_effect = ValueError("Some error")

        mock_request = MagicMock()

        with pytest.raises(ValueError):
            service._call_sync(mock_method, mock_request)


class TestBaseServiceCallAsync:
    """Test BaseService._call_async method."""

    @pytest.mark.asyncio
    async def test_call_async_success(self):
        """Test successful async call."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_request = MagicMock()

        async def async_method(*args, **kwargs):
            return "async_response"

        result = await service._call_async(async_method, mock_request)

        assert result == "async_response"

    @pytest.mark.asyncio
    async def test_call_async_grpc_error(self):
        """Test async call handles gRPC errors."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.UNAUTHENTICATED, "Invalid API key")

        mock_request = MagicMock()

        async def failing_method(*args, **kwargs):
            raise mock_error

        with pytest.raises(InvalidAPIKeyError):
            await service._call_async(failing_method, mock_request)


class TestBaseServiceHandleError:
    """Test BaseService._handle_error method."""

    def test_handle_grpc_error(self):
        """Test _handle_error converts gRPC errors."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.UNAUTHENTICATED, "Invalid key")

        result = service._handle_error(mock_error)

        assert isinstance(result, InvalidAPIKeyError)

    def test_handle_non_grpc_error(self):
        """Test _handle_error returns non-gRPC errors as-is."""
        transport = MockTransport()
        service = BaseService(transport)

        original_error = ValueError("test error")

        result = service._handle_error(original_error)

        assert result is original_error

    def test_handle_unavailable_error(self):
        """Test handling UNAVAILABLE status."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.UNAVAILABLE, "Agent offline")

        result = service._handle_error(mock_error)

        assert isinstance(result, AgentOfflineError)

    def test_handle_resource_exhausted_error(self):
        """Test handling RESOURCE_EXHAUSTED status."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.RESOURCE_EXHAUSTED, "Too many requests")

        result = service._handle_error(mock_error)

        assert isinstance(result, RateLimitError)

    def test_handle_deadline_exceeded_error(self):
        """Test handling DEADLINE_EXCEEDED status."""
        transport = MockTransport()
        service = BaseService(transport)

        mock_error = MockRpcError(grpc.StatusCode.DEADLINE_EXCEEDED, "Timeout")

        result = service._handle_error(mock_error)

        assert isinstance(result, ConnectionTimeoutError)
