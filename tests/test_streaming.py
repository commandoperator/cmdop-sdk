"""
Tests for streaming module (TerminalStream).
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cmdop.streaming import (
    StreamCallback,
    StreamEvent,
    StreamState,
    TerminalStream,
)
from cmdop.streaming.base import StreamMetrics
from cmdop.streaming.handlers import (
    CommandCompleteData,
    ErrorData,
    HistoryData,
    OutputData,
    StatusData,
)


class MockLocalTransport:
    """Mock local transport for testing."""

    @property
    def mode(self) -> str:
        return "local"

    def get_async_channel(self):
        return MagicMock()

    @property
    def metadata(self):
        return []


class MockRemoteTransport:
    """Mock remote transport for testing."""

    @property
    def mode(self) -> str:
        return "remote"

    def get_async_channel(self):
        return MagicMock()

    @property
    def metadata(self):
        return [("authorization", "Bearer test")]


class TestStreamState:
    """Tests for StreamState enum."""

    def test_stream_states_exist(self):
        """Test all expected stream states exist."""
        assert StreamState.IDLE.value == "idle"
        assert StreamState.CONNECTING.value == "connecting"
        assert StreamState.REGISTERING.value == "registering"
        assert StreamState.CONNECTED.value == "connected"
        assert StreamState.RECONNECTING.value == "reconnecting"
        assert StreamState.CLOSING.value == "closing"
        assert StreamState.CLOSED.value == "closed"
        assert StreamState.ERROR.value == "error"


class TestStreamEvent:
    """Tests for StreamEvent enum."""

    def test_stream_events_exist(self):
        """Test all expected stream events exist."""
        assert StreamEvent.OUTPUT.value == "output"
        assert StreamEvent.STATUS.value == "status"
        assert StreamEvent.ERROR.value == "error"
        assert StreamEvent.CONNECTED.value == "connected"
        assert StreamEvent.DISCONNECTED.value == "disconnected"
        assert StreamEvent.COMMAND_COMPLETE.value == "command_complete"
        assert StreamEvent.HISTORY.value == "history"
        assert StreamEvent.KEEPALIVE.value == "keepalive"


class TestStreamMetrics:
    """Tests for StreamMetrics dataclass."""

    def test_initial_values(self):
        """Test initial metric values are zero."""
        metrics = StreamMetrics()

        assert metrics.bytes_sent == 0
        assert metrics.bytes_received == 0
        assert metrics.messages_sent == 0
        assert metrics.messages_received == 0
        assert metrics.keepalive_count == 0
        assert metrics.reconnect_count == 0
        assert metrics.errors == 0

    def test_record_sent(self):
        """Test recording sent messages."""
        metrics = StreamMetrics()

        metrics.record_sent(100)
        metrics.record_sent(50)

        assert metrics.bytes_sent == 150
        assert metrics.messages_sent == 2

    def test_record_received(self):
        """Test recording received messages."""
        metrics = StreamMetrics()

        metrics.record_received(200)

        assert metrics.bytes_received == 200
        assert metrics.messages_received == 1

    def test_record_keepalive(self):
        """Test recording keepalive."""
        metrics = StreamMetrics()

        metrics.record_keepalive()
        metrics.record_keepalive()

        assert metrics.keepalive_count == 2

    def test_record_error(self):
        """Test recording errors."""
        metrics = StreamMetrics()

        metrics.record_error()

        assert metrics.errors == 1

    def test_record_reconnect(self):
        """Test recording reconnects."""
        metrics = StreamMetrics()

        metrics.record_reconnect()

        assert metrics.reconnect_count == 1


class TestHandlerDataClasses:
    """Tests for handler data classes."""

    def test_output_data(self):
        """Test OutputData dataclass."""
        data = OutputData(data=b"hello", is_stderr=False, sequence=1)

        assert data.data == b"hello"
        assert data.text == "hello"
        assert data.is_stderr is False
        assert data.sequence == 1

    def test_output_data_unicode(self):
        """Test OutputData with unicode."""
        data = OutputData(data="привет".encode("utf-8"))

        assert data.text == "привет"

    def test_output_data_invalid_utf8(self):
        """Test OutputData with invalid UTF-8."""
        data = OutputData(data=b"\xff\xfe")

        # Should not raise, uses replacement char
        assert "�" in data.text

    def test_status_data(self):
        """Test StatusData dataclass."""
        data = StatusData(
            old_status="idle",
            new_status="active",
            reason="started",
            working_directory="/home/user",
        )

        assert data.old_status == "idle"
        assert data.new_status == "active"
        assert data.reason == "started"
        assert data.working_directory == "/home/user"

    def test_error_data(self):
        """Test ErrorData dataclass."""
        data = ErrorData(
            error_code="E001",
            message="Something went wrong",
            is_fatal=True,
            can_retry=False,
            suggestions=["Try again", "Check logs"],
        )

        assert data.error_code == "E001"
        assert data.message == "Something went wrong"
        assert data.is_fatal is True
        assert data.can_retry is False
        assert len(data.suggestions) == 2

    def test_command_complete_data(self):
        """Test CommandCompleteData dataclass."""
        data = CommandCompleteData(
            command_id="cmd-123",
            exit_code=0,
            duration_ms=1500,
        )

        assert data.command_id == "cmd-123"
        assert data.exit_code == 0
        assert data.duration_ms == 1500

    def test_history_data(self):
        """Test HistoryData dataclass."""
        data = HistoryData(
            commands=["ls", "cd /", "pwd"],
            total=100,
            source="bash_history",
        )

        assert len(data.commands) == 3
        assert data.total == 100
        assert data.source == "bash_history"


class TestTerminalStream:
    """Tests for TerminalStream class."""

    def test_initial_state(self):
        """Test initial stream state."""
        transport = MockRemoteTransport()
        stream = TerminalStream(transport)

        assert stream.state == StreamState.IDLE
        assert stream.session_id is None
        assert stream.is_connected is False

    def test_callback_registration_chaining(self):
        """Test callback registration returns self for chaining."""
        transport = MockRemoteTransport()
        stream = TerminalStream(transport)

        async def handler(data):
            pass

        result = (
            stream
            .on_output(handler)
            .on_status(handler)
            .on_error(handler)
            .on_disconnect(handler)
        )

        assert result is stream

    @pytest.mark.asyncio
    async def test_connect_rejects_local_transport(self):
        """Test that connect() rejects local transport."""
        transport = MockLocalTransport()
        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError) as exc_info:
            await stream.connect()

        assert "remote connection" in str(exc_info.value).lower()
        assert "local transport" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_send_input_requires_connection(self):
        """Test that send_input requires connected stream."""
        transport = MockRemoteTransport()
        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError) as exc_info:
            await stream.send_input(b"test")

        assert "not connected" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_send_resize_requires_connection(self):
        """Test that send_resize requires connected stream."""
        transport = MockRemoteTransport()
        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError) as exc_info:
            await stream.send_resize(80, 24)

        assert "not connected" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_close_idempotent(self):
        """Test that close() is idempotent."""
        transport = MockRemoteTransport()
        stream = TerminalStream(transport)

        # Close without connecting
        await stream.close()
        await stream.close()  # Should not raise

        assert stream.state == StreamState.CLOSED

    def test_repr(self):
        """Test stream string representation."""
        transport = MockRemoteTransport()
        stream = TerminalStream(transport)

        repr_str = repr(stream)

        assert "TerminalStream" in repr_str
        assert "idle" in repr_str

    def test_metrics_property(self):
        """Test metrics property returns StreamMetrics."""
        transport = MockRemoteTransport()
        stream = TerminalStream(transport)

        metrics = stream.metrics

        assert isinstance(metrics, StreamMetrics)
        assert metrics.bytes_sent == 0


class TestTerminalStreamContextManager:
    """Tests for TerminalStream async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_closes_on_exit(self):
        """Test that context manager closes stream on exit."""
        transport = MockLocalTransport()
        stream = TerminalStream(transport)

        # Mock connect to avoid the local transport error
        # We're testing that __aexit__ calls close()
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"

        async with stream:
            assert stream.state == StreamState.CONNECTED

        assert stream.state == StreamState.CLOSED

    @pytest.mark.asyncio
    async def test_context_manager_closes_on_exception(self):
        """Test that context manager closes stream on exception."""
        transport = MockLocalTransport()
        stream = TerminalStream(transport)

        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"

        with pytest.raises(ValueError):
            async with stream:
                raise ValueError("test error")

        assert stream.state == StreamState.CLOSED
