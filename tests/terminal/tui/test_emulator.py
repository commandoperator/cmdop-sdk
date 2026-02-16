"""
Tests for terminal emulator (pyte wrapper).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestTerminalEmulatorInit:
    """Test TerminalEmulator initialization."""

    def test_default_size(self):
        """Default size is 80x24."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()
            assert emu.cols == 80
            assert emu.rows == 24

    def test_custom_size(self):
        """Custom size is respected."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator(120, 40)
            assert emu.cols == 120
            assert emu.rows == 40

    def test_import_error_without_pyte(self):
        """ImportError raised when pyte not available."""
        with patch.dict("sys.modules", {"pyte": None}):
            # Need to reimport to trigger the error
            import importlib

            from cmdop.services.terminal.tui import emulator

            importlib.reload(emulator)

            with pytest.raises(ImportError) as exc_info:
                emulator.TerminalEmulator()

            assert "pyte is required" in str(exc_info.value)


class TestTerminalEmulatorFeed:
    """Test feed() method."""

    def test_feed_bytes(self):
        """feed() accepts bytes."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()
            # Should not raise
            emu.feed(b"Hello World")

    def test_feed_string(self):
        """feed() accepts string."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()
            # Should not raise
            emu.feed("Hello World")


class TestTerminalEmulatorResize:
    """Test resize() method."""

    def test_resize_updates_dimensions(self):
        """resize() updates cols and rows."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator(80, 24)
            emu.resize(120, 40)

            assert emu.cols == 120
            assert emu.rows == 40


class TestTerminalEmulatorState:
    """Test get_state() and related methods."""

    def test_get_state_returns_terminal_state(self):
        """get_state() returns TerminalState."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import (
                TerminalEmulator,
                TerminalState,
            )

            emu = TerminalEmulator()
            state = emu.get_state()

            assert isinstance(state, TerminalState)
            assert state.cols == 80
            assert state.rows == 24

    def test_get_cursor_returns_tuple(self):
        """get_cursor() returns (x, y) tuple."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()
            cursor = emu.get_cursor()

            assert isinstance(cursor, tuple)
            assert len(cursor) == 2

    def test_get_text_returns_string(self):
        """get_text() returns string."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()
            text = emu.get_text()

            assert isinstance(text, str)

    def test_get_line_returns_string(self):
        """get_line() returns string for valid line."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()
            line = emu.get_line(0)

            assert isinstance(line, str)

    def test_get_line_invalid_returns_empty(self):
        """get_line() returns empty for invalid line."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()

            assert emu.get_line(-1) == ""
            assert emu.get_line(100) == ""


class TestTerminalEmulatorCallbacks:
    """Test callback registration."""

    def test_on_title_change(self):
        """on_title_change() registers callback."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()
            callback = MagicMock()
            emu.on_title_change(callback)

            # Callback stored
            assert emu._title_callback is callback

    def test_on_bell(self):
        """on_bell() registers callback."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()
            callback = MagicMock()
            emu.on_bell(callback)

            # Callback stored
            assert emu._bell_callback is callback


class TestTerminalEmulatorReset:
    """Test reset() method."""

    def test_reset_clears_title(self):
        """reset() clears terminal title."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator()
            emu._title = "Test Title"
            emu.reset()

            assert emu.title == ""


class TestTerminalEmulatorRepr:
    """Test __repr__() method."""

    def test_repr_includes_dimensions(self):
        """repr includes dimensions."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import TerminalEmulator

            emu = TerminalEmulator(120, 40)
            repr_str = repr(emu)

            assert "120" in repr_str
            assert "40" in repr_str


class TestCreateEmulator:
    """Test create_emulator() helper."""

    def test_create_emulator_returns_emulator(self):
        """create_emulator() returns TerminalEmulator."""
        with patch.dict("sys.modules", {"pyte": create_mock_pyte()}):
            from cmdop.services.terminal.tui.emulator import (
                TerminalEmulator,
                create_emulator,
            )

            emu = create_emulator(100, 30)

            assert isinstance(emu, TerminalEmulator)
            assert emu.cols == 100
            assert emu.rows == 30


class TestTerminalCell:
    """Test TerminalCell dataclass."""

    def test_default_values(self):
        """TerminalCell has correct defaults."""
        from cmdop.services.terminal.tui.emulator import TerminalCell

        cell = TerminalCell()

        assert cell.char == " "
        assert cell.fg == "default"
        assert cell.bg == "default"
        assert cell.bold is False
        assert cell.italic is False
        assert cell.underline is False
        assert cell.reverse is False

    def test_custom_values(self):
        """TerminalCell accepts custom values."""
        from cmdop.services.terminal.tui.emulator import TerminalCell

        cell = TerminalCell(
            char="A",
            fg="red",
            bg="blue",
            bold=True,
            italic=True,
            underline=True,
            reverse=True,
        )

        assert cell.char == "A"
        assert cell.fg == "red"
        assert cell.bg == "blue"
        assert cell.bold is True


class TestTerminalState:
    """Test TerminalState dataclass."""

    def test_default_values(self):
        """TerminalState has correct defaults."""
        from cmdop.services.terminal.tui.emulator import TerminalState

        state = TerminalState()

        assert state.lines == []
        assert state.cursor_x == 0
        assert state.cursor_y == 0
        assert state.cols == 80
        assert state.rows == 24
        assert state.title == ""


# =============================================================================
# Helper Functions
# =============================================================================


def create_mock_pyte() -> MagicMock:
    """Create a mock pyte module."""
    mock_pyte = MagicMock()

    # Mock Char (character with attributes)
    mock_char = MagicMock()
    mock_char.data = " "
    mock_char.fg = "default"
    mock_char.bg = "default"
    mock_char.bold = False
    mock_char.underscore = False
    mock_char.reverse = False

    # Mock Screen
    mock_screen = MagicMock()
    mock_screen.cursor = MagicMock()
    mock_screen.cursor.x = 0
    mock_screen.cursor.y = 0

    # Create buffer with mock chars
    buffer = {}
    for y in range(24):
        buffer[y] = {x: mock_char for x in range(80)}
    mock_screen.buffer = buffer

    mock_screen.set_title = MagicMock()
    mock_screen.bell = MagicMock()
    mock_screen.reset = MagicMock()
    mock_screen.resize = MagicMock()

    # Mock HistoryScreen
    mock_pyte.HistoryScreen = MagicMock(return_value=mock_screen)

    # Mock ByteStream
    mock_stream = MagicMock()
    mock_stream.feed = MagicMock()
    mock_pyte.ByteStream = MagicMock(return_value=mock_stream)

    return mock_pyte
