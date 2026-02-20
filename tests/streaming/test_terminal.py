"""
Tests for TerminalStream bidirectional streaming.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cmdop.streaming.base import StreamState
from cmdop.streaming.terminal import TerminalStream


class TestTerminalStreamInit:
    """Test TerminalStream initialization."""

    def test_initial_state_is_idle(self):
        """Stream starts in IDLE state."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        assert stream.state == StreamState.IDLE

    def test_session_id_none_initially(self):
        """Session ID is None before connect."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        assert stream.session_id is None

    def test_is_connected_false_initially(self):
        """is_connected is False before connect."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        assert stream.is_connected is False


class TestTerminalStreamConnect:
    """Test TerminalStream connection."""

    async def test_connect_requires_remote_transport(self):
        """Connect raises RuntimeError for local transport."""
        transport = MagicMock()
        transport.mode = "local"

        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError) as exc_info:
            await stream.connect()

        assert "remote connection" in str(exc_info.value).lower()

    async def test_connect_sets_session_id(self):
        """Connect generates a session ID."""
        transport = MagicMock()
        transport.mode = "remote"
        transport.get_async_channel = MagicMock()
        transport.metadata = {}

        stream = TerminalStream(transport)

        # Mock the stub and stream at the module level import
        with patch("cmdop.grpc.generated.service_pb2_grpc.TerminalStreamingServiceStub") as mock_stub:
            mock_grpc_stream = AsyncMock()
            mock_stub.return_value.ConnectTerminal = MagicMock(return_value=mock_grpc_stream)

            # Pre-set session ready since we're mocking the registration flow
            original_send_register = stream._send_register

            async def mock_send_register():
                stream._session_ready.set()

            stream._send_register = mock_send_register

            session_id = await stream.connect(timeout=1.0)

            assert session_id is not None
            assert stream.session_id == session_id


class TestTerminalStreamWaitReady:
    """Test wait_ready() method."""

    async def test_wait_ready_not_connected_raises(self):
        """wait_ready raises if not connected."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError) as exc_info:
            await stream.wait_ready()

        assert "not connected" in str(exc_info.value).lower()

    async def test_wait_ready_already_connected_returns(self):
        """wait_ready returns immediately if already connected."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED

        # Should not raise
        await stream.wait_ready()

    async def test_wait_ready_timeout(self):
        """wait_ready raises TimeoutError on timeout."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTING
        stream._session_ready = asyncio.Event()  # Not set

        with pytest.raises(TimeoutError):
            await stream.wait_ready(timeout=0.1)

    async def test_wait_ready_error_state_raises(self):
        """wait_ready raises for error/closed states."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        for state in [StreamState.ERROR, StreamState.CLOSED, StreamState.CLOSING]:
            stream._state = state
            with pytest.raises(RuntimeError) as exc_info:
                await stream.wait_ready()
            assert "invalid state" in str(exc_info.value).lower()


class TestTerminalStreamSendInput:
    """Test send_input() method."""

    async def test_send_input_not_connected_raises(self):
        """send_input raises if not connected."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError) as exc_info:
            await stream.send_input(b"test")

        assert "not connected" in str(exc_info.value).lower()

    async def test_send_input_encodes_string(self):
        """send_input converts string to bytes."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._queue = asyncio.Queue()

        await stream.send_input("hello")

        # Check message was queued
        msg = await stream._queue.get()
        assert msg.output.data == b"hello"

    async def test_send_input_bytes_passthrough(self):
        """send_input passes bytes directly."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._queue = asyncio.Queue()

        await stream.send_input(b"\x1b[A")  # Up arrow

        msg = await stream._queue.get()
        assert msg.output.data == b"\x1b[A"


class TestTerminalStreamSendSignal:
    """Test send_signal() method."""

    async def test_send_signal_not_connected_raises(self):
        """send_signal raises if not connected."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError):
            await stream.send_signal(2)  # SIGINT

    async def test_send_signal_queues_message(self):
        """send_signal queues status update with signal info."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._queue = asyncio.Queue()

        await stream.send_signal(2)  # SIGINT

        msg = await stream._queue.get()
        assert "signal:2" in msg.status.reason


class TestTerminalStreamSendResize:
    """Test send_resize() method."""

    async def test_send_resize_not_connected_raises(self):
        """send_resize raises if not connected."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError):
            await stream.send_resize(80, 24)

    async def test_send_resize_queues_message(self):
        """send_resize queues status update with size info."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._queue = asyncio.Queue()

        await stream.send_resize(120, 40)

        msg = await stream._queue.get()
        assert "resize:120x40" in msg.status.reason


class TestTerminalStreamRequestHistory:
    """Test request_history() method."""

    async def test_request_history_not_connected_raises(self):
        """request_history raises if not connected."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError):
            await stream.request_history()

    async def test_request_history_queues_message(self):
        """request_history queues status update."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._queue = asyncio.Queue()

        await stream.request_history(limit=50, offset=10)

        msg = await stream._queue.get()
        assert "history:50:10" in msg.status.reason


class TestTerminalStreamCallbacks:
    """Test callback registration and invocation."""

    def test_on_output_returns_self(self):
        """on_output returns self for chaining."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        result = stream.on_output(lambda data: None)
        assert result is stream

    def test_on_status_returns_self(self):
        """on_status returns self for chaining."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        result = stream.on_status(lambda status: None)
        assert result is stream

    def test_on_error_returns_self(self):
        """on_error returns self for chaining."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        result = stream.on_error(lambda code, msg, fatal: None)
        assert result is stream

    def test_on_disconnect_returns_self(self):
        """on_disconnect returns self for chaining."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        result = stream.on_disconnect(lambda reason: None)
        assert result is stream

    def test_callback_chaining(self):
        """Callbacks can be chained."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        result = (
            stream
            .on_output(lambda data: None)
            .on_status(lambda status: None)
            .on_error(lambda code, msg, fatal: None)
            .on_disconnect(lambda reason: None)
        )

        assert result is stream


class TestTerminalStreamClose:
    """Test close() method."""

    async def test_close_sets_state_closed(self):
        """close() transitions to CLOSED state."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._shutdown = asyncio.Event()

        await stream.close()

        assert stream.state == StreamState.CLOSED

    async def test_close_idempotent(self):
        """close() is idempotent."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CLOSED

        # Should not raise
        await stream.close()
        assert stream.state == StreamState.CLOSED

    async def test_close_invokes_disconnect_callback(self):
        """close() invokes disconnect callback."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._shutdown = asyncio.Event()

        callback = MagicMock()
        stream.on_disconnect(callback)

        await stream.close(reason="test_close")

        callback.assert_called_once_with("test_close")


class TestTerminalStreamContextManager:
    """Test async context manager."""

    async def test_context_manager_connects(self):
        """Context manager calls connect()."""
        transport = MagicMock()
        transport.mode = "remote"
        transport.get_async_channel = MagicMock()
        transport.metadata = {}

        stream = TerminalStream(transport)

        with patch.object(stream, "connect", new_callable=AsyncMock) as mock_connect:
            mock_connect.return_value = "session-id"
            async with stream:
                mock_connect.assert_called_once()

    async def test_context_manager_closes(self):
        """Context manager calls close()."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._shutdown = asyncio.Event()

        with patch.object(stream, "connect", new_callable=AsyncMock):
            with patch.object(stream, "close", new_callable=AsyncMock) as mock_close:
                async with stream:
                    pass
                mock_close.assert_called_once()


class TestTerminalStreamMetrics:
    """Test metrics tracking."""

    def test_metrics_available(self):
        """Metrics object is available."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        assert stream.metrics is not None
        assert stream.metrics.bytes_sent == 0
        assert stream.metrics.bytes_received == 0

    async def test_send_input_records_bytes(self):
        """send_input records bytes sent."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._queue = asyncio.Queue()

        await stream.send_input(b"hello")

        assert stream.metrics.bytes_sent == 5


class TestTerminalStreamRepr:
    """Test string representation."""

    def test_repr_includes_state(self):
        """repr includes state."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        repr_str = repr(stream)
        assert "IDLE" in repr_str or "idle" in repr_str.lower()

    def test_repr_includes_session_id(self):
        """repr includes session_id."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._session_id = "test-123"

        repr_str = repr(stream)
        assert "test-123" in repr_str


class TestTerminalStreamDetach:
    """Test detach() method."""

    async def test_detach_returns_session_id(self):
        """detach() returns session ID."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session-123"
        stream._shutdown = asyncio.Event()
        stream._queue = asyncio.Queue()

        session_id = await stream.detach()

        assert session_id == "test-session-123"

    async def test_detach_sets_state_closed(self):
        """detach() transitions to CLOSED state."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._shutdown = asyncio.Event()
        stream._queue = asyncio.Queue()

        await stream.detach()

        assert stream.state == StreamState.CLOSED

    async def test_detach_not_connected_returns_none(self):
        """detach() returns None if not connected."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.IDLE

        session_id = await stream.detach()

        assert session_id is None

    async def test_detach_sends_detach_message(self):
        """detach() sends detach status update."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._shutdown = asyncio.Event()
        stream._queue = asyncio.Queue()

        await stream.detach()

        # Check that a detach message was queued
        msg = await stream._queue.get()
        assert "detach" in msg.status.reason

    async def test_detach_invokes_disconnect_callback(self):
        """detach() invokes disconnect callback with 'detached' reason."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._shutdown = asyncio.Event()
        stream._queue = asyncio.Queue()

        callback = MagicMock()
        stream.on_disconnect(callback)

        await stream.detach()

        callback.assert_called_once_with("detached")


class TestTerminalStreamAttach:
    """Test attach() method."""

    async def test_attach_requires_remote_transport(self):
        """attach() raises RuntimeError for local transport."""
        transport = MagicMock()
        transport.mode = "local"

        stream = TerminalStream(transport)

        with pytest.raises(RuntimeError) as exc_info:
            await stream.attach("session-123")

        assert "remote connection" in str(exc_info.value).lower()

    async def test_attach_already_connected_raises(self):
        """attach() raises if already connected."""
        transport = MagicMock()
        transport.mode = "remote"

        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED

        with pytest.raises(RuntimeError) as exc_info:
            await stream.attach("session-123")

        assert "already connected" in str(exc_info.value).lower()

    async def test_attach_sets_session_id(self):
        """attach() uses provided session ID."""
        transport = MagicMock()
        transport.mode = "remote"
        transport.get_async_channel = MagicMock()
        transport.metadata = {}

        stream = TerminalStream(transport)

        with patch("cmdop.grpc.generated.service_pb2_grpc.TerminalStreamingServiceStub") as mock_stub:
            mock_grpc_stream = AsyncMock()
            mock_stub.return_value.ConnectTerminal = MagicMock(return_value=mock_grpc_stream)

            # Pre-set session ready
            original_send_attach = stream._send_attach

            async def mock_send_attach():
                stream._session_ready.set()

            stream._send_attach = mock_send_attach

            session_id = await stream.attach("existing-session-123", timeout=1.0)

            assert session_id == "existing-session-123"
            assert stream.session_id == "existing-session-123"

    async def test_attach_timeout(self):
        """attach() raises ConnectionError wrapping TimeoutError on timeout."""
        transport = MagicMock()
        transport.mode = "remote"
        transport.get_async_channel = MagicMock()
        transport.metadata = {}

        stream = TerminalStream(transport)

        with patch("cmdop.grpc.generated.service_pb2_grpc.TerminalStreamingServiceStub") as mock_stub:
            mock_grpc_stream = AsyncMock()
            mock_stub.return_value.ConnectTerminal = MagicMock(return_value=mock_grpc_stream)

            # Don't set session ready - will timeout
            async def mock_send_attach():
                pass  # Don't set ready

            stream._send_attach = mock_send_attach

            # TimeoutError is wrapped in ConnectionError
            with pytest.raises(ConnectionError) as exc_info:
                await stream.attach("session-123", timeout=0.1)

            assert "session-123" in str(exc_info.value)


class TestTerminalStreamMessageGenerator:
    """Test _message_generator() keepalive mechanism."""

    async def test_message_generator_yields_queued_messages(self):
        """_message_generator yields messages from queue."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._session_id = "test-session"
        stream._queue = asyncio.Queue()
        stream._shutdown = asyncio.Event()

        # Queue a message
        from cmdop.grpc.generated.agent_messages_pb2 import AgentMessage, TerminalOutput

        msg = AgentMessage(
            session_id="test-session",
            message_id="1",
            output=TerminalOutput(data=b"test"),
        )
        await stream._queue.put(msg)

        # Get generator
        gen = stream._message_generator()

        # Should yield our message
        result = await gen.__anext__()
        assert result.output.data == b"test"

        # Shutdown to stop generator
        stream._shutdown.set()

    async def test_message_generator_sends_heartbeat_on_timeout(self):
        """_message_generator sends heartbeat when queue is empty."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._session_id = "test-session"
        stream._queue = asyncio.Queue()
        stream._shutdown = asyncio.Event()

        # Override keepalive interval to be very short for test
        original_interval = stream.KEEPALIVE_INTERVAL
        stream.KEEPALIVE_INTERVAL = 0.05  # 50ms

        try:
            gen = stream._message_generator()

            # Should yield heartbeat after timeout (queue is empty)
            result = await asyncio.wait_for(gen.__anext__(), timeout=0.2)

            # Verify it's a heartbeat
            assert result.HasField("heartbeat")
            assert stream.metrics.keepalive_count == 1

        finally:
            stream.KEEPALIVE_INTERVAL = original_interval
            stream._shutdown.set()

    async def test_message_generator_stops_on_shutdown(self):
        """_message_generator stops when shutdown is set."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._session_id = "test-session"
        stream._queue = asyncio.Queue()
        stream._shutdown = asyncio.Event()

        gen = stream._message_generator()

        # Set shutdown
        stream._shutdown.set()

        # Generator should stop (StopAsyncIteration)
        messages = []
        async for msg in gen:
            messages.append(msg)

        assert len(messages) == 0


class TestTerminalStreamNoKeepaliveTask:
    """Verify keepalive task was removed."""

    def test_no_keepalive_task_attribute(self):
        """TerminalStream should not have _keepalive_task attribute."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        assert not hasattr(stream, "_keepalive_task")

    def test_no_keepalive_loop_method(self):
        """TerminalStream should not have _keepalive_loop method."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        assert not hasattr(stream, "_keepalive_loop")


class TestTerminalStreamEdgeCases:
    """Test edge cases and error handling."""

    async def test_close_cancels_receiver_task(self):
        """close() properly cancels receiver task."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._shutdown = asyncio.Event()

        # Create a mock receiver task
        async def mock_receiver():
            await asyncio.sleep(10)

        stream._receiver_task = asyncio.create_task(mock_receiver())

        await stream.close()

        assert stream._receiver_task.cancelled() or stream._receiver_task.done()

    async def test_detach_cancels_receiver_task(self):
        """detach() properly cancels receiver task."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._session_id = "test-session"
        stream._shutdown = asyncio.Event()
        stream._queue = asyncio.Queue()

        # Create a mock receiver task
        async def mock_receiver():
            await asyncio.sleep(10)

        stream._receiver_task = asyncio.create_task(mock_receiver())

        await stream.detach()

        assert stream._receiver_task.cancelled() or stream._receiver_task.done()

    async def test_multiple_close_calls_safe(self):
        """Multiple close() calls are safe (idempotent)."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTED
        stream._shutdown = asyncio.Event()

        await stream.close()
        await stream.close()
        await stream.close()

        assert stream.state == StreamState.CLOSED

    async def test_detach_from_connecting_state(self):
        """detach() works from CONNECTING state."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._state = StreamState.CONNECTING
        stream._session_id = "test-session"
        stream._shutdown = asyncio.Event()
        stream._queue = asyncio.Queue()

        session_id = await stream.detach()

        assert session_id == "test-session"
        assert stream.state == StreamState.CLOSED

    async def test_attach_resets_state(self):
        """attach() properly resets internal state."""
        transport = MagicMock()
        transport.mode = "remote"
        transport.get_async_channel = MagicMock()
        transport.metadata = {}

        stream = TerminalStream(transport)

        # First connection (simulated closed)
        stream._state = StreamState.CLOSED
        stream._session_ready.set()  # Old state

        with patch("cmdop.grpc.generated.service_pb2_grpc.TerminalStreamingServiceStub") as mock_stub:
            mock_grpc_stream = AsyncMock()
            mock_stub.return_value.ConnectTerminal = MagicMock(return_value=mock_grpc_stream)

            async def mock_send_attach():
                stream._session_ready.set()

            stream._send_attach = mock_send_attach

            # attach() should reset and work
            session_id = await stream.attach("new-session", timeout=1.0)

            assert session_id == "new-session"
            assert stream.state == StreamState.CONNECTED
