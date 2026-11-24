"""The one error a call raises. Decide by `code`, never by the message."""

from __future__ import annotations

from typing import Any


class CmdopError(Exception):
    """A call returned no result: refused, failed, timed out, cancelled. `code` is one of `ERROR_CODES`."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.details = details


class CarrierError(Exception):
    """A carrier could not reach the door or read what came back: not a contract answer."""

    def __init__(self, carrier: str, message: str) -> None:
        super().__init__(f"{carrier}: {message}")
        self.carrier = carrier
