"""
Terminal streaming implementation.

Provides bidirectional gRPC streaming for terminal I/O.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import TYPE_CHECKING, Any

from cmdop.config import get_settings
from cmdop.streaming.base import StreamMetrics, StreamState
from cmdop.streaming.handlers import (
    CommandCompleteData,
    CommandCompleteHandler,
    DisconnectHandler,
    ErrorData,
    ErrorHandler,
    HistoryData,
    HistoryHandler,
    OutputData,
    OutputHandler,
    StatusData,
    StatusHandler,
)

if TYPE_CHECKING:
    from cmdop.transport.base import BaseTransport


class TerminalStream:
    """
    Bidirectional terminal stream.

    Manages a gRPC bidirectional stream for real-time terminal I/O.
    Sends keepalive heartbeats every 25 seconds to prevent NAT timeout.

    **IMPORTANT: Remote mode only!**
    Bidirectional streaming is only supported via cloud relay (RemoteTransport).
    Local connections (LocalTransport) return Unimplemented error.
    For local mode, use unary RPCs: SendInput, GetHistory, etc.

    Usage (remote mode):
        >>> from cmdop import AsyncCMDOPClient
        >>>
        >>> async with AsyncCMDOPClient.remote(api_key="xxx") as client:
        ...     async with client.terminal.stream() as stream:
        ...         stream.on_output(lambda data: print(data.decode(), end=""))
        ...         await stream.send_input(b"ls -la\\n")

    For local mode, use:
        >>> transport = LocalTransport.discover()
        >>> client = AsyncCMDOPClient(transport)
        >>> session = await client.terminal.create()
        >>> await client.terminal.send_input(session.session_id, b"ls\\n")

    Callbacks:
        - on_output: Called when terminal output is received
        - on_status: Called when session status changes
        - on_error: Called when an error occurs
        - on_disconnect: Called when stream disconnects
    """

    # Constants
    KEEPALIVE_INTERVAL = 25.0  # seconds, must be < 30s for NAT
    QUEUE_MAX_SIZE = 1000
    QUEUE_PUT_TIMEOUT = 5.0

    def __init__(self, transport: BaseTransport) -> None:
        """
        Initialize terminal stream.

        Args:
            transport: Transport to use for gRPC connection.
        """
        self._transport = transport
        self._settings = get_settings()

        # State
        self._state = StreamState.IDLE
        self._session_id: str | None = None
        self._message_id = 0

        # Async primitives
        self._queue: asyncio.Queue[Any] = asyncio.Queue(
            maxsize=self._settings.queue_max_size
        )
        self._session_ready = asyncio.Event()
        self._shutdown = asyncio.Event()

        # Tasks
        self._receiver_task: asyncio.Task[None] | None = None

        # gRPC stream
        self._stream: Any = None
        self._stub: Any = None

        # Callbacks
        self._on_output: OutputHandler | None = None
        self._on_status: StatusHandler | None = None
        self._on_error: ErrorHandler | None = None
        self._on_command_complete: CommandCompleteHandler | None = None
        self._on_history: HistoryHandler | None = None
        self._on_disconnect: DisconnectHandler | None = None

        # Metrics
        self._metrics = StreamMetrics()

    @property
    def state(self) -> StreamState:
        """Get current stream state."""
        return self._state

    @property
    def session_id(self) -> str | None:
        """Get session ID (available after connect)."""
        return self._session_id

    @property
    def is_connected(self) -> bool:
        """Check if stream is connected."""
        return self._state == StreamState.CONNECTED

    @property
    def metrics(self) -> StreamMetrics:
        """Get stream metrics."""
        return self._metrics

    # =========================================================================
    # Callback Registration
    # =========================================================================

    def on_output(self, handler: OutputHandler) -> TerminalStream:
        """
        Register output callback.

        Args:
            handler: Function called with OutputData when output received.

        Returns:
            Self for chaining.
        """
        self._on_output = handler
        return self

    def on_status(self, handler: StatusHandler) -> TerminalStream:
        """
        Register status change callback.

        Args:
            handler: Function called with (old_status, new_status).

        Returns:
            Self for chaining.
        """
        self._on_status = handler
        return self

    def on_error(self, handler: ErrorHandler) -> TerminalStream:
        """
        Register error callback.

        Args:
            handler: Function called with (error_code, message, is_fatal).

        Returns:
            Self for chaining.
        """
        self._on_error = handler
        return self

    def on_command_complete(self, handler: CommandCompleteHandler) -> TerminalStream:
        """
        Register command completion callback.

        Args:
            handler: Function called with (command_id, exit_code, duration_ms).

        Returns:
            Self for chaining.
        """
        self._on_command_complete = handler
        return self

    def on_history(self, handler: HistoryHandler) -> TerminalStream:
        """
        Register history callback.

        Args:
            handler: Function called with (commands, total).

        Returns:
            Self for chaining.
        """
        self._on_history = handler
        return self

    def on_disconnect(self, handler: DisconnectHandler) -> TerminalStream:
        """
        Register disconnect callback.

        Args:
            handler: Function called with reason when disconnected.

        Returns:
            Self for chaining.
        """
        self._on_disconnect = handler
        return self

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect(self, timeout: float = 10.0) -> str:
        """
        Establish bidirectional stream connection.

        Args:
            timeout: Connection timeout in seconds.

        Returns:
            Session ID.

        Raises:
            ConnectionError: If connection fails.
            TimeoutError: If connection times out.
            RuntimeError: If using local transport (streaming not supported).
        """
        if self._state in (StreamState.CONNECTED, StreamState.CONNECTING):
            if self._session_id:
                return self._session_id
            raise ConnectionError("Stream already connecting")

        # Check transport mode - streaming only works with remote transport
        if self._transport.mode == "local":
            raise RuntimeError(
                "Bidirectional streaming requires remote connection. "
                "Local transport does not support ConnectTerminal streaming. "
                "Use unary RPCs instead: terminal.send_input(), terminal.get_history()"
            )

        self._state = StreamState.CONNECTING
        self._session_id = str(uuid.uuid4())

        try:
            # Get gRPC stub
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            channel = self._transport.get_async_channel()
            self._stub = TerminalStreamingServiceStub(channel)

            # Start bidirectional stream
            self._state = StreamState.REGISTERING
            self._stream = self._stub.ConnectTerminal(
                self._message_generator(),
                metadata=self._transport.metadata,
            )

            # Start receiver task
            self._receiver_task = asyncio.create_task(
                self._receive_loop(),
                name="terminal-stream-receiver",
            )

            # Send registration message
            await self._send_register()

            # Wait for session to be ready
            try:
                await asyncio.wait_for(
                    self._session_ready.wait(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                self._state = StreamState.ERROR
                raise TimeoutError("Connection timed out waiting for session")

            # Keepalive is handled by _message_generator() timeout
            self._state = StreamState.CONNECTED
            return self._session_id

        except Exception as e:
            self._state = StreamState.ERROR
            raise ConnectionError(f"Failed to connect: {e}") from e

    async def wait_ready(self, timeout: float = 10.0) -> None:
        """
        Wait for session to be ready after connection.

        This method can be used to explicitly wait for the session to be
        fully initialized. Note that `connect()` already waits for readiness,
        so this is primarily for use cases where you need to verify readiness
        or wait again after potential disconnection.

        Args:
            timeout: Maximum wait time in seconds.

        Raises:
            RuntimeError: If stream not connected.
            TimeoutError: If session doesn't become ready in time.
        """
        if self._state == StreamState.IDLE:
            raise RuntimeError("Stream not connected. Call connect() first.")

        if self._state == StreamState.CONNECTED:
            return  # Already ready

        if self._state in (StreamState.ERROR, StreamState.CLOSED, StreamState.CLOSING):
            raise RuntimeError(f"Stream in invalid state: {self._state.value}")

        # Wait for session ready event
        try:
            await asyncio.wait_for(
                self._session_ready.wait(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Session did not become ready within {timeout} seconds"
            )

    async def close(self, reason: str = "client_close") -> None:
        """
        Gracefully close the stream and terminate remote session.

        This closes both the local connection AND the remote terminal session.
        Use `detach()` if you want to disconnect locally but keep the remote
        session alive for later reattachment.

        Args:
            reason: Reason for closing.
        """
        if self._state in (StreamState.CLOSED, StreamState.CLOSING):
            return

        self._state = StreamState.CLOSING
        self._shutdown.set()

        # Cancel receiver task
        if self._receiver_task:
            self._receiver_task.cancel()
            try:
                await self._receiver_task
            except asyncio.CancelledError:
                pass

        # Close gRPC stream
        if self._stream:
            try:
                await self._stream.done_writing()
            except Exception:
                pass

        self._state = StreamState.CLOSED

        # Invoke disconnect callback
        if self._on_disconnect:
            await self._invoke_callback(self._on_disconnect, reason)

    async def detach(self) -> str | None:
        """
        Detach from stream without closing remote session.

        This disconnects the local client but keeps the remote terminal
        session alive. You can later reattach to the same session using
        `attach(session_id)`.

        Returns:
            Session ID for later reattachment, or None if not connected.

        Example:
            >>> session_id = await stream.detach()
            >>> print(f"Detached from {session_id}")
            >>> # Later...
            >>> new_stream = client.terminal.stream()
            >>> await new_stream.attach(session_id)
        """
        if self._state not in (StreamState.CONNECTED, StreamState.CONNECTING, StreamState.REGISTERING):
            return None

        session_id = self._session_id

        # Send detach notification to server
        if self.is_connected:
            try:
                from cmdop._generated.agent_messages_pb2 import AgentMessage, StatusUpdate

                msg = AgentMessage(
                    session_id=self._session_id,
                    message_id=self._next_message_id(),
                    status=StatusUpdate(reason="detach"),
                )
                await self._enqueue_message(msg)
            except Exception:
                pass  # Best effort

        self._state = StreamState.CLOSING
        self._shutdown.set()

        # Cancel receiver task
        if self._receiver_task:
            self._receiver_task.cancel()
            try:
                await self._receiver_task
            except asyncio.CancelledError:
                pass

        # Close gRPC stream (but remote session stays alive)
        if self._stream:
            try:
                await self._stream.done_writing()
            except Exception:
                pass

        self._state = StreamState.CLOSED

        # Invoke disconnect callback with detach reason
        if self._on_disconnect:
            await self._invoke_callback(self._on_disconnect, "detached")

        return session_id

    async def attach(self, session_id: str, timeout: float = 10.0) -> str:
        """
        Attach to an existing remote terminal session (agent).

        IMPORTANT: session_id must be a REAL agent session_id obtained from
        get_active_session(). Do NOT generate a new UUID - that won't work!

        How it works:
        1. SDK sends RegisterRequest with version="sdk-python-*-attach"
        2. Django sees "attach" in version → adds SDK to _sdk_subscribers
        3. When agent sends output → Django forwards to all SDK subscribers
        4. When SDK sends input → Django forwards to agent queue

        Args:
            session_id: Agent's session ID (from get_active_session()).
            timeout: Connection timeout in seconds.

        Returns:
            Session ID (same as input).

        Raises:
            ConnectionError: If connection fails.
            TimeoutError: If connection times out.
            RuntimeError: If using local transport or already connected.

        Example:
            >>> session = await client.terminal.get_active_session("my-server")
            >>> stream = client.terminal.stream()
            >>> await stream.attach(session.session_id)  # Use agent's session_id!
            >>> stream.on_output(lambda data: print(data.decode(), end=""))
        """
        if self._state in (StreamState.CONNECTED, StreamState.CONNECTING):
            raise RuntimeError("Stream already connected. Create a new stream to attach.")

        # Check transport mode
        if self._transport.mode == "local":
            raise RuntimeError(
                "Bidirectional streaming requires remote connection. "
                "Local transport does not support session attach."
            )

        self._state = StreamState.CONNECTING
        # CRITICAL: Use the agent's real session_id, not a new UUID!
        # This session_id is used in all messages to Django.
        # Django uses it to find the agent queue and SDK subscribers.
        self._session_id = session_id

        # Reset state for reattachment
        self._session_ready.clear()
        self._shutdown.clear()
        self._queue = asyncio.Queue(maxsize=self._settings.queue_max_size)

        try:
            # Get gRPC stub
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            channel = self._transport.get_async_channel()
            self._stub = TerminalStreamingServiceStub(channel)

            # Start bidirectional stream
            self._state = StreamState.REGISTERING
            self._stream = self._stub.ConnectTerminal(
                self._message_generator(),
                metadata=self._transport.metadata,
            )

            # Start receiver task
            self._receiver_task = asyncio.create_task(
                self._receive_loop(),
                name="terminal-stream-receiver",
            )

            # Send attach message (reuse register with existing session_id)
            await self._send_attach()

            # Wait for session to be ready
            try:
                await asyncio.wait_for(
                    self._session_ready.wait(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                self._state = StreamState.ERROR
                raise TimeoutError(f"Attach timed out for session {session_id}")

            # Keepalive is handled by _message_generator() timeout
            self._state = StreamState.CONNECTED
            return self._session_id

        except Exception as e:
            self._state = StreamState.ERROR
            raise ConnectionError(f"Failed to attach: {e}") from e

    async def _send_attach(self) -> None:
        """Send attach message to reconnect to existing session."""
        from cmdop._generated.agent_messages_pb2 import AgentMessage, RegisterRequest
        from cmdop._generated.common_types_pb2 import TerminalSize

        import platform
        import os

        # Attach uses register with attach flag in version string
        register = RegisterRequest(
            version="sdk-python-0.1.0-attach",
            hostname=platform.node(),
            platform=platform.system().lower(),
            initial_size=TerminalSize(cols=80, rows=24),
            username=os.getenv("USER", "unknown"),
            home_dir=os.path.expanduser("~"),
        )

        msg = AgentMessage(
            session_id=self._session_id,
            message_id=self._next_message_id(),
            register=register,
        )

        await self._enqueue_message(msg)

    # =========================================================================
    # Input Operations
    # =========================================================================

    async def send_input(self, data: bytes | str) -> None:
        """
        Send terminal input.

        Args:
            data: Input data (bytes or string).

        Raises:
            RuntimeError: If stream not connected.
        """
        if not self.is_connected:
            raise RuntimeError("Stream not connected")

        if isinstance(data, str):
            data = data.encode("utf-8")

        from cmdop._generated.agent_messages_pb2 import AgentMessage, TerminalOutput

        # Note: For SDK sending TO agent, we use AgentMessage
        # with TerminalOutput containing the input data
        msg = AgentMessage(
            session_id=self._session_id,
            message_id=self._next_message_id(),
            output=TerminalOutput(data=data, sequence=0),
        )

        await self._enqueue_message(msg)
        self._metrics.record_sent(len(data))

    async def send_resize(self, cols: int, rows: int) -> None:
        """
        Send terminal resize.

        Args:
            cols: New width in columns.
            rows: New height in rows.

        Raises:
            RuntimeError: If stream not connected.
        """
        if not self.is_connected:
            raise RuntimeError("Stream not connected")

        from cmdop._generated.agent_messages_pb2 import AgentMessage, StatusUpdate

        # Send resize via status update
        msg = AgentMessage(
            session_id=self._session_id,
            message_id=self._next_message_id(),
            status=StatusUpdate(reason=f"resize:{cols}x{rows}"),
        )

        await self._enqueue_message(msg)

    async def send_signal(self, signal: int) -> None:
        """
        Send signal to remote process.

        Common signals:
        - 2 (SIGINT): Interrupt (Ctrl+C)
        - 9 (SIGKILL): Kill (cannot be caught)
        - 15 (SIGTERM): Terminate gracefully
        - 18 (SIGCONT): Continue if stopped
        - 19 (SIGSTOP): Stop process

        Args:
            signal: Signal number to send.

        Raises:
            RuntimeError: If stream not connected.
        """
        if not self.is_connected:
            raise RuntimeError("Stream not connected")

        from cmdop._generated.agent_messages_pb2 import AgentMessage, StatusUpdate

        # Send signal via status update with signal info
        msg = AgentMessage(
            session_id=self._session_id,
            message_id=self._next_message_id(),
            status=StatusUpdate(reason=f"signal:{signal}"),
        )

        await self._enqueue_message(msg)

    async def request_history(self, limit: int = 100, offset: int = 0) -> None:
        """
        Request shell history from agent.

        Args:
            limit: Maximum commands to return.
            offset: Offset for pagination.

        Raises:
            RuntimeError: If stream not connected.
        """
        if not self.is_connected:
            raise RuntimeError("Stream not connected")

        from cmdop._generated.agent_messages_pb2 import AgentMessage, StatusUpdate

        # Request history via status update
        msg = AgentMessage(
            session_id=self._session_id,
            message_id=self._next_message_id(),
            status=StatusUpdate(reason=f"history:{limit}:{offset}"),
        )

        await self._enqueue_message(msg)

    # =========================================================================
    # Internal: Message Generator
    # =========================================================================

    async def _message_generator(self) -> Any:
        """
        Generate outgoing messages with keepalive.

        Yields AgentMessage proto objects to send to server.
        """
        while not self._shutdown.is_set():
            try:
                # Wait for message with keepalive timeout
                msg = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self.KEEPALIVE_INTERVAL,
                )
                yield msg
            except asyncio.TimeoutError:
                # Send heartbeat on timeout
                heartbeat = self._create_heartbeat()
                self._metrics.record_keepalive()
                yield heartbeat
            except asyncio.CancelledError:
                break

    async def _enqueue_message(self, msg: Any) -> None:
        """Enqueue message for sending."""
        try:
            await asyncio.wait_for(
                self._queue.put(msg),
                timeout=self.QUEUE_PUT_TIMEOUT,
            )
        except asyncio.TimeoutError:
            raise RuntimeError("Message queue full")

    # =========================================================================
    # Internal: Receive Loop
    # =========================================================================

    async def _receive_loop(self) -> None:
        """
        Receive and process incoming messages.

        Runs until stream closes or error occurs.
        """
        try:
            async for message in self._stream:
                await self._handle_message(message)
                self._metrics.record_received(message.ByteSize())
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._metrics.record_error()
            if self._state == StreamState.CONNECTED:
                self._state = StreamState.ERROR
                if self._on_error:
                    await self._invoke_callback(
                        self._on_error,
                        "STREAM_ERROR",
                        str(e),
                        True,
                    )

    async def _handle_message(self, message: Any) -> None:
        """
        Handle incoming ControlMessage.

        Args:
            message: ControlMessage proto object.
        """
        # Determine message type from oneof payload
        payload_type = message.WhichOneof("payload")

        if payload_type == "input":
            # Terminal input from server (output to display)
            output = OutputData(
                data=message.input.data,
                is_stderr=False,
                sequence=message.input.sequence,
            )
            if self._on_output:
                await self._invoke_callback(self._on_output, output.data)

        elif payload_type == "start_session":
            # Session started - mark ready and invoke status callback
            self._session_ready.set()
            if self._on_status:
                await self._invoke_callback(
                    self._on_status,
                    StatusData(
                        old_status="registering",
                        new_status="connected",
                        reason="session_started",
                    ),
                )

        elif payload_type == "close_session":
            # Session closed by server
            reason = message.close_session.reason
            await self.close(reason)

        elif payload_type == "signal":
            # Signal forwarded from server
            signal_num = message.signal.signal
            if self._settings.log_level == "DEBUG":
                import logging

                logging.getLogger(__name__).debug(
                    f"Received signal from server: {signal_num}"
                )

        elif payload_type == "ping":
            # Ping from server - respond with heartbeat to keep connection alive
            heartbeat = self._create_heartbeat()
            await self._enqueue_message(heartbeat)
            self._metrics.record_keepalive()

        elif payload_type == "resize":
            # Resize command from server (terminal dimensions changed)
            if hasattr(message.resize, "size"):
                cols = message.resize.size.cols
                rows = message.resize.size.rows
                if self._on_status:
                    await self._invoke_callback(
                        self._on_status,
                        StatusData(
                            old_status="connected",
                            new_status="connected",
                            reason=f"resize:{cols}x{rows}",
                        ),
                    )

        elif payload_type == "get_history":
            # History response from server
            if hasattr(message.get_history, "commands"):
                commands = list(message.get_history.commands)
                total = getattr(message.get_history, "total", len(commands))
                if self._on_history:
                    await self._invoke_callback(
                        self._on_history,
                        HistoryData(commands=commands, total=total),
                    )

        elif payload_type == "config_update":
            # Configuration update from server
            if self._settings.log_level == "DEBUG":
                import logging

                logging.getLogger(__name__).debug("Received config update from server")

        elif payload_type == "cancel":
            # Cancel command from server
            if hasattr(message.cancel, "command_id"):
                command_id = message.cancel.command_id
                if self._settings.log_level == "DEBUG":
                    import logging

                    logging.getLogger(__name__).debug(
                        f"Received cancel for command: {command_id}"
                    )

        else:
            # Unknown message type - log in debug mode
            if self._settings.log_level == "DEBUG":
                import logging

                logging.getLogger(__name__).warning(
                    f"Unknown message type: {payload_type}"
                )


    # =========================================================================
    # Internal: Message Creation
    # =========================================================================

    async def _send_register(self) -> None:
        """Send registration message."""
        from cmdop._generated.agent_messages_pb2 import AgentMessage, RegisterRequest
        from cmdop._generated.common_types_pb2 import TerminalSize

        import platform
        import os

        register = RegisterRequest(
            version="sdk-python-0.1.0",
            hostname=platform.node(),
            platform=platform.system().lower(),
            initial_size=TerminalSize(cols=80, rows=24),
            username=os.getenv("USER", "unknown"),
            home_dir=os.path.expanduser("~"),
        )

        msg = AgentMessage(
            session_id=self._session_id,
            message_id=self._next_message_id(),
            register=register,
        )

        await self._enqueue_message(msg)

    def _create_heartbeat(self) -> Any:
        """Create heartbeat message."""
        from cmdop._generated.agent_messages_pb2 import AgentMessage, HeartbeatUpdate

        return AgentMessage(
            session_id=self._session_id,
            message_id=self._next_message_id(),
            heartbeat=HeartbeatUpdate(),
        )

    def _next_message_id(self) -> str:
        """Generate next message ID."""
        self._message_id += 1
        return f"{self._session_id}-{self._message_id}"

    # =========================================================================
    # Internal: Callback Invocation
    # =========================================================================

    async def _invoke_callback(self, callback: Any, *args: Any) -> None:
        """
        Safely invoke callback.

        Handles both sync and async callbacks.
        """
        try:
            result = callback(*args)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            # Log callback errors in debug mode
            if self._settings.log_level == "DEBUG":
                import logging

                logging.getLogger(__name__).error(
                    f"Callback error: {e}", exc_info=True
                )

    # =========================================================================
    # Context Manager
    # =========================================================================

    async def __aenter__(self) -> TerminalStream:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, *_args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        return (
            f"<TerminalStream "
            f"session_id={self._session_id} "
            f"state={self._state.value}>"
        )
