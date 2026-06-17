"""``machines.ask`` streaming: the typed frame union + :class:`FrameStream`.

The Go core drives the relay's SSE ``/ask`` + the ``/pin`` + ``/confirm``
side-channel POSTs and projects each onto an ``Envelope`` on the call's id
(report 13 §4.1):

* ``EVENT``  + ``ask_frame.event``            -> :class:`EventFrame`
* ``EVENT``  + ``ask_frame.pin_denied``       -> :class:`PinDeniedFrame`
* ``CALLBACK`` + ``pin_required``             -> :class:`PinRequiredFrame`
* ``CALLBACK`` + ``confirm_required``         -> :class:`ConfirmRequiredFrame`
* ``DONE``   + ``done``                       -> :class:`DoneFrame`
* ``ERROR``  + ``error``                      -> raised as :class:`AgentStreamError`

The caller answers a pin/confirm mid-iteration with ``stream.pin(...)`` /
``stream.confirm(...)`` — these write an ``ANSWER`` envelope on the **same id**,
and the core resumes the stream. This is byte-for-byte the archived REST
wrapper's ergonomics (report 03 §4.3); only the transport changed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop._proto.cmdop.core.v1 import machines_pb2 as m_pb
from cmdop.errors import AgentStreamError, CmdopError, map_core_error

# Stream-terminal ``error`` codes that surface as their typed exception (not the
# generic AgentStreamError) — the connection-PIN gate's verdicts. Everything else
# keeps the established AgentStreamError stream contract.
_TYPED_STREAM_ERROR_CODES = frozenset({"pin_denied", "pin_required_timeout"})


def _stream_error(code: str, message: str) -> CmdopError:
    """Raise the typed PIN exception for a PIN-gate verdict; otherwise the
    generic :class:`AgentStreamError` (the ask stream's error-frame contract)."""
    if code in _TYPED_STREAM_ERROR_CODES:
        return map_core_error(code, message)
    return AgentStreamError(code or "internal", message or "")

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from cmdop._transport import Transport


# --- Frame union ----------------------------------------------------------


@dataclass
class EventFrame:
    type: Literal["event"]
    event_type: int
    payload: Any


@dataclass
class DoneFrame:
    type: Literal["done"]
    success: bool
    text: str
    error: str
    duration_ms: int


@dataclass
class ConfirmRequiredFrame:
    type: Literal["confirm_required"]
    token: str
    plan: str
    danger_level: str = "medium"


@dataclass
class PinRequiredFrame:
    type: Literal["pin_required"]
    challenge_id: str
    label: str


@dataclass
class PinDeniedFrame:
    type: Literal["pin_denied"]
    challenge_id: str
    reason: str


@dataclass
class ErrorFrame:
    type: Literal["error"]
    code: str
    message: str


@dataclass
class UnknownFrame:
    """Forward-compat: a frame whose shape we do not model yet."""

    type: str
    raw: dict[str, Any] = field(default_factory=dict)


AskFrame = (
    EventFrame
    | DoneFrame
    | ConfirmRequiredFrame
    | PinRequiredFrame
    | PinDeniedFrame
    | ErrorFrame
    | UnknownFrame
)


def _frame_from_envelope(env: pb.Envelope) -> AskFrame:
    """Project one streamed Envelope onto a typed frame."""
    kind = env.kind
    if kind == pb.Envelope.KIND_DONE:
        d = env.done
        return DoneFrame(
            type="done",
            success=d.success,
            text=d.text or "",
            error=d.error or "",
            duration_ms=int(d.duration_ms or 0),
        )
    if kind == pb.Envelope.KIND_CALLBACK:
        arm = env.WhichOneof("payload")
        if arm == "pin_required":
            pr = env.pin_required
            return PinRequiredFrame(
                type="pin_required", challenge_id=pr.challenge_id, label=pr.label
            )
        if arm == "confirm_required":
            cr = env.confirm_required
            return ConfirmRequiredFrame(
                type="confirm_required",
                token=cr.token,
                plan=cr.plan,
                danger_level=cr.danger_level or "medium",
            )
        return UnknownFrame(type=str(arm))
    if kind == pb.Envelope.KIND_EVENT:
        frame = env.ask_frame
        inner = frame.WhichOneof("frame")
        if inner == "event":
            ev = frame.event
            payload: Any = None
            if ev.payload_json:
                try:
                    payload = json.loads(ev.payload_json)
                except (ValueError, json.JSONDecodeError):
                    payload = ev.payload_json
            return EventFrame(type="event", event_type=int(ev.event_type), payload=payload)
        if inner == "pin_denied":
            pd = frame.pin_denied
            return PinDeniedFrame(
                type="pin_denied", challenge_id=pd.challenge_id, reason=pd.reason
            )
        return UnknownFrame(type=str(inner))
    return UnknownFrame(type=pb.Envelope.Kind.Name(kind))


# --- FrameStream ----------------------------------------------------------


class FrameStream:
    """Async-iterable of :data:`AskFrame` with ``pin()`` / ``confirm()`` /
    ``collect()``.

    Iterating starts the streaming call (sends the REQUEST), then yields typed
    frames until a terminal DONE; a terminal ERROR is raised as
    :class:`AgentStreamError`.
    """

    def __init__(self, transport: Transport, req: pb.Envelope) -> None:
        self._t = transport
        self._req = req
        self._id: int | None = None

    async def __aiter__(self) -> AsyncIterator[AskFrame]:
        from cmdop._transport import _STREAM_END  # local import: avoid cycle

        self._id, queue = await self._t._start_stream(self._req)
        while True:
            item = await queue.get()
            if item is _STREAM_END:
                return
            if isinstance(item, BaseException):
                # transport-level failure (core crashed / EOF mid-stream).
                raise item
            if item.kind == pb.Envelope.KIND_ERROR:
                # ask stream's terminal error frame. PIN-gate verdicts surface as
                # their typed exception (PinDeniedError / PinTimeoutError).
                raise _stream_error(item.error.code or "", item.error.message or "")
            yield _frame_from_envelope(item)

    async def pin(self, challenge_id: str, pin: str) -> None:
        """Answer a ``pin_required`` frame with the entered connection PIN."""
        await self._t.write_answer(
            pb.Envelope(
                id=self._require_id(),
                kind=pb.Envelope.KIND_ANSWER,
                pin_answer=m_pb.PinAnswer(challenge_id=challenge_id, pin=pin),
            )
        )

    async def confirm(self, token: str, accept: bool) -> None:
        """Answer a ``confirm_required`` frame. ``accept=True`` resumes the
        stream onto the same id; ``accept=False`` ends it with a rejected DONE."""
        await self._t.write_answer(
            pb.Envelope(
                id=self._require_id(),
                kind=pb.Envelope.KIND_ANSWER,
                confirm_answer=m_pb.ConfirmAnswer(token=token, accept=accept),
            )
        )

    async def collect(self) -> str:
        """Drain to the final text (the ``done`` frame's text, else accumulated
        event deltas). Raises :class:`AgentStreamError` on an error outcome."""
        text = ""
        async for frame in self:
            if isinstance(frame, EventFrame):
                payload = frame.payload if isinstance(frame.payload, dict) else {}
                text += payload.get("delta") or payload.get("text") or ""
            elif isinstance(frame, DoneFrame):
                return frame.text or text
            elif isinstance(frame, ErrorFrame):
                raise _stream_error(frame.code, frame.message)
        return text

    def _require_id(self) -> int:
        if self._id is None:
            raise RuntimeError("answer called before the ask stream was iterated")
        return self._id
