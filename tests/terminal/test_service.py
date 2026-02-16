"""
Tests for Terminal service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cmdop.models.terminal import (
    SessionMode,
    SessionState,
    SignalType,
)
from cmdop.services.terminal import AsyncTerminalService, TerminalService


class TestTerminalServiceInit:
    """Test TerminalService initialization."""

    def test_service_creation(self):
        """Service can be created with transport."""
        transport = MagicMock()
        service = TerminalService(transport)
        assert service._transport is transport

    def test_stub_lazy_loaded(self):
        """gRPC stub is lazy loaded."""
        transport = MagicMock()
        service = TerminalService(transport)
        assert service._stub is None


class TestTerminalServiceCreate:
    """Test TerminalService.create() method."""

    def test_create_with_defaults(self):
        """create() uses default values."""
        transport = MagicMock()
        service = TerminalService(transport)

        mock_response = MagicMock()
        mock_response.session_id = "session-123"

        with patch.object(service, "_call_sync", return_value=mock_response):
            # Mock the stub by setting _stub directly
            service._stub = MagicMock()
            session = service.create()

            assert session.session_id == "session-123"
            assert session.shell == "/bin/bash"
            assert session.cols == 80
            assert session.rows == 24
            assert session.state == SessionState.ACTIVE

    def test_create_with_custom_values(self):
        """create() accepts custom values."""
        transport = MagicMock()
        service = TerminalService(transport)

        mock_response = MagicMock()
        mock_response.session_id = "session-456"

        with patch.object(service, "_call_sync", return_value=mock_response):
            service._stub = MagicMock()
            session = service.create(
                shell="/bin/zsh",
                cols=120,
                rows=40,
                env={"FOO": "bar"},
                working_dir="/home/user",
                mode=SessionMode.SHARED,
            )

            assert session.session_id == "session-456"
            assert session.shell == "/bin/zsh"
            assert session.cols == 120
            assert session.rows == 40
            assert session.mode == SessionMode.SHARED


class TestTerminalServiceSendInput:
    """Test TerminalService.send_input() method."""

    def test_send_input_bytes(self):
        """send_input accepts bytes."""
        transport = MagicMock()
        service = TerminalService(transport)
        service._stub = MagicMock()

        with patch.object(service, "_call_sync") as mock_call:
            service.send_input("session-123", b"hello")
            mock_call.assert_called_once()

    def test_send_input_string(self):
        """send_input converts string to bytes."""
        transport = MagicMock()
        service = TerminalService(transport)
        service._stub = MagicMock()

        with patch.object(service, "_call_sync") as mock_call:
            service.send_input("session-123", "hello")
            mock_call.assert_called_once()


class TestTerminalServiceResize:
    """Test TerminalService.resize() method."""

    def test_resize(self):
        """resize sends dimensions."""
        transport = MagicMock()
        service = TerminalService(transport)
        service._stub = MagicMock()

        with patch.object(service, "_call_sync") as mock_call:
            service.resize("session-123", 100, 50)
            mock_call.assert_called_once()


class TestTerminalServiceSendSignal:
    """Test TerminalService.send_signal() method."""

    def test_send_signal_sigint(self):
        """send_signal sends SIGINT."""
        transport = MagicMock()
        service = TerminalService(transport)
        service._stub = MagicMock()

        with patch.object(service, "_call_sync") as mock_call:
            service.send_signal("session-123", SignalType.SIGINT)
            mock_call.assert_called_once()

    def test_send_signal_sigterm(self):
        """send_signal sends SIGTERM."""
        transport = MagicMock()
        service = TerminalService(transport)
        service._stub = MagicMock()

        with patch.object(service, "_call_sync") as mock_call:
            service.send_signal("session-123", SignalType.SIGTERM)
            mock_call.assert_called_once()


class TestTerminalServiceClose:
    """Test TerminalService.close() method."""

    def test_close(self):
        """close sends close request."""
        transport = MagicMock()
        service = TerminalService(transport)
        service._stub = MagicMock()

        with patch.object(service, "_call_sync") as mock_call:
            service.close("session-123")
            mock_call.assert_called_once()


class TestTerminalServiceGetHistory:
    """Test TerminalService.get_history() method."""

    def test_get_history(self):
        """get_history returns history response."""
        transport = MagicMock()
        service = TerminalService(transport)
        service._stub = MagicMock()

        mock_response = MagicMock()
        mock_response.data = b"command output"
        mock_response.total = 100

        with patch.object(service, "_call_sync", return_value=mock_response):
            history = service.get_history("session-123", lines=50)

            assert history.session_id == "session-123"
            assert history.data == b"command output"


# =============================================================================
# Async Terminal Service Tests
# =============================================================================


class TestAsyncTerminalServiceInit:
    """Test AsyncTerminalService initialization."""

    def test_service_creation(self):
        """Service can be created with transport."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        assert service._transport is transport


class TestAsyncTerminalServiceCreate:
    """Test AsyncTerminalService.create() method."""

    async def test_create_with_defaults(self):
        """create() uses default values."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._stub = MagicMock()

        mock_response = MagicMock()
        mock_response.session_id = "session-123"

        with patch.object(service, "_call_async", new_callable=AsyncMock, return_value=mock_response):
            session = await service.create()

            assert session.session_id == "session-123"
            assert session.shell == "/bin/bash"


class TestAsyncTerminalServiceStream:
    """Test AsyncTerminalService.stream() method."""

    def test_stream_returns_terminal_stream(self):
        """stream() returns TerminalStream instance."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)

        stream = service.stream()

        from cmdop.streaming.terminal import TerminalStream
        assert isinstance(stream, TerminalStream)


class TestAsyncTerminalServiceExecute:
    """Test AsyncTerminalService.execute() method."""

    async def test_execute_requires_set_machine_or_session_id(self):
        """execute() returns error when no hostname set and no session_id."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)

        # No hostname set, no session_id provided
        output, code = await service.execute("ls", timeout=1.0)

        assert b"set_machine()" in output
        assert code == -1

    async def test_execute_uses_cached_hostname(self):
        """execute() uses cached hostname from set_machine()."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._stub = MagicMock()
        service._cached_hostname = "my-server"

        # Mock get_active_session
        mock_session = MagicMock()
        mock_session.session_id = "auto-session-123"

        # Mock send_input
        service.send_input = AsyncMock()

        # Mock get_output to return output with marker (returns bytes directly)
        marker_output = b"output\n__CMDOP_DONE_12345__0\n"

        with patch.object(service, "get_active_session", new_callable=AsyncMock, return_value=mock_session) as mock_get:
            with patch.object(service, "get_output", new_callable=AsyncMock, return_value=marker_output):
                await service.execute("ls", timeout=1.0)

                # Verify get_active_session was called with hostname
                mock_get.assert_called_once_with("my-server")

    async def test_execute_with_explicit_session_id(self):
        """execute() uses provided session_id."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._stub = MagicMock()

        # Mock send_input
        service.send_input = AsyncMock()

        # Mock get_output to return output with marker (returns bytes directly)
        marker_output = b"hello\n__CMDOP_DONE_12345__0\n"

        with patch.object(service, "get_active_session", new_callable=AsyncMock) as mock_get:
            with patch.object(service, "get_output", new_callable=AsyncMock, return_value=marker_output):
                output, code = await service.execute("echo hello", session_id="explicit-123", timeout=1.0)

                # Should NOT call get_active_session when session_id provided
                mock_get.assert_not_called()

    async def test_execute_extracts_exit_code(self):
        """execute() extracts exit code from marker."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._stub = MagicMock()
        service._cached_hostname = "my-server"

        # Mock send_input - capture the command to extract markers
        sent_commands = []
        async def mock_send_input(data, session_id=None):
            sent_commands.append(data)
        service.send_input = mock_send_input

        # Mock get_active_session
        mock_session = MagicMock()
        mock_session.session_id = "test-123"

        # Mock get_output: returns buffer with START/END markers (Django format)
        call_count = 0
        async def mock_get_output(session_id=None, limit=0, offset=0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return b""
            # Extract cmd_id from sent command (format: <<CMD:id:START>>)
            import re
            start_match = re.search(rb"<<CMD:([a-f0-9]+):START>>", sent_commands[0])
            if start_match:
                cmd_id = start_match.group(1).decode()
                # Return output with Django-format markers
                return f"<<CMD:{cmd_id}:START>>\nsome output\n<<CMD:{cmd_id}:END:0>>\n".encode()
            return b""

        with patch.object(service, "get_active_session", new_callable=AsyncMock, return_value=mock_session):
            with patch.object(service, "get_output", side_effect=mock_get_output):
                output, code = await service.execute("test", timeout=5.0)

                assert code == 0
                assert b"some output" in output

    async def test_execute_timeout(self):
        """execute() returns -1 on timeout."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._stub = MagicMock()
        service._cached_hostname = "my-server"

        # Mock get_active_session
        mock_session = MagicMock()
        mock_session.session_id = "test-123"

        # Mock send_input - capture the command to extract markers
        sent_commands = []
        async def mock_send_input(data, session_id=None):
            sent_commands.append(data)
        service.send_input = mock_send_input

        # Mock get_output: returns partial output with START but no END marker
        call_count = 0
        async def mock_get_output(session_id=None, limit=0, offset=0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return b""
            # Extract cmd_id and return partial output (no END marker)
            import re
            start_match = re.search(rb"<<CMD:([a-f0-9]+):START>>", sent_commands[0])
            if start_match:
                cmd_id = start_match.group(1).decode()
                return f"<<CMD:{cmd_id}:START>>\npartial output only".encode()
            return b"partial output only"

        with patch.object(service, "get_active_session", new_callable=AsyncMock, return_value=mock_session):
            with patch.object(service, "get_output", side_effect=mock_get_output):
                output, code = await service.execute("slow cmd", timeout=0.5)

                # Should timeout with -1
                assert code == -1
                # Check timeout message includes helpful hints
                assert b"[CMDOP]" in output
                assert b"timed out" in output
                assert b"START marker found but END marker missing" in output
                assert b"partial output" in output


class TestAsyncTerminalServiceListSessions:
    """Test AsyncTerminalService.list_sessions() method."""

    async def test_list_sessions(self):
        """list_sessions returns session list."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._stub = MagicMock()

        mock_session = MagicMock()
        mock_session.session_id = "session-1"
        mock_session.machine_hostname = "host1"
        mock_session.machine_name = "Host 1"
        mock_session.status = "connected"
        mock_session.os = "linux"
        mock_session.agent_version = "1.0.0"
        mock_session.heartbeat_age_seconds = 5
        mock_session.has_shell = True
        mock_session.shell = "/bin/bash"
        mock_session.working_directory = "/home/user"
        mock_session.connected_at.seconds = 0

        mock_response = MagicMock()
        mock_response.error = ""
        mock_response.sessions = [mock_session]
        mock_response.total = 1
        mock_response.workspace_name = "default"

        with patch.object(service, "_call_async", new_callable=AsyncMock, return_value=mock_response):
            response = await service.list_sessions()

            assert len(response.sessions) == 1
            assert response.sessions[0].session_id == "session-1"
            assert response.total == 1

    async def test_list_sessions_with_filters(self):
        """list_sessions accepts filters."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._stub = MagicMock()

        mock_response = MagicMock()
        mock_response.error = ""
        mock_response.sessions = []
        mock_response.total = 0
        mock_response.workspace_name = "default"

        with patch.object(service, "_call_async", new_callable=AsyncMock, return_value=mock_response) as mock_call:
            await service.list_sessions(
                hostname="myhost",
                status="connected",
                limit=10,
            )

            mock_call.assert_called_once()


class TestAsyncTerminalServiceGetActiveSession:
    """Test AsyncTerminalService.get_active_session() method."""

    async def test_get_active_session_found(self):
        """get_active_session returns session if found."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)

        mock_session = MagicMock()
        mock_session.session_id = "active-session"
        mock_session.machine_hostname = "host1"

        mock_response = MagicMock()
        mock_response.sessions = [mock_session]

        with patch.object(service, "list_sessions", new_callable=AsyncMock, return_value=mock_response):
            # hostname is now required
            session = await service.get_active_session("host1")

            assert session.session_id == "active-session"

    async def test_get_active_session_not_found(self):
        """get_active_session returns None if not found."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)

        mock_response = MagicMock()
        mock_response.sessions = []

        with patch.object(service, "list_sessions", new_callable=AsyncMock, return_value=mock_response):
            # hostname is now required
            session = await service.get_active_session("nonexistent")

            assert session is None


class TestAsyncTerminalServiceSetMachine:
    """Test AsyncTerminalService.set_machine() method."""

    async def test_set_machine_success(self):
        """set_machine caches session and hostname."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._stub = MagicMock()

        # Mock GetSessionByHostname RPC response
        mock_response = MagicMock()
        mock_response.found = True
        mock_response.session_id = "machine-session-123"
        mock_response.machine_hostname = "my-server"
        mock_response.machine_name = "My Server"
        mock_response.status = "connected"
        mock_response.os = "linux"
        mock_response.agent_version = "1.0.0"
        mock_response.heartbeat_age_seconds = 5
        mock_response.has_shell = True
        mock_response.shell = "/bin/bash"
        mock_response.working_directory = "/home/user"
        mock_response.connected_at.seconds = 0

        with patch.object(service, "_call_async", new_callable=AsyncMock, return_value=mock_response):
            result = await service.set_machine("my-server")

            assert result.session_id == "machine-session-123"
            assert service._cached_session_id == "machine-session-123"
            assert service._cached_hostname == "my-server"
            assert service.current_session is not None
            assert service.current_hostname == "my-server"

    async def test_set_machine_not_found_raises(self):
        """set_machine raises CMDOPError if no session found."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._stub = MagicMock()

        # Mock GetSessionByHostname RPC response - not found
        mock_response = MagicMock()
        mock_response.found = False
        mock_response.ambiguous = False
        mock_response.error = "No active session found for hostname: nonexistent-server"

        with patch.object(service, "_call_async", new_callable=AsyncMock, return_value=mock_response):
            from cmdop.exceptions import CMDOPError

            with pytest.raises(CMDOPError, match="No active session found"):
                await service.set_machine("nonexistent-server")

    async def test_clear_session(self):
        """clear_session clears all cached state."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)

        # Set some state
        service._cached_session_id = "some-id"
        service._cached_hostname = "some-host"
        service._cached_session_info = MagicMock()

        service.clear_session()

        assert service._cached_session_id is None
        assert service._cached_hostname is None
        assert service._cached_session_info is None

    async def test_resolve_session_uses_hostname_filter(self):
        """_resolve_session_id uses cached hostname for auto-detection."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)
        service._cached_hostname = "filtered-host"

        mock_session = MagicMock()
        mock_session.session_id = "filtered-session"

        with patch.object(service, "get_active_session", new_callable=AsyncMock, return_value=mock_session) as mock_get:
            result = await service._resolve_session_id(None)

            # Should pass hostname filter
            mock_get.assert_called_once_with("filtered-host")
            assert result == "filtered-session"

    async def test_resolve_session_returns_none_without_hostname(self):
        """_resolve_session_id returns None if no hostname set."""
        transport = MagicMock()
        service = AsyncTerminalService(transport)

        # No hostname set, no cached session
        result = await service._resolve_session_id(None)

        assert result is None
