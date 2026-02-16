"""
TUI (Text User Interface) module for terminal support.

Provides SSH-like interactive terminal experience and terminal emulation.

Usage:
    >>> from cmdop.services.terminal.tui import ssh_connect
    >>> await ssh_connect("my-server", api_key="xxx")

    >>> from cmdop.services.terminal.tui import TerminalEmulator
    >>> emu = TerminalEmulator(80, 24)
    >>> emu.feed(b"Hello World")
"""

from cmdop.services.terminal.tui.emulator import (
    TerminalCell,
    TerminalEmulator,
    TerminalState,
    create_emulator,
)
from cmdop.services.terminal.tui.modes import (
    TerminalMode,
    enter_raw_mode,
    exit_raw_mode,
    get_terminal_size,
)
from cmdop.services.terminal.tui.ssh import ssh_connect

__all__ = [
    # Emulator
    "TerminalEmulator",
    "TerminalCell",
    "TerminalState",
    "create_emulator",
    # Modes
    "TerminalMode",
    "enter_raw_mode",
    "exit_raw_mode",
    "get_terminal_size",
    # SSH
    "ssh_connect",
]
