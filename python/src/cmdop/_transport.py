"""Bounded protobuf-over-stdio transport for ``cmdop-core``."""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

from google.protobuf.internal.decoder import _DecodeVarint32  # type: ignore[attr-defined]
from google.protobuf.internal.encoder import _VarintBytes  # type: ignore[attr-defined]

from cmdop._proto.cmdop.core.v2 import contract_pb2 as pb
from cmdop.errors import ConnectionError as CmdopConnectionError
from cmdop.errors import TimeoutError as CmdopTimeoutError
from cmdop.errors import map_core_error
from cmdop.streaming import AskStream

if TYPE_CHECKING:
    from cmdop.config import ClientConfig

_MAX_REQUEST_FRAME_BYTES = 4 * 1024 * 1024
_MAX_RESPONSE_FRAME_BYTES = 16 * 1024 * 1024
_STREAM_QUEUE_SIZE = 256
_STREAM_END = object()


class _UnaryPending:
    def __init__(self, future: asyncio.Future[pb.Envelope]) -> None:
        self.future = future


class _StreamPending:
    def __init__(self, queue: asyncio.Queue[object]) -> None:
        self.queue = queue


async def _read_delimited(reader: asyncio.StreamReader) -> bytes:
    length = bytearray()
    for _ in range(10):
        byte = await reader.readexactly(1)
        length.extend(byte)
        if not byte[0] & 0x80:
            size, _ = _DecodeVarint32(bytes(length), 0)
            if size > _MAX_RESPONSE_FRAME_BYTES:
                raise ValueError(
                    f"core frame exceeds {_MAX_RESPONSE_FRAME_BYTES} bytes"
                )
            return await reader.readexactly(size)
    raise ValueError("invalid frame length varint")


def _write_delimited(writer: asyncio.StreamWriter, envelope: pb.Envelope) -> None:
    data = envelope.SerializeToString()
    if len(data) > _MAX_REQUEST_FRAME_BYTES:
        raise CmdopConnectionError(
            f"request frame exceeds {_MAX_REQUEST_FRAME_BYTES} bytes",
            code="transport",
        )
    writer.write(_VarintBytes(len(data)) + data)


def _fail_stream(queue: asyncio.Queue[object], error: Exception) -> None:
    """Discard buffered frames and deliver one terminal error without blocking."""
    while True:
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            break
    queue.put_nowait(error)
    queue.put_nowait(_STREAM_END)


class Transport:
    def __init__(self, config: ClientConfig, binary_path: str) -> None:
        self._config = config
        self._binary_path = binary_path
        self._process: asyncio.subprocess.Process | None = None
        self._reader_task: asyncio.Task[None] | None = None
        self._stderr_task: asyncio.Task[None] | None = None
        self._pending: dict[int, _UnaryPending | _StreamPending] = {}
        self._next_id = 1
        self._closed = False
        self._start_lock = asyncio.Lock()

    async def _ensure_started(self) -> None:
        if self._process is not None:
            return
        async with self._start_lock:
            if self._process is not None:
                return
            env = dict(os.environ)
            if self._config.token:
                env["CMDOP_TOKEN"] = self._config.token
            else:
                env.pop("CMDOP_TOKEN", None)
            if self._config.base_url:
                env["CMDOP_BASE_URL"] = self._config.base_url
            else:
                env.pop("CMDOP_BASE_URL", None)
            self._process = await asyncio.create_subprocess_exec(
                self._binary_path,
                "--stdio",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            self._reader_task = asyncio.create_task(self._read_loop())
            self._stderr_task = asyncio.create_task(self._drain_stderr())

    async def _drain_stderr(self) -> None:
        assert self._process is not None and self._process.stderr is not None
        while await self._process.stderr.readline():
            pass

    async def _read_loop(self) -> None:
        assert self._process is not None and self._process.stdout is not None
        try:
            while True:
                envelope = pb.Envelope.FromString(
                    await _read_delimited(self._process.stdout)
                )
                self._dispatch(envelope)
        except asyncio.IncompleteReadError:
            self._fail_all(CmdopConnectionError("cmdop-core exited", code="transport"))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            self._fail_all(
                CmdopConnectionError(f"core read failed: {exc}", code="transport")
            )

    def _dispatch(self, envelope: pb.Envelope) -> None:
        pending = self._pending.get(envelope.id)
        if pending is None:
            return
        if isinstance(pending, _UnaryPending):
            if envelope.kind == pb.Envelope.KIND_ERROR:
                self._pending.pop(envelope.id, None)
                if not pending.future.done():
                    pending.future.set_exception(map_core_error(envelope.error))
            elif envelope.kind == pb.Envelope.KIND_RESPONSE:
                self._pending.pop(envelope.id, None)
                if not pending.future.done():
                    pending.future.set_result(envelope)
            return
        if envelope.kind == pb.Envelope.KIND_EVENT:
            try:
                pending.queue.put_nowait(envelope)
            except asyncio.QueueFull:
                self._pending.pop(envelope.id, None)
                _fail_stream(
                    pending.queue,
                    CmdopConnectionError(
                        "agent stream consumer is too slow", code="transport"
                    ),
                )
        elif envelope.kind == pb.Envelope.KIND_DONE:
            self._pending.pop(envelope.id, None)
            if pending.queue.qsize() > pending.queue.maxsize - 2:
                _fail_stream(
                    pending.queue,
                    CmdopConnectionError(
                        "agent stream consumer is too slow", code="transport"
                    ),
                )
            else:
                pending.queue.put_nowait(envelope)
                pending.queue.put_nowait(_STREAM_END)
        elif envelope.kind == pb.Envelope.KIND_ERROR:
            self._pending.pop(envelope.id, None)
            _fail_stream(pending.queue, map_core_error(envelope.error))

    def _fail_all(self, error: Exception) -> None:
        pending, self._pending = self._pending, {}
        for call in pending.values():
            if isinstance(call, _UnaryPending):
                if not call.future.done():
                    call.future.set_exception(error)
            else:
                _fail_stream(call.queue, error)

    def _allocate_id(self) -> int:
        call_id = self._next_id
        self._next_id += 1
        return call_id

    async def _write(self, envelope: pb.Envelope) -> None:
        await self._ensure_started()
        assert self._process is not None and self._process.stdin is not None
        _write_delimited(self._process.stdin, envelope)
        await self._process.stdin.drain()

    async def call_unary(self, request: pb.Envelope) -> pb.Envelope:
        request.id = self._allocate_id()
        request.kind = pb.Envelope.KIND_REQUEST
        future = asyncio.get_running_loop().create_future()
        self._pending[request.id] = _UnaryPending(future)
        try:
            await self._write(request)
            return await asyncio.wait_for(
                asyncio.shield(future), self._config.timeout_ms / 1000
            )
        except (TimeoutError, asyncio.TimeoutError) as exc:
            self._pending.pop(request.id, None)
            future.cancel()
            raise CmdopTimeoutError(
                "cmdop-core request timed out", code="deadline_exceeded"
            ) from exc
        except BaseException:
            self._pending.pop(request.id, None)
            raise

    def call_stream(self, request: pb.Envelope) -> AskStream:
        return AskStream(self, request, self._config.timeout_ms)

    async def _start_stream(
        self, request: pb.Envelope
    ) -> tuple[int, asyncio.Queue[object]]:
        request.id = self._allocate_id()
        request.kind = pb.Envelope.KIND_REQUEST
        queue: asyncio.Queue[object] = asyncio.Queue(maxsize=_STREAM_QUEUE_SIZE)
        self._pending[request.id] = _StreamPending(queue)
        try:
            await self._write(request)
        except BaseException:
            self._pending.pop(request.id, None)
            raise
        return request.id, queue

    def _abandon_stream(self, call_id: int) -> None:
        self._pending.pop(call_id, None)

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        process = self._process
        if process is None:
            return
        if process.stdin is not None:
            process.stdin.close()
        try:
            await asyncio.wait_for(process.wait(), 5)
        except (TimeoutError, asyncio.TimeoutError):
            process.kill()
            await process.wait()
        for task in (self._reader_task, self._stderr_task):
            if task is not None:
                task.cancel()
        self._fail_all(CmdopConnectionError("client closed", code="transport"))
