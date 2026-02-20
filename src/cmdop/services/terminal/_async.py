"""
Asynchronous terminal service implementation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from cmdop.models.terminal import (
    HistoryResponse,
    SessionInfo,
    SessionListItem,
    SessionListResponse,
    SessionMode,
    SessionState,
    SessionStatus,
    SignalType,
)
from cmdop.services.base import BaseService
from cmdop.services.terminal._helpers import get_signal_number

if TYPE_CHECKING:
    from cmdop.streaming.terminal import TerminalStream
    from cmdop.transport.base import BaseTransport


class AsyncTerminalService(BaseService):
    """
    Asynchronous terminal service.

    Provides async operations for terminal session management.
    Most methods support auto-detection of session_id when not provided.

    Example:
        >>> # Auto session detection - SDK handles session automatically
        >>> output, code = await client.terminal.execute("ls -la")
        >>> history = await client.terminal.get_history()
        >>>
        >>> # Or explicit session control
        >>> session = await client.terminal.get_active_session()
        >>> await client.terminal.send_input(b"ls\\n", session_id=session.session_id)
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None
        self._cached_session_id: str | None = None
        self._cached_hostname: str | None = None
        self._cached_session_info: SessionListItem | None = None

    # -------------------------------------------------------------------------
    # Machine & Session Management
    # -------------------------------------------------------------------------

    async def set_machine(self, hostname: str, partial_match: bool = True) -> SessionListItem:
        """
        Set the target machine by hostname and cache its session.

        Uses GetSessionByHostname RPC for efficient server-side resolution.
        Finds the most recently active session on the specified machine
        and caches both hostname and session_id for all subsequent operations.

        Args:
            hostname: Machine hostname.
            partial_match: If True, allows partial hostname matching (default).
                          If False, requires exact hostname match.

        Returns:
            SessionListItem for the found session.

        Raises:
            CMDOPError: If no active session found, or hostname is ambiguous
                       (matches multiple machines when partial_match=True).

        Example:
            >>> await client.terminal.set_machine("my-server")
            >>> # Now all operations target this machine
            >>> output, code = await client.terminal.execute("ls")
            >>> await client.terminal.send_input("echo hello\\n")

            >>> # Exact match to avoid ambiguity
            >>> await client.terminal.set_machine("prod-server-1", partial_match=False)
        """
        from cmdop.grpc.generated.rpc_messages.session_pb2 import (
            GetSessionByHostnameRequest,
        )
        from cmdop.exceptions import CMDOPError

        request = GetSessionByHostnameRequest(
            hostname=hostname,
            partial_match=partial_match,
        )
        response = await self._call_async(self._get_stub.GetSessionByHostname, request)

        if not response.found:
            if response.ambiguous:
                raise CMDOPError(
                    f"Ambiguous hostname '{hostname}' matches {response.matches_count} machines. "
                    "Use a more specific hostname or set partial_match=False for exact match."
                )
            raise CMDOPError(response.error or f"No active session found for hostname: {hostname}")

        # Parse connected_at timestamp
        connected_at = None
        if response.connected_at and response.connected_at.seconds > 0:
            connected_at = datetime.fromtimestamp(
                response.connected_at.seconds, tz=timezone.utc
            )

        # Build SessionListItem from response
        session = SessionListItem(
            session_id=response.session_id,
            machine_hostname=response.machine_hostname,
            machine_name=response.machine_name,
            status=response.status,
            os=response.os,
            agent_version=response.agent_version,
            heartbeat_age_seconds=response.heartbeat_age_seconds,
            has_shell=response.has_shell,
            shell=response.shell,
            working_directory=response.working_directory,
            connected_at=connected_at,
        )

        # Cache session info
        self._cached_hostname = response.machine_hostname
        self._cached_session_id = response.session_id
        self._cached_session_info = session
        return session

    async def _resolve_session_id(self, session_id: str | None) -> str | None:
        """
        Resolve session_id, using cache or auto-detecting if None.

        Resolution order:
        1. Explicit session_id parameter
        2. Cached session_id (from set_machine or set_session_id)
        3. Auto-detect from cached hostname (requires set_machine() first)

        Returns None if no session found or hostname not set.
        """
        if session_id is not None:
            self._cached_session_id = session_id
            return session_id

        if self._cached_session_id is not None:
            return self._cached_session_id

        # Auto-detect requires hostname to be set
        if self._cached_hostname is None:
            return None

        session = await self.get_active_session(self._cached_hostname)
        if session:
            self._cached_session_id = session.session_id
            self._cached_session_info = session
            return session.session_id

        return None

    def set_session_id(self, session_id: str) -> None:
        """
        Set the default session_id for all operations.

        Use this to pre-set the session once. For targeting a specific
        machine, prefer set_machine() which also validates the session exists.

        Args:
            session_id: Session ID to use for all operations.

        Example:
            >>> session = await client.terminal.get_active_session("my-server")
            >>> client.terminal.set_session_id(session.session_id)
            >>> await client.terminal.send_input(b"ls\\n")
        """
        self._cached_session_id = session_id

    def clear_session(self) -> None:
        """Clear cached session and hostname, forcing auto-detection on next call."""
        self._cached_session_id = None
        self._cached_hostname = None
        self._cached_session_info = None

    def clear_session_id(self) -> None:
        """Clear cached session_id only. Alias for clear_session()."""
        self.clear_session()

    @property
    def current_session(self) -> SessionListItem | None:
        """Get the currently cached session info, if any."""
        return self._cached_session_info

    @property
    def current_hostname(self) -> str | None:
        """Get the currently cached hostname filter, if any."""
        return self._cached_hostname

    # -------------------------------------------------------------------------
    # gRPC Stub
    # -------------------------------------------------------------------------

    @property
    def _get_stub(self) -> Any:
        """Lazy-load async gRPC stub."""
        if self._stub is None:
            from cmdop.grpc.generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._async_channel)
        return self._stub

    # -------------------------------------------------------------------------
    # Session Operations
    # -------------------------------------------------------------------------

    async def create(
        self,
        shell: str = "/bin/bash",
        cols: int = 80,
        rows: int = 24,
        env: dict[str, str] | None = None,
        working_dir: str | None = None,
        mode: SessionMode = SessionMode.EXCLUSIVE,
    ) -> SessionInfo:
        """Create a new terminal session."""
        from cmdop.grpc.generated.common_types_pb2 import SessionConfig, TerminalSize
        from cmdop.grpc.generated.rpc_messages.session_pb2 import (
            CreateSessionRequest as PbRequest,
        )

        config = SessionConfig(
            shell=shell,
            working_directory=working_dir or "",
            size=TerminalSize(cols=cols, rows=rows),
        )
        if env:
            for k, v in env.items():
                config.env[k] = v

        request = PbRequest(config=config)
        response = await self._call_async(self._get_stub.CreateSession, request)

        return SessionInfo(
            session_id=response.session_id,
            state=SessionState.ACTIVE,
            mode=mode,
            shell=shell,
            cols=cols,
            rows=rows,
            working_dir=working_dir,
            created_at=datetime.now(timezone.utc),
        )

    async def close(
        self,
        session_id: str | None = None,
        force: bool = False,  # noqa: ARG002
    ) -> None:
        """
        Close terminal session.

        Args:
            session_id: Session UUID to close. If None, closes cached/active session.
            force: Force kill if graceful close fails.

        Raises:
            CMDOPError: If no session found and session_id not provided.
        """
        from cmdop.grpc.generated.rpc_messages.session_pb2 import CloseSessionRequest

        resolved_id = await self._resolve_session_id(session_id)
        if resolved_id is None:
            from cmdop.exceptions import CMDOPError

            raise CMDOPError("No active session found")

        request = CloseSessionRequest(session_id=resolved_id)
        await self._call_async(self._get_stub.CloseSession, request)

        if self._cached_session_id == resolved_id:
            self._cached_session_id = None

    # -------------------------------------------------------------------------
    # Terminal I/O
    # -------------------------------------------------------------------------

    async def send_input(
        self,
        data: bytes | str,
        session_id: str | None = None,
    ) -> None:
        """
        Send input to terminal session.

        Args:
            data: Input bytes or string to send.
            session_id: Target session UUID. If None, auto-detects active session.

        Raises:
            CMDOPError: If no session found and session_id not provided.

        Example:
            >>> await client.terminal.send_input("ls\\n")
            >>> await client.terminal.send_input("ls\\n", session_id="...")
        """
        from cmdop.grpc.generated.rpc_messages.terminal_pb2 import SendInputRequest

        resolved_id = await self._resolve_session_id(session_id)
        if resolved_id is None:
            from cmdop.exceptions import CMDOPError

            raise CMDOPError("No active session found")

        if isinstance(data, str):
            data = data.encode("utf-8")

        request = SendInputRequest(session_id=resolved_id, data=data)
        await self._call_async(self._get_stub.SendInput, request)

    async def resize(
        self,
        cols: int,
        rows: int,
        session_id: str | None = None,
    ) -> None:
        """
        Resize terminal window.

        Args:
            cols: New width in columns.
            rows: New height in rows.
            session_id: Target session UUID. If None, auto-detects active session.

        Raises:
            CMDOPError: If no session found and session_id not provided.
        """
        from cmdop.grpc.generated.rpc_messages.terminal_pb2 import SendResizeRequest

        resolved_id = await self._resolve_session_id(session_id)
        if resolved_id is None:
            from cmdop.exceptions import CMDOPError

            raise CMDOPError("No active session found")

        request = SendResizeRequest(session_id=resolved_id, cols=cols, rows=rows)
        await self._call_async(self._get_stub.SendResize, request)

    async def send_signal(
        self,
        signal: SignalType,
        session_id: str | None = None,
    ) -> None:
        """
        Send signal to terminal session.

        Args:
            signal: Signal to send (SIGINT, SIGTERM, etc.).
            session_id: Target session UUID. If None, auto-detects active session.

        Raises:
            CMDOPError: If no session found and session_id not provided.
        """
        from cmdop.grpc.generated.rpc_messages.terminal_pb2 import SendSignalRequest

        resolved_id = await self._resolve_session_id(session_id)
        if resolved_id is None:
            from cmdop.exceptions import CMDOPError

            raise CMDOPError("No active session found")

        request = SendSignalRequest(
            session_id=resolved_id,
            signal=get_signal_number(signal),
        )
        await self._call_async(self._get_stub.SendSignal, request)

    async def get_history(
        self,
        session_id: str | None = None,
        lines: int = 1000,
        offset: int = 0,
    ) -> HistoryResponse:
        """
        Get terminal output history.

        Args:
            session_id: Target session UUID. If None, auto-detects active session.
            lines: Number of lines to retrieve.
            offset: Start offset for pagination.

        Returns:
            History response with output data.

        Raises:
            CMDOPError: If no session found and session_id not provided.
        """
        from cmdop.grpc.generated.rpc_messages.history_pb2 import GetHistoryRequest

        resolved_id = await self._resolve_session_id(session_id)
        if resolved_id is None:
            from cmdop.exceptions import CMDOPError

            raise CMDOPError("No active session found")

        request = GetHistoryRequest(
            session_id=resolved_id,
            limit=lines,
            offset=offset,
        )
        response = await self._call_async(self._get_stub.GetHistory, request)

        return HistoryResponse(
            session_id=resolved_id,
            data=response.data
            if hasattr(response, "data")
            else b"".join(c.encode() for c in response.commands),
            total_lines=response.total if hasattr(response, "total") else lines,
            has_more=False,
        )

    async def get_output(
        self,
        session_id: str | None = None,
        limit: int = 0,
        offset: int = 0,
    ) -> bytes:
        """
        Get terminal output buffer (raw PTY output).

        Retrieves terminal output from Django's Redis buffer.
        This is different from get_history() which returns command strings.

        Args:
            session_id: Target session UUID. If None, auto-detects active session.
            limit: Max bytes to return (0 = default 1MB).
            offset: Byte offset to start from.

        Returns:
            Raw terminal output bytes.

        Raises:
            CMDOPError: If no session found and session_id not provided.
        """
        from cmdop.grpc.generated.rpc_messages.history_pb2 import GetOutputRequest

        resolved_id = await self._resolve_session_id(session_id)
        if resolved_id is None:
            from cmdop.exceptions import CMDOPError

            raise CMDOPError("No active session found")

        request = GetOutputRequest(
            session_id=resolved_id,
            limit=limit,
            offset=offset,
        )
        response = await self._call_async(self._get_stub.GetOutput, request)

        return response.data if response.data else b""

    # -------------------------------------------------------------------------
    # Streaming
    # -------------------------------------------------------------------------

    def stream(self) -> TerminalStream:
        """
        Create a bidirectional terminal stream.

        Returns a TerminalStream that manages real-time terminal I/O
        via gRPC bidirectional streaming.

        **IMPORTANT: Remote mode only!**
        Streaming requires cloud relay connection (RemoteTransport).
        Local connections will raise RuntimeError on connect().
        For local mode, use send_input(), get_history() methods instead.

        Usage (remote mode):
            >>> async with AsyncCMDOPClient.remote(api_key="xxx") as client:
            ...     async with client.terminal.stream() as stream:
            ...         stream.on_output(lambda data: print(data.decode(), end=""))
            ...         await stream.send_input(b"ls\\n")

        Returns:
            TerminalStream instance (not yet connected).

        Raises:
            RuntimeError: On connect() if using local transport.

        Note:
            Call `await stream.connect()` or use as context manager
            to establish the connection.
        """
        from cmdop.streaming.terminal import TerminalStream

        return TerminalStream(self._transport)

    def attach_stream(self, session_id: str) -> TerminalStream:
        """
        Create a terminal stream attached to an existing agent session.

        Unlike stream() which creates a new session, attach_stream()
        connects to an existing agent session to receive terminal output.

        **IMPORTANT:** You must use `await stream.attach(session_id)` to connect,
        NOT `await stream.connect()`.

        Usage:
            >>> session = await client.terminal.get_active_session()
            >>> if session:
            ...     stream = client.terminal.attach_stream(session.session_id)
            ...     await stream.attach(session.session_id)
            ...     stream.on_output(lambda data: print(data.decode(), end=""))

        Args:
            session_id: Existing agent session ID to attach to.

        Returns:
            TerminalStream instance (call attach() to connect).
        """
        from cmdop.streaming.terminal import TerminalStream

        return TerminalStream(self._transport)

    # -------------------------------------------------------------------------
    # Command Execution
    # -------------------------------------------------------------------------

    async def execute(
        self,
        command: str,
        timeout: float = 30.0,
        session_id: str | None = None,
    ) -> tuple[bytes, int]:
        """
        Execute a command and return output.

        Wraps command with START/END markers, sends to terminal, polls output
        buffer until END marker appears, then extracts clean output.

        Requires either:
        - Explicit session_id parameter, OR
        - Prior call to set_machine() to set target hostname

        Args:
            command: Command to execute (shell command string).
            timeout: Maximum time to wait for command completion (default: 30s).
            session_id: Session ID to use. If None, uses cached session.

        Returns:
            Tuple of (output_bytes, exit_code).
            - exit_code: 0+ on success, -1 on timeout or error.

        Troubleshooting:
            - Timeout (-1): Increase timeout for slow commands, or check if
              another terminal client is consuming the output buffer.
            - Empty output: The output buffer has a 20KB limit per poll.
              For commands with large output, use stream() instead.
            - No session: Call set_machine("hostname") first.

        Example:
            >>> await client.terminal.set_machine("my-server")
            >>> output, code = await client.terminal.execute("ls -la")
            >>> print(output.decode())

            >>> # With explicit timeout for slow commands
            >>> output, code = await client.terminal.execute(
            ...     "apt update", timeout=120.0
            ... )
        """
        import asyncio

        from cmdop.exceptions import CMDOPError

        resolved_id = await self._resolve_session_id(session_id)
        if resolved_id is None:
            return b"No session. Call set_machine() first or provide session_id.", -1
        session_id = resolved_id

        import re
        import uuid

        # =====================================================================
        # MARKER SYSTEM
        # =====================================================================
        # We wrap the user's command with START/END markers to reliably extract
        # output from the terminal buffer. Format is Django-compatible:
        #   <<CMD:uuid:START>>
        #   <command output>
        #   <<CMD:uuid:END:exit_code>>
        #
        # The UUID ensures we find output for THIS specific command even if
        # the buffer contains output from multiple commands.
        # =====================================================================
        cmd_id = uuid.uuid4().hex[:12]
        start_marker = f"<<CMD:{cmd_id}:START>>"
        end_marker_prefix = f"<<CMD:{cmd_id}:END:"

        # Build wrapped command:
        # 1. printf START marker with newlines
        # 2. Execute user's command
        # 3. printf END marker with $? (exit code) embedded
        full_cmd = (
            f'printf "\\n{start_marker}\\n"; '
            f'{command}; '
            f'printf "\\n{end_marker_prefix}%d>>\\n" $?\n'
        )

        try:
            await self.send_input(full_cmd.encode(), session_id=session_id)
        except CMDOPError as e:
            return f"Failed to send command: {e.message}".encode(), -1

        # =====================================================================
        # POLLING LOOP
        # =====================================================================
        # Poll the output buffer every 200ms until END marker appears.
        # Buffer limit is 20KB - sufficient for most commands.
        # For large output (logs, dumps), consider using stream() instead.
        # =====================================================================
        start_time = asyncio.get_event_loop().time()
        start_marker_bytes = start_marker.encode()
        end_pattern = re.compile(rf"<<CMD:{cmd_id}:END:(\d+)>>".encode())

        while True:
            await asyncio.sleep(0.2)  # Poll interval - balance between latency and load

            try:
                # Fetch recent terminal output (20KB should capture most commands)
                full_output = await self.get_output(session_id, limit=20 * 1024)
            except CMDOPError as e:
                return f"Failed to get output: {e.message}".encode(), -1

            # Check for END marker with exit code
            end_match = end_pattern.search(full_output)
            if end_match and start_marker_bytes in full_output:
                # Extract exit code
                exit_code = int(end_match.group(1))

                # Extract output between markers
                # Find the START marker that corresponds to this command's END marker
                # (must be before the END marker position)
                end_pos = end_match.start()

                # Find the last START marker before the END marker
                search_region = full_output[:end_pos]
                start_idx = search_region.rfind(start_marker_bytes)

                if start_idx != -1:
                    # Skip past the START marker line (handle both \n and \r\n)
                    content_start = start_idx + len(start_marker_bytes)
                    # Skip any trailing \r\n after marker
                    while content_start < end_pos and full_output[content_start:content_start+1] in (b"\r", b"\n"):
                        content_start += 1

                    # Content ends at END marker
                    content_end = end_pos

                    # Extract raw content between markers
                    raw_content = full_output[content_start:content_end]

                    # =========================================================
                    # OUTPUT FILTERING
                    # =========================================================
                    # Terminal output contains noise we need to filter:
                    # 1. Command echo - shell echoes back what we typed
                    # 2. Marker lines - our <<CMD:...>> markers
                    # 3. Prompt lines - user@host:path$ patterns
                    # =========================================================
                    lines = raw_content.split(b"\n")
                    filtered_lines: list[bytes] = []

                    # Pattern to detect echoed command (contains our printf)
                    full_cmd_pattern = b'printf "' + start_marker_bytes

                    for line in lines:
                        # Skip marker lines
                        if b"<<CMD:" in line:
                            continue
                        # Skip command echo (shell repeating our input)
                        if full_cmd_pattern in line:
                            continue
                        # Skip shell prompt lines (user@host:path$ or similar)
                        stripped = line.strip()
                        if stripped and (
                            stripped.endswith(b"$")
                            or stripped.endswith(b"#")
                            or stripped.endswith(b">")
                        ):
                            if b"@" in stripped or b":" in stripped:
                                continue
                        filtered_lines.append(line)

                    # Remove carriage returns
                    output = b"\n".join(filtered_lines)
                    output = output.replace(b"\r", b"")

                    # Remove empty lines at start/end only
                    lines = output.split(b"\n")
                    while lines and not lines[0].strip():
                        lines = lines[1:]
                    while lines and not lines[-1].strip():
                        lines = lines[:-1]
                    output = b"\n".join(lines)

                    return output, exit_code

                return b"", exit_code

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                # Timeout - provide detailed troubleshooting message
                has_start = start_marker_bytes in full_output
                has_end = end_pattern.search(full_output) is not None

                hints = []
                if not has_start and not has_end:
                    hints.append("No markers found - command may not have been sent")
                    hints.append("Check: Is the terminal session active?")
                elif has_start and not has_end:
                    hints.append("START marker found but END marker missing")
                    hints.append("The command is still running or was interrupted")
                    hints.append("Try: Increase timeout parameter")

                timeout_msg = f"[CMDOP] Command timed out after {timeout}s.\n".encode()
                if hints:
                    timeout_msg += b"Hints:\n" + b"\n".join(f"  - {h}".encode() for h in hints) + b"\n"

                # Try to extract partial output if START marker exists
                if has_start:
                    start_idx = full_output.rfind(start_marker_bytes)
                    content_start = start_idx + len(start_marker_bytes)
                    while content_start < len(full_output) and full_output[content_start:content_start+1] in (b"\r", b"\n"):
                        content_start += 1
                    partial = full_output[content_start:].replace(b"\r", b"").strip()
                    # Limit partial output to avoid huge dumps
                    if partial and len(partial) < 2000:
                        timeout_msg += b"Partial output:\n" + partial + b"\n"

                return timeout_msg, -1

    # -------------------------------------------------------------------------
    # Session Discovery
    # -------------------------------------------------------------------------

    async def list_sessions(
        self,
        hostname: str | None = None,
        status: str | None = None,
        limit: int = 20,
    ) -> SessionListResponse:
        """
        List terminal sessions in workspace (v2.14.0).

        Returns sessions visible to the authenticated API key's workspace.

        Args:
            hostname: Optional filter by machine hostname (partial match).
            status: Optional filter by status ("connected", "disconnected").
            limit: Maximum sessions to return (default: 20).

        Returns:
            SessionListResponse with list of sessions.

        Example:
            >>> response = await client.terminal.list_sessions(status="connected")
            >>> for s in response.sessions:
            ...     print(f"{s.machine_hostname}: {s.status}")
        """
        from cmdop.grpc.generated.rpc_messages.session_pb2 import ListSessionsRequest

        request = ListSessionsRequest(
            hostname_filter=hostname or "",
            status_filter=status or "",
            limit=limit,
        )

        response = await self._call_async(self._get_stub.ListSessions, request)

        if response.error:
            from cmdop.exceptions import CMDOPError

            raise CMDOPError(response.error)

        sessions = []
        for s in response.sessions:
            connected_at = None
            if s.connected_at and s.connected_at.seconds > 0:
                connected_at = datetime.fromtimestamp(
                    s.connected_at.seconds, tz=timezone.utc
                )

            sessions.append(
                SessionListItem(
                    session_id=s.session_id,
                    machine_hostname=s.machine_hostname,
                    machine_name=s.machine_name,
                    status=s.status,
                    os=s.os,
                    agent_version=s.agent_version,
                    heartbeat_age_seconds=s.heartbeat_age_seconds,
                    has_shell=s.has_shell,
                    shell=s.shell,
                    working_directory=s.working_directory,
                    connected_at=connected_at,
                )
            )

        return SessionListResponse(
            sessions=sessions,
            total=response.total,
            workspace_name=response.workspace_name,
        )

    async def list_active_sessions(
        self,
        hostname: str,
        limit: int = 100,
    ) -> list[SessionListItem]:
        """
        List active (connected) sessions for a specific machine.

        Filters for connected sessions and sorts by heartbeat_age_seconds
        (lower = more recently active).

        Args:
            hostname: Machine hostname filter (required, partial match).
            limit: Maximum sessions to return (default: 100).

        Returns:
            List of SessionListItem, sorted by most recent activity.

        Example:
            >>> sessions = await client.terminal.list_active_sessions("my-server")
            >>> for s in sessions:
            ...     print(f"{s.machine_hostname} ({s.heartbeat_age_seconds}s ago)")
        """
        response = await self.list_sessions(
            hostname=hostname,
            status=SessionStatus.CONNECTED.value,
            limit=limit,
        )

        return sorted(
            response.sessions,
            key=lambda s: s.heartbeat_age_seconds,
        )

    async def get_active_session(
        self,
        hostname: str | None = None,
    ) -> SessionListItem | None:
        """
        Get most recently active (connected) session for a specific machine.

        Returns the connected session with the lowest heartbeat_age_seconds,
        i.e., the one that was active most recently.

        Args:
            hostname: Machine hostname filter (partial match).
                     If None, uses cached hostname from set_machine().
                     If no hostname and no cache, returns None.

        Returns:
            SessionListItem if found, None otherwise.

        Example:
            >>> session = await client.terminal.get_active_session("my-server")
            >>> if session:
            ...     client.terminal.set_session_id(session.session_id)
        """
        # Use cached hostname if not provided
        if hostname is None:
            hostname = self._cached_hostname
        if hostname is None:
            return None

        sessions = await self.list_active_sessions(hostname, limit=1)
        return sessions[0] if sessions else None
