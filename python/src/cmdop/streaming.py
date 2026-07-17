"""Typed ``machines.ask`` stream."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from cmdop._proto.cmdop.core.v2 import contract_pb2 as pb
from cmdop.errors import AgentStreamError
from cmdop.errors import TimeoutError as CmdopTimeoutError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from cmdop._transport import Transport


@dataclass(frozen=True)
class EventFrame:
    type: Literal["event"]
    event_type: int
    payload: Any
    machine_id: str | None = None


@dataclass(frozen=True)
class StreamErrorFrame:
    type: Literal["error"]
    code: str
    message: str


@dataclass(frozen=True)
class DoneFrame:
    type: Literal["done"]
    success: bool
    text: str
    error: str | None = None
    upstream_status: int | None = None
    provider: str | None = None
    detail: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cache_read_tokens: int | None = None
    cache_write_tokens: int | None = None
    cost_usd: float | None = None
    cost_source: str | None = None
    engine: str | None = None
    model: str | None = None


AskFrame = EventFrame | StreamErrorFrame | DoneFrame


def _optional(message: Any, name: str) -> Any | None:
    return getattr(message, name) if message.HasField(name) else None


def _stream_error_code(code: int) -> str:
    return pb.AskStreamErrorCode.Name(code).removeprefix(
        "ASK_STREAM_ERROR_CODE_"
    ).lower()


class AskStream:
    def __init__(self, transport: Transport, request: pb.Envelope, timeout_ms: int) -> None:
        self._transport = transport
        self._request = request
        self._timeout = timeout_ms / 1000
        self._started = False

    async def __aiter__(self) -> AsyncIterator[AskFrame]:
        if self._started:
            raise RuntimeError("an AskStream can only be consumed once")
        self._started = True
        from cmdop._transport import _STREAM_END

        call_id, queue = await self._transport._start_stream(self._request)
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), self._timeout)
                except (TimeoutError, asyncio.TimeoutError) as exc:
                    raise CmdopTimeoutError(
                        "agent stream timed out", code="deadline_exceeded"
                    ) from exc
                if item is _STREAM_END:
                    return
                if isinstance(item, BaseException):
                    raise item
                assert isinstance(item, pb.Envelope)
                if item.kind == pb.Envelope.KIND_EVENT:
                    arm = item.WhichOneof("payload")
                    if arm == "ask_event":
                        payload: Any = item.ask_event.payload_json
                        try:
                            payload = json.loads(payload)
                        except (TypeError, ValueError):
                            pass
                        yield EventFrame(
                            "event",
                            int(item.ask_event.event_type),
                            payload,
                            _optional(item.ask_event, "machine_id"),
                        )
                    elif arm == "ask_stream_error":
                        yield StreamErrorFrame(
                            "error",
                            _stream_error_code(item.ask_stream_error.code),
                            item.ask_stream_error.message,
                        )
                elif item.kind == pb.Envelope.KIND_DONE:
                    done = item.ask_done
                    yield DoneFrame(
                        "done",
                        done.success,
                        done.text,
                        _optional(done, "error"),
                        _optional(done, "upstream_status"),
                        _optional(done, "provider"),
                        _optional(done, "detail"),
                        _optional(done, "input_tokens"),
                        _optional(done, "output_tokens"),
                        _optional(done, "total_tokens"),
                        _optional(done, "cache_read_tokens"),
                        _optional(done, "cache_write_tokens"),
                        _optional(done, "cost_usd"),
                        _optional(done, "cost_source"),
                        _optional(done, "engine"),
                        _optional(done, "model"),
                    )
        finally:
            self._transport._abandon_stream(call_id)

    async def collect(self) -> str:
        text = ""
        stream_error: StreamErrorFrame | None = None
        async for frame in self:
            if isinstance(frame, EventFrame) and isinstance(frame.payload, dict):
                text += frame.payload.get("delta") or frame.payload.get("text") or ""
            elif isinstance(frame, StreamErrorFrame):
                stream_error = frame
            elif isinstance(frame, DoneFrame):
                if not frame.success:
                    raise AgentStreamError(
                        frame.error or (stream_error.message if stream_error else "agent run failed"),
                        code=stream_error.code if stream_error else "internal",
                        status=frame.upstream_status,
                    )
                return frame.text or text
        return text
