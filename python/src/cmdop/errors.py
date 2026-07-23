"""Typed errors shared by every v2 SDK operation."""

from __future__ import annotations

import json
from typing import Any

from cmdop._proto.cmdop.core.v2 import contract_pb2 as pb


class CmdopError(Exception):
    retryable = False

    def __init__(
        self,
        message: str,
        *,
        code: str = "internal",
        status: int | None = None,
        retryable: bool | None = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.details = details
        if retryable is not None:
            self.retryable = retryable


class AuthError(CmdopError):
    pass


class PermissionError(CmdopError):  # noqa: A001
    pass


class NotFoundError(CmdopError):
    pass


class ConflictError(CmdopError):
    pass


class ValidationError(CmdopError):
    pass


class RateLimitError(CmdopError):
    pass


class ServerError(CmdopError):
    pass


class ConnectionError(CmdopError):  # noqa: A001
    pass


class TimeoutError(ConnectionError):  # noqa: A001
    retryable = True


class UnavailableError(CmdopError):
    pass


class UnsupportedError(CmdopError):
    pass


class ProtocolError(CmdopError):
    pass


class AgentStreamError(CmdopError):
    pass


_ERROR_TYPES: dict[str, type[CmdopError]] = {
    "invalid_argument": ValidationError,
    "unauthenticated": AuthError,
    "permission_denied": PermissionError,
    "not_found": NotFoundError,
    "conflict": ConflictError,
    "rate_limited": RateLimitError,
    "internal": ServerError,
    "unavailable": UnavailableError,
    "deadline_exceeded": TimeoutError,
    "transport": ConnectionError,
    "unsupported": UnsupportedError,
    "protocol": ProtocolError,
}


def error_code_name(code: int) -> str:
    name = pb.ErrorCode.Name(code)
    return name.removeprefix("ERROR_CODE_").lower()


def map_core_error(info: pb.ErrorInfo) -> CmdopError:
    code = error_code_name(info.code)
    details: Any = None
    if info.HasField("details_json"):
        try:
            details = json.loads(info.details_json)
        except ValueError:
            details = info.details_json
    error_type = _ERROR_TYPES.get(code, CmdopError)
    return error_type(
        info.message or code.replace("_", " "),
        code=code,
        status=info.http_status if info.HasField("http_status") else None,
        retryable=info.retryable,
        details=details,
    )
