"""
Terminal emulator wrapper using pyte.

Provides a virtual terminal screen that processes escape sequences
and maintains terminal state (cursor, colors, scrollback).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    import pyte


@dataclass
class TerminalCell:
    """
    Single cell in terminal grid.

    Attributes:
        char: Character at this position.
        fg: Foreground color (name or hex).
        bg: Background color (name or hex).
        bold: Bold text.
        italic: Italic text.
        underline: Underlined text.
        reverse: Reverse video (swap fg/bg).
    """

    char: str = " "
    fg: str = "default"
    bg: str = "default"
    bold: bool = False
    italic: bool = False
    underline: bool = False
    reverse: bool = False


@dataclass
class TerminalState:
    """
    Current terminal state snapshot.

    Attributes:
        lines: List of lines, each line is list of cells.
        cursor_x: Cursor column (0-indexed).
        cursor_y: Cursor row (0-indexed).
        cols: Number of columns.
        rows: Number of rows.
        title: Terminal title (if set via escape sequence).
    """

    lines: list[list[TerminalCell]] = field(default_factory=list)
    cursor_x: int = 0
    cursor_y: int = 0
    cols: int = 80
    rows: int = 24
    title: str = ""


class TerminalEmulator:
    """
    Terminal emulator using pyte library.

    Processes ANSI escape sequences and maintains a virtual screen.
    Useful for TUI rendering and terminal state inspection.

    Example:
        >>> emu = TerminalEmulator(80, 24)
        >>> emu.feed(b"Hello\\x1b[31m World\\x1b[0m")
        >>> state = emu.get_state()
        >>> print(state.lines[0][0].char)  # 'H'
        >>> print(state.lines[0][6].fg)    # 'red'
    """

    def __init__(
        self,
        cols: int = 80,
        rows: int = 24,
        *,
        scrollback: int = 1000,
    ) -> None:
        """
        Initialize terminal emulator.

        Args:
            cols: Number of columns.
            rows: Number of rows.
            scrollback: Number of scrollback lines to keep.
        """
        self._cols = cols
        self._rows = rows
        self._scrollback = scrollback
        self._title = ""
        self._title_callback: Callable[[str], None] | None = None
        self._bell_callback: Callable[[], None] | None = None

        # Lazy import pyte
        self._screen: pyte.Screen | None = None
        self._stream: pyte.ByteStream | None = None

        self._init_pyte()

    def _init_pyte(self) -> None:
        """Initialize pyte screen and stream."""
        try:
            import pyte

            # Create screen with history
            self._screen = pyte.HistoryScreen(
                self._cols,
                self._rows,
                history=self._scrollback,
            )

            # Create byte stream that feeds the screen
            self._stream = pyte.ByteStream(self._screen)

            # Hook into title changes
            original_set_title = self._screen.set_title

            def set_title_hook(title: str) -> None:
                self._title = title
                if self._title_callback:
                    self._title_callback(title)
                original_set_title(title)

            self._screen.set_title = set_title_hook  # type: ignore

            # Hook into bell
            original_bell = self._screen.bell

            def bell_hook() -> None:
                if self._bell_callback:
                    self._bell_callback()
                original_bell()

            self._screen.bell = bell_hook  # type: ignore

        except ImportError as e:
            raise ImportError(
                "pyte is required for terminal emulation. "
                "Install with: pip install pyte"
            ) from e

    @property
    def cols(self) -> int:
        """Number of columns."""
        return self._cols

    @property
    def rows(self) -> int:
        """Number of rows."""
        return self._rows

    @property
    def title(self) -> str:
        """Current terminal title."""
        return self._title

    def feed(self, data: bytes | str) -> None:
        """
        Feed data to terminal.

        Processes escape sequences and updates screen state.

        Args:
            data: Raw terminal output (bytes or string).
        """
        if self._stream is None:
            return

        if isinstance(data, str):
            data = data.encode("utf-8", errors="replace")

        self._stream.feed(data)

    def resize(self, cols: int, rows: int) -> None:
        """
        Resize terminal.

        Args:
            cols: New number of columns.
            rows: New number of rows.
        """
        if self._screen is None:
            return

        self._cols = cols
        self._rows = rows
        self._screen.resize(rows, cols)

    def reset(self) -> None:
        """Reset terminal to initial state."""
        if self._screen is None:
            return

        self._screen.reset()
        self._title = ""

    def get_state(self) -> TerminalState:
        """
        Get current terminal state.

        Returns:
            TerminalState with all screen data.
        """
        if self._screen is None:
            return TerminalState(
                cols=self._cols,
                rows=self._rows,
            )

        lines: list[list[TerminalCell]] = []

        for y in range(self._rows):
            line: list[TerminalCell] = []
            for x in range(self._cols):
                char = self._screen.buffer[y][x]
                cell = TerminalCell(
                    char=char.data,
                    fg=char.fg,
                    bg=char.bg,
                    bold=char.bold,
                    italic=getattr(char, "italics", False),
                    underline=char.underscore,
                    reverse=char.reverse,
                )
                line.append(cell)
            lines.append(line)

        return TerminalState(
            lines=lines,
            cursor_x=self._screen.cursor.x,
            cursor_y=self._screen.cursor.y,
            cols=self._cols,
            rows=self._rows,
            title=self._title,
        )

    def get_text(self, *, strip_trailing: bool = True) -> str:
        """
        Get screen content as plain text.

        Args:
            strip_trailing: Remove trailing whitespace from lines.

        Returns:
            Screen content as string with newlines.
        """
        if self._screen is None:
            return ""

        lines = []
        for y in range(self._rows):
            line = "".join(
                self._screen.buffer[y][x].data for x in range(self._cols)
            )
            if strip_trailing:
                line = line.rstrip()
            lines.append(line)

        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()

        return "\n".join(lines)

    def get_line(self, y: int) -> str:
        """
        Get single line as text.

        Args:
            y: Line number (0-indexed).

        Returns:
            Line content.
        """
        if self._screen is None or y < 0 or y >= self._rows:
            return ""

        return "".join(
            self._screen.buffer[y][x].data for x in range(self._cols)
        ).rstrip()

    def get_cursor(self) -> tuple[int, int]:
        """
        Get cursor position.

        Returns:
            Tuple of (x, y) cursor position.
        """
        if self._screen is None:
            return (0, 0)

        return (self._screen.cursor.x, self._screen.cursor.y)

    def get_scrollback(self) -> list[str]:
        """
        Get scrollback history.

        Returns:
            List of scrollback lines (oldest first).
        """
        if self._screen is None:
            return []

        try:
            # HistoryScreen stores history in top/bottom
            history = getattr(self._screen, "history", None)
            if history is None:
                return []

            lines = []
            for line in history.top:
                text = "".join(char.data for char in line.values())
                lines.append(text.rstrip())

            return lines
        except Exception:
            return []

    def on_title_change(self, callback: Callable[[str], None]) -> None:
        """
        Register callback for title changes.

        Args:
            callback: Function called with new title.
        """
        self._title_callback = callback

    def on_bell(self, callback: Callable[[], None]) -> None:
        """
        Register callback for bell (BEL character).

        Args:
            callback: Function called on bell.
        """
        self._bell_callback = callback

    def __repr__(self) -> str:
        return f"TerminalEmulator({self._cols}x{self._rows})"


def create_emulator(
    cols: int = 80,
    rows: int = 24,
    scrollback: int = 1000,
) -> TerminalEmulator:
    """
    Create a terminal emulator.

    Convenience function for creating TerminalEmulator instances.

    Args:
        cols: Number of columns.
        rows: Number of rows.
        scrollback: Scrollback buffer size.

    Returns:
        Configured TerminalEmulator.

    Example:
        >>> emu = create_emulator(120, 40)
        >>> emu.feed(b"Hello World")
        >>> print(emu.get_text())
        Hello World
    """
    return TerminalEmulator(cols, rows, scrollback=scrollback)
