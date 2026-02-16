"""
Terminal mode management utilities.

Provides TTY state management for raw mode terminal operations.
Supports Unix (Linux, macOS) systems via termios.
"""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator


@dataclass
class TerminalMode:
    """
    Container for terminal mode state.

    Stores the original terminal settings for restoration.
    """

    original_settings: Any | None = None
    is_raw: bool = False
    platform: str = ""

    @classmethod
    def detect_platform(cls) -> str:
        """Detect current platform."""
        if sys.platform == "darwin":
            return "macos"
        elif sys.platform.startswith("linux"):
            return "linux"
        elif sys.platform == "win32":
            return "windows"
        return "unknown"


# Global terminal mode state
_terminal_mode = TerminalMode()


def is_tty() -> bool:
    """Check if stdin is a TTY."""
    return sys.stdin.isatty()


def get_terminal_size() -> tuple[int, int]:
    """
    Get current terminal size.

    Returns:
        Tuple of (columns, rows).
    """
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24  # Default fallback


def enter_raw_mode() -> bool:
    """
    Enter raw terminal mode (unbuffered, no echo).

    Raw mode:
    - Disables line buffering
    - Disables local echo
    - Disables signal generation (Ctrl+C, Ctrl+Z)
    - Allows reading individual keypresses

    Returns:
        True if successful, False if not supported.

    Note:
        Always call exit_raw_mode() to restore terminal state.
    """
    global _terminal_mode

    if _terminal_mode.is_raw:
        return True  # Already in raw mode

    _terminal_mode.platform = TerminalMode.detect_platform()

    if _terminal_mode.platform == "windows":
        return _enter_raw_mode_windows()
    else:
        return _enter_raw_mode_unix()


def exit_raw_mode() -> bool:
    """
    Exit raw terminal mode and restore original settings.

    Returns:
        True if successful, False if not in raw mode.
    """
    global _terminal_mode

    if not _terminal_mode.is_raw:
        return False  # Not in raw mode

    if _terminal_mode.platform == "windows":
        return _exit_raw_mode_windows()
    else:
        return _exit_raw_mode_unix()


@contextmanager
def raw_mode() -> Generator[None, None, None]:
    """
    Context manager for raw terminal mode.

    Usage:
        >>> with raw_mode():
        ...     char = sys.stdin.read(1)
        ...     process_char(char)
    """
    try:
        enter_raw_mode()
        yield
    finally:
        exit_raw_mode()


# =============================================================================
# Unix Implementation (Linux, macOS)
# =============================================================================


def _enter_raw_mode_unix() -> bool:
    """Enter raw mode on Unix systems."""
    global _terminal_mode

    if not is_tty():
        return False

    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        _terminal_mode.original_settings = termios.tcgetattr(fd)

        # Enter raw mode
        tty.setraw(fd)
        _terminal_mode.is_raw = True

        return True

    except (ImportError, OSError, termios.error):
        return False


def _exit_raw_mode_unix() -> bool:
    """Exit raw mode on Unix systems."""
    global _terminal_mode

    if _terminal_mode.original_settings is None:
        return False

    try:
        import termios

        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, _terminal_mode.original_settings)

        _terminal_mode.original_settings = None
        _terminal_mode.is_raw = False

        return True

    except (ImportError, OSError, termios.error):
        return False


def save_tty_state() -> Any:
    """
    Save current TTY state for later restoration.

    Returns:
        TTY state object (platform-specific), or None on failure.
    """
    if not is_tty():
        return None

    platform = TerminalMode.detect_platform()

    if platform == "windows":
        return _save_tty_state_windows()
    else:
        return _save_tty_state_unix()


def restore_tty_state(state: Any) -> bool:
    """
    Restore TTY state from saved state.

    Args:
        state: State object from save_tty_state().

    Returns:
        True if successful.
    """
    if state is None:
        return False

    platform = TerminalMode.detect_platform()

    if platform == "windows":
        return _restore_tty_state_windows(state)
    else:
        return _restore_tty_state_unix(state)


def _save_tty_state_unix() -> Any:
    """Save TTY state on Unix."""
    try:
        import termios

        fd = sys.stdin.fileno()
        return termios.tcgetattr(fd)
    except (ImportError, OSError):
        return None


def _restore_tty_state_unix(state: Any) -> bool:
    """Restore TTY state on Unix."""
    try:
        import termios

        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, state)
        return True
    except (ImportError, OSError):
        return False


# =============================================================================
# Windows Implementation (placeholder)
# =============================================================================


def _enter_raw_mode_windows() -> bool:
    """Enter raw mode on Windows (placeholder)."""
    # Windows requires msvcrt or ctypes for console mode
    # TODO: Implement Windows support
    return False


def _exit_raw_mode_windows() -> bool:
    """Exit raw mode on Windows (placeholder)."""
    global _terminal_mode
    _terminal_mode.is_raw = False
    return True


def _save_tty_state_windows() -> Any:
    """Save TTY state on Windows (placeholder)."""
    return None


def _restore_tty_state_windows(state: Any) -> bool:
    """Restore TTY state on Windows (placeholder)."""
    return False


# =============================================================================
# SIGWINCH Handler (Unix only)
# =============================================================================


def setup_resize_handler(callback: Any) -> bool:
    """
    Setup terminal resize signal handler.

    Args:
        callback: Function to call with (cols, rows) on resize.

    Returns:
        True if handler was installed successfully.

    Note:
        Only works on Unix systems. Windows does not support SIGWINCH.
    """
    platform = TerminalMode.detect_platform()

    if platform == "windows":
        return False

    try:
        import signal

        def sigwinch_handler(signum: int, frame: Any) -> None:
            """Handle SIGWINCH signal."""
            try:
                cols, rows = get_terminal_size()
                callback(cols, rows)
            except Exception:
                pass

        signal.signal(signal.SIGWINCH, sigwinch_handler)
        return True

    except (ImportError, ValueError, OSError):
        return False


def remove_resize_handler() -> bool:
    """
    Remove terminal resize signal handler.

    Returns:
        True if handler was removed successfully.
    """
    platform = TerminalMode.detect_platform()

    if platform == "windows":
        return False

    try:
        import signal

        signal.signal(signal.SIGWINCH, signal.SIG_DFL)
        return True

    except (ImportError, ValueError, OSError):
        return False
