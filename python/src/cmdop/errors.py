"""Public error hierarchy + ``ErrorInfo.code`` -> exception mapping.

The Go core emits a terminal ``ERROR`` frame carrying an ``ErrorInfo{code,
message}``; the thin client maps that ``code`` to the right typed exception via
:func:`map_core_error`. The ``code`` values are owned by the core
(``internal/sdk/core/errmap.go``): ``auth / permission / not_found / conflict /
validation / rate_limit / server / connection / timeout / unavailable`` (plus
``internal``, ``unknown_op``, ``unsupported`` catch-alls).

This mirrors the archived REST wrapper's :class:`CmdopError` tree exactly; only
the source of the discriminator changed (an HTTP status became an
``ErrorInfo.code``).
"""

from __future__ import annotations

from typing import Any


class CmdopError(Exception):
    """Base class for every SDK error."""

    #: True for transient failures worth retrying (timeouts). Subclasses override.
    retryable: bool = False

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        code: str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.body = body


class AuthError(CmdopError):
    """``auth`` — invalid/expired/missing token (401)."""


class PermissionError(CmdopError):  # noqa: A001 - intentional shadow within this ns
    """``permission`` — role/api-key restriction (403)."""


class NotFoundError(CmdopError):
    """``not_found`` — resource not visible / not found (404)."""


class ConflictError(CmdopError):
    """``conflict`` — slug taken, already linked, last-owner, etc. (409)."""


class ValidationError(CmdopError):
    """``validation`` — bad request (422 / unprocessable / bad arg)."""


class RateLimitError(CmdopError):
    """``rate_limit`` — too many requests (429)."""

    def __init__(self, *args: Any, retry_after: int | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.retry_after = retry_after


class ServerError(CmdopError):
    """``server`` — relay/agent internal error (5xx)."""


class ConnectionError(CmdopError):  # noqa: A001 - intentional shadow within this ns
    """``connection`` — transport failure (DNS, refused, reset) or the core process died."""


class TimeoutError(ConnectionError):  # noqa: A001 - intentional shadow within this ns
    """``timeout`` — a deadline/handshake timeout. Retryable; subclasses
    :class:`ConnectionError` so existing ``except ConnectionError`` still catches it."""

    retryable = True


class UnavailableError(CmdopError):
    """``unavailable`` — the relay is reachable but the target machine/agent has no
    connected session (it's offline). Distinct from a transport failure."""


class PinDeniedError(PermissionError):  # noqa: A001 - intentional shadow within this ns
    """``pin_denied`` — the connection PIN was rejected (wrong PIN, lockout).

    Subclasses :class:`PermissionError` so existing ``except PermissionError``
    still catches it. Non-retryable: a wrong PIN won't fix itself on retry."""

    retryable = False


class PinTimeoutError(PermissionError):  # noqa: A001 - intentional shadow within this ns
    """``pin_required_timeout`` — no PIN supplied (or verified) within the gate
    window. Subclasses :class:`PermissionError`. Non-retryable."""

    retryable = False


class AgentStreamError(CmdopError):
    """An ``error`` outcome from ``machines.ask`` (machine_offline/timeout/internal)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message, code=code)


# ErrorInfo.code -> exception class (codes owned by internal/sdk/core/errmap.go).
_CODE_MAP: dict[str, type[CmdopError]] = {
    "auth": AuthError,
    "permission": PermissionError,
    "not_found": NotFoundError,
    "conflict": ConflictError,
    "validation": ValidationError,
    "server": ServerError,
    "connection": ConnectionError,
    "timeout": TimeoutError,
    "unavailable": UnavailableError,
    "pin_denied": PinDeniedError,
    "pin_required_timeout": PinTimeoutError,
}


def map_core_error(code: str, message: str) -> CmdopError:
    """Map a core ``ErrorInfo{code, message}`` to a typed exception."""
    if code == "rate_limit":
        return RateLimitError(message, code=code)

    cls = _CODE_MAP.get(code)
    if cls is not None:
        return cls(message, code=code)

    # internal / unknown_op / unsupported / anything new -> base error.
    return CmdopError(message, code=code)
