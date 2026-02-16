"""
Tests for CMDOP SDK Terminal service.

Tests verify the service layer logic by mocking the underlying gRPC calls.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from cmdop.models.terminal import (
    HistoryResponse,
    SessionInfo,
    SessionMode,
    SessionState,
    SignalType,
)


class MockChannel:
    """Mock gRPC channel for testing."""
    pass


class MockTransport:
    """Mock transport for testing services."""

    def __init__(self):
        self._channel = MockChannel()
        self._config = MagicMock()
        self._config.request_timeout_seconds = 30.0
        self._mode = "test"

    @property
    def channel(self):
        return self._channel

    @property
    def async_channel(self):
        return self._channel

    @property
    def metadata(self):
        return [("authorization", "Bearer test_token")]

    @property
    def config(self):
        return self._config

    @property
    def mode(self):
        return self._mode


class TestTerminalServiceCreation:
    """Test TerminalService initialization."""

    def test_service_creation(self):
        """Test service can be created with transport."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)
        assert service._transport == transport
        assert service._stub is None

    def test_transport_property(self):
        """Test transport property access."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)
        assert service.transport == transport


class TestTerminalServiceCreate:
    """Test TerminalService.create method."""

    def test_create_session_default_params(self):
        """Test create session with default parameters."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_response = MagicMock()
        mock_response.session_id = "test-session-123"

        # Mock the stub to avoid gRPC channel issues
        mock_stub = MagicMock()
        mock_stub.CreateSession = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        # Patch protobuf to avoid field validation issues
        with patch("cmdop._generated.rpc_messages.session_pb2.CreateSessionRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.create()

        assert isinstance(result, SessionInfo)
        assert result.session_id == "test-session-123"
        assert result.state == SessionState.ACTIVE
        assert result.mode == SessionMode.EXCLUSIVE
        assert result.shell == "/bin/bash"
        assert result.cols == 80
        assert result.rows == 24

    def test_create_session_custom_params(self):
        """Test create session with custom parameters."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_response = MagicMock()
        mock_response.session_id = "custom-session-456"

        mock_stub = MagicMock()
        mock_stub.CreateSession = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.session_pb2.CreateSessionRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.create(
                shell="/bin/zsh",
                cols=120,
                rows=40,
                working_dir="/home/user",
                mode=SessionMode.SHARED,
            )

        assert result.session_id == "custom-session-456"
        assert result.shell == "/bin/zsh"
        assert result.cols == 120
        assert result.rows == 40
        assert result.working_dir == "/home/user"
        assert result.mode == SessionMode.SHARED

    def test_create_session_returns_utc_timestamp(self):
        """Test created_at is UTC datetime."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_response = MagicMock()
        mock_response.session_id = "session-with-time"

        mock_stub = MagicMock()
        mock_stub.CreateSession = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.session_pb2.CreateSessionRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.create()

        assert result.created_at is not None
        assert result.created_at.tzinfo == timezone.utc


class TestTerminalServiceSendInput:
    """Test TerminalService.send_input method."""

    def test_send_input_bytes(self):
        """Test sending bytes input."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.terminal_pb2.SendInputRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.send_input("session-123", b"ls -la\n")
            MockRequest.assert_called_once_with(
                session_id="session-123",
                data=b"ls -la\n",
            )

    def test_send_input_string(self):
        """Test sending string input (auto-encoded)."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.terminal_pb2.SendInputRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.send_input("session-456", "echo hello\n")
            MockRequest.assert_called_once_with(
                session_id="session-456",
                data=b"echo hello\n",
            )


class TestTerminalServiceResize:
    """Test TerminalService.resize method."""

    def test_resize(self):
        """Test terminal resize."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.terminal_pb2.SendResizeRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.resize("session-123", cols=120, rows=40)
            MockRequest.assert_called_once_with(
                session_id="session-123",
                cols=120,
                rows=40,
            )


class TestTerminalServiceSendSignal:
    """Test TerminalService.send_signal method."""

    def test_send_sigint(self):
        """Test sending SIGINT signal."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.terminal_pb2.SendSignalRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.send_signal("session-123", SignalType.SIGINT)
            MockRequest.assert_called_once_with(
                session_id="session-123",
                signal=2,  # SIGINT
            )

    def test_send_sigterm(self):
        """Test sending SIGTERM signal."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.terminal_pb2.SendSignalRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.send_signal("session-123", SignalType.SIGTERM)
            MockRequest.assert_called_once_with(
                session_id="session-123",
                signal=15,  # SIGTERM
            )

    def test_send_sigkill(self):
        """Test sending SIGKILL signal."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.terminal_pb2.SendSignalRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.send_signal("session-123", SignalType.SIGKILL)
            MockRequest.assert_called_once_with(
                session_id="session-123",
                signal=9,  # SIGKILL
            )

    def test_signal_mapping(self):
        """Test all signal mappings."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        signal_map = {
            SignalType.SIGHUP: 1,
            SignalType.SIGINT: 2,
            SignalType.SIGTERM: 15,
            SignalType.SIGKILL: 9,
            SignalType.SIGSTOP: 19,
            SignalType.SIGCONT: 18,
        }

        for signal_type, expected_value in signal_map.items():
            with patch("cmdop._generated.rpc_messages.terminal_pb2.SendSignalRequest") as MockRequest:
                MockRequest.return_value = MagicMock()
                service.send_signal("session-123", signal_type)
                MockRequest.assert_called_with(
                    session_id="session-123",
                    signal=expected_value,
                )


class TestTerminalServiceClose:
    """Test TerminalService.close method."""

    def test_close_session(self):
        """Test closing a session."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.session_pb2.CloseSessionRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.close("session-123")
            MockRequest.assert_called_once_with(session_id="session-123")

    def test_close_session_force(self):
        """Test force closing a session."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.session_pb2.CloseSessionRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.close("session-123", force=True)
            # Note: force param is not currently used in implementation
            MockRequest.assert_called_once_with(session_id="session-123")


class TestTerminalServiceGetHistory:
    """Test TerminalService.get_history method."""

    def test_get_history_default(self):
        """Test getting history with defaults."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_response = MagicMock()
        mock_response.data = b"command output\nmore output\n"
        mock_response.total = 100  # Service looks for 'total', not 'total_lines'

        mock_stub = MagicMock()
        mock_stub.GetHistory = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.history_pb2.GetHistoryRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.get_history("session-123")
            MockRequest.assert_called_once_with(
                session_id="session-123",
                limit=1000,
                offset=0,
            )

        assert isinstance(result, HistoryResponse)
        assert result.session_id == "session-123"
        assert result.data == b"command output\nmore output\n"
        assert result.total_lines == 100

    def test_get_history_custom_lines(self):
        """Test getting history with custom line count."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_response = MagicMock()
        mock_response.data = b"output"
        mock_response.total = 50  # Service looks for 'total', not 'total_lines'

        mock_stub = MagicMock()
        mock_stub.GetHistory = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.history_pb2.GetHistoryRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.get_history("session-123", lines=500)
            MockRequest.assert_called_once_with(
                session_id="session-123",
                limit=500,
                offset=0,
            )

    def test_get_history_no_total_lines_attr(self):
        """Test history response without total_lines attribute."""
        from cmdop.services.terminal import TerminalService

        transport = MockTransport()
        service = TerminalService(transport)

        mock_response = MagicMock(spec=["data"])
        mock_response.data = b"output"
        # total_lines attribute is missing

        mock_stub = MagicMock()
        mock_stub.GetHistory = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.history_pb2.GetHistoryRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.get_history("session-123", lines=100)

        assert result.total_lines == 100  # Falls back to requested lines


class TestAsyncTerminalService:
    """Test AsyncTerminalService class."""

    def test_async_service_creation(self):
        """Test async service can be created."""
        from cmdop.services.terminal import AsyncTerminalService

        transport = MockTransport()
        service = AsyncTerminalService(transport)
        assert service._transport == transport
        assert service._stub is None

    @pytest.mark.asyncio
    async def test_async_create_session(self):
        """Test async create session."""
        from cmdop.services.terminal import AsyncTerminalService

        transport = MockTransport()
        service = AsyncTerminalService(transport)

        mock_response = MagicMock()
        mock_response.session_id = "async-session-123"

        # Create async mock
        async def mock_create_session(*args, **kwargs):
            return mock_response

        mock_stub = MagicMock()
        mock_stub.CreateSession = mock_create_session
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.session_pb2.CreateSessionRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = await service.create()

        assert result.session_id == "async-session-123"
        assert result.state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_async_send_input(self):
        """Test async send input."""
        from cmdop.services.terminal import AsyncTerminalService

        transport = MockTransport()
        service = AsyncTerminalService(transport)

        async def mock_send_input(*args, **kwargs):
            return MagicMock()

        mock_stub = MagicMock()
        mock_stub.SendInput = mock_send_input
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.terminal_pb2.SendInputRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            await service.send_input("session-123", "test\n")
            MockRequest.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_resize(self):
        """Test async resize."""
        from cmdop.services.terminal import AsyncTerminalService

        transport = MockTransport()
        service = AsyncTerminalService(transport)

        async def mock_send_resize(*args, **kwargs):
            return MagicMock()

        mock_stub = MagicMock()
        mock_stub.SendResize = mock_send_resize
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.terminal_pb2.SendResizeRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            await service.resize("session-123", 100, 50)
            MockRequest.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_send_signal(self):
        """Test async send signal."""
        from cmdop.services.terminal import AsyncTerminalService

        transport = MockTransport()
        service = AsyncTerminalService(transport)

        async def mock_send_signal(*args, **kwargs):
            return MagicMock()

        mock_stub = MagicMock()
        mock_stub.SendSignal = mock_send_signal
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.terminal_pb2.SendSignalRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            await service.send_signal("session-123", SignalType.SIGINT)
            MockRequest.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_close(self):
        """Test async close."""
        from cmdop.services.terminal import AsyncTerminalService

        transport = MockTransport()
        service = AsyncTerminalService(transport)

        async def mock_close_session(*args, **kwargs):
            return MagicMock()

        mock_stub = MagicMock()
        mock_stub.CloseSession = mock_close_session
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.session_pb2.CloseSessionRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            await service.close("session-123")
            MockRequest.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_get_history(self):
        """Test async get history."""
        from cmdop.services.terminal import AsyncTerminalService

        transport = MockTransport()
        service = AsyncTerminalService(transport)

        mock_response = MagicMock()
        mock_response.data = b"async output"
        mock_response.total = 50  # Service looks for 'total', not 'total_lines'

        async def mock_get_history(*args, **kwargs):
            return mock_response

        mock_stub = MagicMock()
        mock_stub.GetHistory = mock_get_history
        service._stub = mock_stub

        with patch("cmdop._generated.rpc_messages.history_pb2.GetHistoryRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = await service.get_history("session-123")

        assert result.data == b"async output"
        assert result.total_lines == 50
