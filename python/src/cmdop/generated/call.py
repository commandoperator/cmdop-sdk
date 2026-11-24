# Generated from cmdop/crates/tools/tools.schema.json (sha256 459e32fe9bbff178, cmdop 0.1.9) by exports/sdk/gen/gen.ts. Do not edit.
# Types by datamodel-code-generator==0.30.2.

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, RootModel


class OutputChunk(BaseModel):
    """
    One piece of a running command's output, as a streaming `exec_run` sends it (the payload of
    a `CallChunk`). The machine writes it and every client reads it, so it is defined here once.
    Fields are in the order the text has always had them; `dropped` is absent when nothing was.
    """

    data: str
    """
    The output, as text (invalid UTF-8 replaced).
    """
    dropped: int | None = Field(None, ge=0)
    """
    Bytes left out just before this piece because the reader fell behind; the call's final
    result still has the whole tail.
    """
    stream: Literal["stdout", "stderr"] = Field(..., title="OutputStream")
    """
    Which output of the command a piece comes from.
    """


class CallRequest(BaseModel):
    """
    One call, as a caller sends it.
    """

    args: Any | None = None
    """
    The arguments, as the tool's input schema says. Absent means `{}`.
    """
    deadline_ms: int | None = Field(None, ge=0)
    """
    How long the caller waits, in milliseconds. The call keeps the smaller of this and the
    tool's own time; past it the answer is `timed_out`. Absent: the tool's time.
    """
    machine: str | None = None
    """
    Machine id or unique name; optional when exactly one machine is online.
    """
    sealed: str | None = None
    """
    The arguments sealed for the machine, instead of `args`.
    """
    tool: str
    """
    The tool's name, in clear: the server routes and checks the grant by it.
    """


class ToolError(BaseModel):
    """
    Why a call did not return a result. The machine answers with this; the server and the SDK
    decide by `code`, never by `message`.
    """

    code: Literal[
        "other",
        "denied",
        "unknown_tool",
        "bad_args",
        "not_found",
        "busy",
        "permission_missing",
        "screen_locked",
        "stale_capture",
        "element_gone",
        "app_not_allowed",
        "lease_paused",
        "paused",
        "offline",
        "rate_limited",
        "quota_exceeded",
        "not_dispatched",
        "display_gone",
        "timed_out",
        "cancelled",
        "too_large",
        "hash_required",
        "failed",
        "needs_presence",
        "unauthorized",
    ] = Field(..., title="ErrorCode")
    """
    `denied`: The grant or the machine's ceiling does not allow it.
    `unknown_tool`: This machine does not have the tool (an older program).
    `bad_args`: The arguments do not match the tool's schema.
    `not_found`: The path or the thing named does not exist.
    `busy`: The machine runs too many calls already.
    `permission_missing`: The OS has not granted screen capture or input to the machine program.
    `screen_locked`: The screen is locked or asleep.
    `stale_capture`: A pixel action without a current capture of that display, or the display changed.
    `element_gone`: The element id is not in the tree any more.
    `app_not_allowed`: `control` is not allowed for this app on this machine.
    `lease_paused`: The owner paused control, or the lease was ended.
    `paused`: The owner paused this machine (`control.pause`): no tool runs until it is resumed there.
    `offline`: The machine is not connected: it is off or asleep, or cmdop is not running on it, or its
    link ended before it answered (then the call may have run there). Only its owner can
    bring it back; do not retry until `machines_list` shows it online. Sent by the server,
    never by a machine.
    `rate_limited`: Too many calls: the machine's screen input this minute, or the contour's tool calls this
    minute under its plan (then `details.plan`, `details.per_minute` and
    `details.retry_after_s`). Wait, then try again.
    `quota_exceeded`: The contour's plan allows no more of this: `details.resource` (`computers`),
    `details.used`, `details.allowed`, `details.plan`. Retrying does not help; the owner removes
    one or changes the plan. Sent by the server, never by a machine.
    `not_dispatched`: The event may not have reached the OS; it is never replayed.
    `display_gone`: The display left (unplugged or resized) between capture and action.
    `timed_out`: No answer within the call's deadline: the caller's, or the tool's own time if shorter.
    `cancelled`: The caller stopped the call before it answered. The machine was told to stop it; what it
    had done by then stays done.
    `too_large`: The call's arguments, or its result, are more than one message between the server and a
    machine may hold (16 MiB). Nothing of that size is sent, and the machine stays online.
    `hash_required`: `fs_write` would replace an existing file and no `expect_sha256` came with it: get its
    SHA-256 with `fs_stat` and `hash=true` and pass it. Nothing was written.
    `failed`: The tool ran and failed.
    `needs_presence`: The change raises what agents may do; only a person present at the machine can allow it.
    `unauthorized`: No live token of this contour came with the call, or its kind may not use this door.
    `details.reason` says which: `unknown`, `revoked`, `expired` with `expired_at` (unix
    seconds), or `second_factor` (an owner token while the owner's second factor is on: use an
    agent token). Do not retry: an expired token works again only once the owner extends it.
    Sent by the server, never by a machine.
    """
    details: Any | None = None
    """
    Machine-readable facts for the caller, per code (`permission_missing` carries the
    permission, who must act and where). Absent for most errors; never required to read
    `code`.
    """
    message: str


class Answer1(BaseModel):
    """
    How a call ended: its result, why there is none, or a sealed answer with its outcome in
    clear (`ok` or an error code).
    """

    ok: Any


class Answer2(BaseModel):
    """
    How a call ended: its result, why there is none, or a sealed answer with its outcome in
    clear (`ok` or an error code).
    """

    error: ToolError


class Answer3(BaseModel):
    """
    How a call ended: its result, why there is none, or a sealed answer with its outcome in
    clear (`ok` or an error code).
    """

    outcome: str
    sealed: str


class StreamLine1(BaseModel):
    """
    One line of a streamed answer: a piece of output while the call runs, and the answer last.
    `seq` counts the pieces of one call from 0, in the order they were made.
    """

    chunk: OutputChunk
    seq: int = Field(..., ge=0)


class StreamLine2(BaseModel):
    """
    One line of a streamed answer: a piece of output while the call runs, and the answer last.
    `seq` counts the pieces of one call from 0, in the order they were made.
    """

    sealed_chunk: str
    seq: int = Field(..., ge=0)



ERROR_CODES: tuple[str, ...] = (
    "other",
    "denied",
    "unknown_tool",
    "bad_args",
    "not_found",
    "busy",
    "permission_missing",
    "screen_locked",
    "stale_capture",
    "element_gone",
    "app_not_allowed",
    "lease_paused",
    "paused",
    "offline",
    "rate_limited",
    "quota_exceeded",
    "not_dispatched",
    "display_gone",
    "timed_out",
    "cancelled",
    "too_large",
    "hash_required",
    "failed",
    "needs_presence",
    "unauthorized",
)
"""Every error code, in the order Rust declares them."""

ENVELOPE_MAX_BYTES = 16777216
"""The most one encoded call or answer may hold."""
PIECE_MAX_BYTES = 65536
"""The most one piece of a result sent in pieces holds."""
