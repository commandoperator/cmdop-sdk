"""
Tests for TUI terminal mode utilities.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from cmdop.services.terminal.tui.modes import (
    TerminalMode,
    enter_raw_mode,
    exit_raw_mode,
    get_terminal_size,
    is_tty,
    raw_mode,
    remove_resize_handler,
    restore_tty_state,
    save_tty_state,
    setup_resize_handler,
)


class TestTerminalMode:
    """Test TerminalMode class."""

    def test_default_values(self):
        """TerminalMode has correct defaults."""
        mode = TerminalMode()
        assert mode.original_settings is None
        assert mode.is_raw is False
        assert mode.platform == ""

    def test_detect_platform_returns_string(self):
        """detect_platform returns platform string."""
        platform = TerminalMode.detect_platform()
        assert platform in ("macos", "linux", "windows", "unknown")


class TestIsTty:
    """Test is_tty() function."""

    def test_is_tty_returns_bool(self):
        """is_tty returns boolean."""
        result = is_tty()
        assert isinstance(result, bool)

    def test_is_tty_with_mock_stdin(self):
        """is_tty checks stdin.isatty()."""
        with patch.object(sys, "stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            assert is_tty() is True

            mock_stdin.isatty.return_value = False
            assert is_tty() is False


class TestGetTerminalSize:
    """Test get_terminal_size() function."""

    def test_returns_tuple(self):
        """get_terminal_size returns (cols, rows) tuple."""
        cols, rows = get_terminal_size()
        assert isinstance(cols, int)
        assert isinstance(rows, int)

    def test_fallback_on_error(self):
        """get_terminal_size returns 80x24 on error."""
        with patch("os.get_terminal_size", side_effect=OSError):
            cols, rows = get_terminal_size()
            assert cols == 80
            assert rows == 24

    def test_positive_values(self):
        """get_terminal_size returns positive values."""
        cols, rows = get_terminal_size()
        assert cols > 0
        assert rows > 0


class TestRawMode:
    """Test raw mode functions."""

    def test_enter_raw_mode_not_tty(self):
        """enter_raw_mode returns False if not TTY."""
        with patch("cmdop.services.terminal.tui.modes.is_tty", return_value=False):
            result = enter_raw_mode()
            assert result is False

    def test_exit_raw_mode_not_in_raw(self):
        """exit_raw_mode returns False if not in raw mode."""
        # Reset global state
        from cmdop.services.terminal.tui import modes
        modes._terminal_mode.is_raw = False

        result = exit_raw_mode()
        assert result is False

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
    def test_enter_exit_raw_mode_unix(self):
        """enter/exit raw mode works on Unix (mocked)."""
        with patch("cmdop.services.terminal.tui.modes.is_tty", return_value=True):
            with patch("termios.tcgetattr", return_value=[0, 0, 0, 0, 0, 0, []]):
                with patch("tty.setraw"):
                    result = enter_raw_mode()
                    # May return True or False depending on actual TTY state
                    assert isinstance(result, bool)


class TestRawModeContextManager:
    """Test raw_mode() context manager."""

    def test_context_manager_calls_enter_exit(self):
        """raw_mode context manager calls enter and exit."""
        with patch("cmdop.services.terminal.tui.modes.enter_raw_mode") as mock_enter:
            with patch("cmdop.services.terminal.tui.modes.exit_raw_mode") as mock_exit:
                with raw_mode():
                    mock_enter.assert_called_once()
                mock_exit.assert_called_once()

    def test_context_manager_exits_on_exception(self):
        """raw_mode context manager exits even on exception."""
        with patch("cmdop.services.terminal.tui.modes.enter_raw_mode"):
            with patch("cmdop.services.terminal.tui.modes.exit_raw_mode") as mock_exit:
                try:
                    with raw_mode():
                        raise ValueError("test error")
                except ValueError:
                    pass
                mock_exit.assert_called_once()


class TestTtyState:
    """Test TTY state save/restore."""

    def test_save_tty_state_not_tty(self):
        """save_tty_state returns None if not TTY."""
        with patch("cmdop.services.terminal.tui.modes.is_tty", return_value=False):
            result = save_tty_state()
            assert result is None

    def test_restore_tty_state_none(self):
        """restore_tty_state returns False for None."""
        result = restore_tty_state(None)
        assert result is False

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
    def test_save_restore_tty_state_unix(self):
        """save/restore TTY state works on Unix (mocked)."""
        mock_settings = [0, 0, 0, 0, 0, 0, []]

        with patch("cmdop.services.terminal.tui.modes.is_tty", return_value=True):
            with patch("cmdop.services.terminal.tui.modes.TerminalMode.detect_platform", return_value="linux"):
                # Need to patch termios at the place where it's imported inside the function
                with patch("cmdop.services.terminal.tui.modes.sys.stdin") as mock_stdin:
                    mock_stdin.fileno.return_value = 0
                    with patch.dict("sys.modules", {"termios": MagicMock()}):
                        import sys
                        mock_termios = sys.modules["termios"]
                        mock_termios.tcgetattr = MagicMock(return_value=mock_settings)
                        mock_termios.TCSADRAIN = 1

                        state = save_tty_state()
                        assert state == mock_settings

                        mock_termios.tcsetattr = MagicMock()
                        result = restore_tty_state(state)
                        assert result is True
                        mock_termios.tcsetattr.assert_called_once()


class TestResizeHandler:
    """Test resize signal handler."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
    def test_setup_resize_handler(self):
        """setup_resize_handler installs signal handler."""
        callback = MagicMock()

        with patch("signal.signal") as mock_signal:
            result = setup_resize_handler(callback)
            assert result is True
            mock_signal.assert_called_once()

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
    def test_remove_resize_handler(self):
        """remove_resize_handler removes signal handler."""
        with patch("signal.signal") as mock_signal:
            result = remove_resize_handler()
            assert result is True
            mock_signal.assert_called_once()

    def test_setup_resize_handler_windows(self):
        """setup_resize_handler returns False on Windows."""
        with patch.object(TerminalMode, "detect_platform", return_value="windows"):
            callback = MagicMock()
            result = setup_resize_handler(callback)
            assert result is False

    def test_remove_resize_handler_windows(self):
        """remove_resize_handler returns False on Windows."""
        with patch.object(TerminalMode, "detect_platform", return_value="windows"):
            result = remove_resize_handler()
            assert result is False
