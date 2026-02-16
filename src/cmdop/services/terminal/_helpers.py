"""
Helper utilities for terminal services.
"""

from __future__ import annotations

from cmdop.models.terminal import SignalType

# Signal enum to Unix signal number mapping
SIGNAL_MAP: dict[SignalType, int] = {
    SignalType.SIGHUP: 1,
    SignalType.SIGINT: 2,
    SignalType.SIGTERM: 15,
    SignalType.SIGKILL: 9,
    SignalType.SIGSTOP: 19,
    SignalType.SIGCONT: 18,
}


def get_signal_number(signal: SignalType) -> int:
    """Convert SignalType enum to Unix signal number."""
    return SIGNAL_MAP.get(signal, 15)  # Default to SIGTERM
