"""
Tests for SSH-like terminal connection.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cmdop.services.terminal.tui.ssh import ssh_connect, ssh_execute


# Path to patch - the import happens inside the function
CMDOP_CLIENT_PATH = "cmdop.services.terminal.tui.ssh.AsyncCMDOPClient"


class TestSshConnect:
    """Test ssh_connect() function."""

    async def test_ssh_connect_no_tty(self):
        """ssh_connect returns 1 if not TTY."""
        with patch("cmdop.services.terminal.tui.ssh.is_tty", return_value=False):
            result = await ssh_connect("test-host", "api-key")
            assert result == 1

    async def test_ssh_connect_no_session_found(self):
        """ssh_connect returns 1 if no session found."""
        # Need to patch at the place where it's imported (inside the function)
        with patch("cmdop.services.terminal.tui.ssh.is_tty", return_value=True):
            # Patch the module-level import that happens inside ssh_connect
            with patch.dict("sys.modules", {"cmdop": MagicMock()}):
                with patch("cmdop.AsyncCMDOPClient") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client_class.remote.return_value.__aenter__.return_value = mock_client
                    mock_client.terminal.get_active_session = AsyncMock(return_value=None)

                    result = await ssh_connect("nonexistent-host", "api-key")
                    assert result == 1

    async def test_ssh_connect_connection_failed(self):
        """ssh_connect returns 1 if connection fails."""
        with patch("cmdop.services.terminal.tui.ssh.is_tty", return_value=True):
            with patch("cmdop.AsyncCMDOPClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.remote.return_value.__aenter__.return_value = mock_client

                # Mock session found
                mock_session = MagicMock()
                mock_session.session_id = "session-123"
                mock_session.machine_hostname = "test-host"
                mock_client.terminal.get_active_session = AsyncMock(return_value=mock_session)

                # Mock stream that fails to connect
                mock_stream = MagicMock()
                mock_stream.on_output = MagicMock(return_value=mock_stream)
                mock_stream.on_error = MagicMock(return_value=mock_stream)
                mock_stream.on_disconnect = MagicMock(return_value=mock_stream)
                mock_stream.connect = AsyncMock(side_effect=Exception("Connection failed"))
                mock_client.terminal.stream.return_value = mock_stream

                result = await ssh_connect("test-host", "api-key")
                assert result == 1

    async def test_ssh_connect_with_session_id(self):
        """ssh_connect uses provided session_id."""
        with patch("cmdop.services.terminal.tui.ssh.is_tty", return_value=True):
            with patch("cmdop.AsyncCMDOPClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.remote.return_value.__aenter__.return_value = mock_client

                # Mock stream (must have all callback methods)
                mock_stream = MagicMock()
                mock_stream.on_output = MagicMock(return_value=mock_stream)
                mock_stream.on_error = MagicMock(return_value=mock_stream)
                mock_stream.on_disconnect = MagicMock(return_value=mock_stream)
                mock_stream.connect = AsyncMock()
                mock_stream.wait_ready = AsyncMock()
                mock_stream.is_connected = False  # Will exit loop
                mock_stream.close = AsyncMock()
                mock_stream._shutdown = MagicMock()
                mock_stream._shutdown.set = MagicMock()
                mock_client.terminal.stream.return_value = mock_stream

                # Should NOT call get_active_session when session_id provided
                with patch("cmdop.services.terminal.tui.ssh._run_terminal_loop", new_callable=AsyncMock) as mock_loop:
                    mock_loop.return_value = 0

                    await ssh_connect(
                        "test-host",
                        "api-key",
                        session_id="explicit-session-id"
                    )

                    # get_active_session should not be called
                    mock_client.terminal.get_active_session.assert_not_called()


class TestSshExecute:
    """Test ssh_execute() function."""

    async def test_ssh_execute_no_session(self):
        """ssh_execute raises if no session found."""
        with patch("cmdop.AsyncCMDOPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.remote.return_value.__aenter__.return_value = mock_client
            mock_client.terminal.get_active_session = AsyncMock(return_value=None)

            with pytest.raises(ValueError) as exc_info:
                await ssh_execute("test-host", "ls -la", "api-key")

            assert "no active session" in str(exc_info.value).lower()

    async def test_ssh_execute_success(self):
        """ssh_execute returns output and exit code."""
        with patch("cmdop.AsyncCMDOPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.remote.return_value.__aenter__.return_value = mock_client

            # Mock session found
            mock_session = MagicMock()
            mock_session.session_id = "session-123"
            mock_client.terminal.get_active_session = AsyncMock(return_value=mock_session)

            # Mock execute
            mock_client.terminal.execute = AsyncMock(return_value=(b"file1\nfile2\n", 0))

            output, code = await ssh_execute("test-host", "ls", "api-key")

            assert output == b"file1\nfile2\n"
            assert code == 0

    async def test_ssh_execute_with_timeout(self):
        """ssh_execute passes timeout to execute."""
        with patch("cmdop.AsyncCMDOPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.remote.return_value.__aenter__.return_value = mock_client

            mock_session = MagicMock()
            mock_session.session_id = "session-123"
            mock_client.terminal.get_active_session = AsyncMock(return_value=mock_session)
            mock_client.terminal.execute = AsyncMock(return_value=(b"", 0))

            await ssh_execute("test-host", "ls", "api-key", timeout=60.0)

            mock_client.terminal.execute.assert_called_once_with(
                "ls",
                timeout=60.0,
                session_id="session-123",
            )
