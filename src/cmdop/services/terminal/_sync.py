"""
Synchronous terminal service implementation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from cmdop.models.terminal import (
    HistoryResponse,
    SessionInfo,
    SessionMode,
    SessionState,
    SignalType,
)
from cmdop.services.base import BaseService
from cmdop.services.terminal._helpers import get_signal_number

if TYPE_CHECKING:
    from cmdop.transport.base import BaseTransport


class TerminalService(BaseService):
    """
    Synchronous terminal service.

    Provides operations for terminal session management.
    Requires explicit session_id for all operations.

    Example:
        >>> session = client.terminal.create()
        >>> client.terminal.send_input(session.session_id, b"ls\\n")
        >>> history = client.terminal.get_history(session.session_id)
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None

    @property
    def _get_stub(self) -> Any:
        """Lazy-load gRPC stub."""
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._channel)
        return self._stub

    def create(
        self,
        shell: str = "/bin/bash",
        cols: int = 80,
        rows: int = 24,
        env: dict[str, str] | None = None,
        working_dir: str | None = None,
        mode: SessionMode = SessionMode.EXCLUSIVE,
    ) -> SessionInfo:
        """
        Create a new terminal session.

        Args:
            shell: Shell executable path
            cols: Terminal width in columns
            rows: Terminal height in rows
            env: Additional environment variables
            working_dir: Initial working directory
            mode: Session access mode

        Returns:
            Created session info

        Raises:
            CMDOPError: On creation failure
        """
        from cmdop._generated.common_types_pb2 import SessionConfig, TerminalSize
        from cmdop._generated.rpc_messages.session_pb2 import (
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
        response = self._call_sync(self._get_stub.CreateSession, request)

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

    def send_input(self, session_id: str, data: bytes | str) -> None:
        """
        Send input to terminal session.

        Args:
            session_id: Target session UUID
            data: Input bytes or string to send
        """
        from cmdop._generated.rpc_messages.terminal_pb2 import SendInputRequest

        if isinstance(data, str):
            data = data.encode("utf-8")

        request = SendInputRequest(session_id=session_id, data=data)
        self._call_sync(self._get_stub.SendInput, request)

    def resize(self, session_id: str, cols: int, rows: int) -> None:
        """
        Resize terminal window.

        Args:
            session_id: Target session UUID
            cols: New width in columns
            rows: New height in rows
        """
        from cmdop._generated.rpc_messages.terminal_pb2 import SendResizeRequest

        request = SendResizeRequest(session_id=session_id, cols=cols, rows=rows)
        self._call_sync(self._get_stub.SendResize, request)

    def send_signal(self, session_id: str, signal: SignalType) -> None:
        """
        Send signal to terminal session.

        Args:
            session_id: Target session UUID
            signal: Signal to send
        """
        from cmdop._generated.rpc_messages.terminal_pb2 import SendSignalRequest

        request = SendSignalRequest(
            session_id=session_id,
            signal=get_signal_number(signal),
        )
        self._call_sync(self._get_stub.SendSignal, request)

    def close(
        self,
        session_id: str,
        force: bool = False,  # noqa: ARG002
    ) -> None:
        """
        Close terminal session.

        Args:
            session_id: Session UUID to close
            force: Force kill if graceful close fails
        """
        from cmdop._generated.rpc_messages.session_pb2 import CloseSessionRequest

        request = CloseSessionRequest(session_id=session_id)
        self._call_sync(self._get_stub.CloseSession, request)

    def get_history(
        self,
        session_id: str,
        lines: int = 1000,
        offset: int = 0,
    ) -> HistoryResponse:
        """
        Get terminal output history.

        Args:
            session_id: Target session UUID
            lines: Number of lines to retrieve
            offset: Start offset for pagination

        Returns:
            History response with output data
        """
        from cmdop._generated.rpc_messages.history_pb2 import GetHistoryRequest

        request = GetHistoryRequest(
            session_id=session_id,
            limit=lines,
            offset=offset,
        )
        response = self._call_sync(self._get_stub.GetHistory, request)

        return HistoryResponse(
            session_id=session_id,
            data=response.data
            if hasattr(response, "data")
            else b"".join(c.encode() for c in response.commands),
            total_lines=response.total if hasattr(response, "total") else lines,
            has_more=False,
        )
