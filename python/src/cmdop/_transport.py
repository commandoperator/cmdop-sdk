"""Async stdio transport: spawn ``cmdop-core``, frame protobuf Envelopes over
its stdin/stdout, demux by ``Envelope.id``.

Three concentric pieces (report 11 §0): this is the **hand-written transport
runtime**, written once and never touched when methods are added. Each generated
resource method is ~3 lines calling :meth:`Transport.call_unary` /
:meth:`Transport.call_stream`.

Framing (report 13 §1.4): protobuf length-delimited. ``_read_delimited`` reads
the varint size one byte at a time, then ``readexactly(size)`` for the exact
body. ``readexactly`` has **no line-length limit**, so the 64 KB ``readline``
trap that NDJSON-over-asyncio hit (report 11 §2.2) **does not exist** here — a
large ask frame (tool-call blob, long delta) is read whole. We deliberately do
NOT pass ``limit=`` to ``create_subprocess_exec`` for any readline workaround,
because we never call ``readline``.

Demux (report 11 §2.3): a ``dict[int, _Pending]`` keyed by id. A unary call gets
an :class:`asyncio.Future`; a streaming call gets an :class:`asyncio.Queue` fed
per-id by the single read loop. ``CALLBACK`` (pin/confirm) frames are pushed into
the stream's queue so the caller can answer them mid-iteration with an ``ANSWER``
envelope on the same id.
"""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

from google.protobuf.internal.decoder import _DecodeVarint32  # type: ignore[attr-defined]
from google.protobuf.internal.encoder import _VarintBytes  # type: ignore[attr-defined]

from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop.errors import ConnectionError as CmdopConnectionError
from cmdop.streaming import FrameStream

if TYPE_CHECKING:
    from cmdop.config import ClientConfig

# Sentinel pushed onto a stream queue to signal "no more frames" (terminal
# RESPONSE/DONE/ERROR already delivered).
_STREAM_END = object()


class _UnaryPending:
    __slots__ = ("fut",)

    def __init__(self, fut: asyncio.Future) -> None:
        self.fut = fut


class _StreamPending:
    __slots__ = ("queue",)

    def __init__(self, queue: asyncio.Queue) -> None:
        self.queue = queue


_Pending = _UnaryPending | _StreamPending


async def _read_delimited(reader: asyncio.StreamReader) -> bytes:
    """Read one length-delimited protobuf body off ``reader``.

    Reads the varint length one byte at a time (high bit = continue), then the
    exact body. ``readexactly`` has no buffer-size cap, so there is no 64 KB
    readline trap (report 13 §1.4 — this is *why* proto framing replaced NDJSON).
    Raises :class:`asyncio.IncompleteReadError` at EOF.
    """
    buf = b""
    while True:
        b = await reader.readexactly(1)
        buf += b
        if not (b[0] & 0x80):
            break
    size, _ = _DecodeVarint32(buf, 0)
    return await reader.readexactly(size)


def _write_delimited(writer: asyncio.StreamWriter, env: pb.Envelope) -> None:
    """Write ``env`` as a varint-size-prefixed protobuf frame."""
    data = env.SerializeToString()
    writer.write(_VarintBytes(len(data)))
    writer.write(data)


class Transport:
    """Owns one persistent ``cmdop-core`` subprocess and the id-mux over it."""

    def __init__(self, cfg: ClientConfig, bin_path: str) -> None:
        self._cfg = cfg
        self._bin = bin_path
        self._proc: asyncio.subprocess.Process | None = None
        self._reader_task: asyncio.Task | None = None
        self._stderr_task: asyncio.Task | None = None
        self._pending: dict[int, _Pending] = {}
        self._next_id = 1
        self._closed = False
        self._start_lock = asyncio.Lock()

    # -- lifecycle ---------------------------------------------------------

    async def _ensure_started(self) -> asyncio.subprocess.Process:
        if self._proc is not None:
            return self._proc
        async with self._start_lock:
            if self._proc is not None:
                return self._proc
            env = {
                **os.environ,
                "CMDOP_TOKEN": self._cfg.token,
                "CMDOP_BASE_URL": self._cfg.base_url,
                # Django platform plane (skills) — separate credential + base URL.
                "CMDOP_API_BASE_URL": self._cfg.api_base_url,
            }
            if self._cfg.api_key:
                env["CMDOP_API_KEY"] = self._cfg.api_key
            proc = await asyncio.create_subprocess_exec(
                self._bin,
                "--stdio",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            self._proc = proc
            self._reader_task = asyncio.create_task(self._read_loop())
            self._stderr_task = asyncio.create_task(self._drain_stderr())
            return proc

    async def _drain_stderr(self) -> None:
        """Drain the core's stderr so its diagnostics never block / corrupt the
        protocol pipe. We discard it (set CMDOP_DEBUG=1 to have the core log to a
        file); a host that wants it can read the core's log file."""
        assert self._proc is not None and self._proc.stderr is not None
        try:
            while True:
                line = await self._proc.stderr.readline()
                if not line:
                    return
        except Exception:  # noqa: BLE001 - stderr drain must never raise
            return

    async def _read_loop(self) -> None:
        assert self._proc is not None and self._proc.stdout is not None
        reader = self._proc.stdout
        try:
            while True:
                body = await _read_delimited(reader)
                env = pb.Envelope()
                env.ParseFromString(body)
                self._dispatch(env)
        except asyncio.IncompleteReadError:
            self._fail_all(CmdopConnectionError("cmdop-core exited"))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            self._fail_all(CmdopConnectionError(f"core read loop failed: {exc}"))

    def _dispatch(self, env: pb.Envelope) -> None:
        """Route a frame by id, branch on kind (report 13 §4.1)."""
        p = self._pending.get(env.id)
        if p is None:
            return
        kind = env.kind

        if isinstance(p, _UnaryPending):
            if kind == pb.Envelope.KIND_ERROR:
                self._pending.pop(env.id, None)
                if not p.fut.done():
                    p.fut.set_exception(self._to_error(env))
            elif kind == pb.Envelope.KIND_RESPONSE:
                self._pending.pop(env.id, None)
                if not p.fut.done():
                    p.fut.set_result(env)
            # Any other kind on a unary id is a protocol violation — ignore.
            return

        # Streaming call (machines.ask): EVENT/CALLBACK push; DONE/ERROR/RESPONSE
        # terminate.
        queue = p.queue
        if kind in (pb.Envelope.KIND_EVENT, pb.Envelope.KIND_CALLBACK):
            queue.put_nowait(env)
        elif kind == pb.Envelope.KIND_DONE:
            self._pending.pop(env.id, None)
            queue.put_nowait(env)
            queue.put_nowait(_STREAM_END)
        elif kind == pb.Envelope.KIND_ERROR:
            # Push the raw ERROR envelope; FrameStream raises it as an
            # AgentStreamError (the ask stream's error-frame semantics, mirroring
            # the archived wrapper) rather than the unary code->exception map.
            self._pending.pop(env.id, None)
            queue.put_nowait(env)
            queue.put_nowait(_STREAM_END)
        elif kind == pb.Envelope.KIND_RESPONSE:
            # A unary-shaped reply on a stream id (shouldn't happen for ask, but
            # be forgiving): deliver then end.
            self._pending.pop(env.id, None)
            queue.put_nowait(env)
            queue.put_nowait(_STREAM_END)

    @staticmethod
    def _to_error(env: pb.Envelope) -> Exception:
        from cmdop.errors import map_core_error

        info = env.error
        return map_core_error(info.code or "internal", info.message or "")

    def _fail_all(self, exc: Exception) -> None:
        """EOF / crash: fail every in-flight call."""
        pending, self._pending = self._pending, {}
        for p in pending.values():
            if isinstance(p, _UnaryPending):
                if not p.fut.done():
                    p.fut.set_exception(exc)
            else:
                p.queue.put_nowait(exc)
                p.queue.put_nowait(_STREAM_END)

    async def aclose(self) -> None:
        """Close stdin (graceful drain), reap the child, cancel the read loop."""
        if self._closed:
            return
        self._closed = True
        proc = self._proc
        if proc is None:
            return
        try:
            if proc.stdin is not None:
                proc.stdin.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=5)
        except (TimeoutError, asyncio.TimeoutError):
            proc.kill()
            await proc.wait()
        for task in (self._reader_task, self._stderr_task):
            if task is not None:
                task.cancel()
                try:
                    await task
                except (asyncio.CancelledError, Exception):  # noqa: BLE001
                    pass
        self._fail_all(CmdopConnectionError("client closed"))

    # -- write path --------------------------------------------------------

    def _alloc_id(self) -> int:
        i = self._next_id
        self._next_id += 1
        return i

    def _write(self, env: pb.Envelope) -> None:
        proc = self._proc
        if proc is None or proc.stdin is None:
            raise CmdopConnectionError("cmdop-core not running")
        _write_delimited(proc.stdin, env)

    async def write_answer(self, env: pb.Envelope) -> None:
        """Write an ANSWER envelope (pin/confirm) on an open stream's id."""
        await self._ensure_started()
        self._write(env)
        if self._proc is not None and self._proc.stdin is not None:
            await self._proc.stdin.drain()

    # -- call entry points (used by generated resources) -------------------

    async def call_unary(self, req: pb.Envelope) -> pb.Envelope:
        """Send a REQUEST envelope, await the RESPONSE/ERROR on its id.

        ``req`` must already carry ``kind=KIND_REQUEST`` and the right oneof arm;
        ``id`` is assigned here. Returns the response Envelope (caller reads the
        typed arm); raises a typed :class:`CmdopError` on an ERROR frame.
        """
        await self._ensure_started()
        req.id = self._alloc_id()
        req.kind = pb.Envelope.KIND_REQUEST
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending[req.id] = _UnaryPending(fut)
        self._write(req)
        assert self._proc is not None and self._proc.stdin is not None
        await self._proc.stdin.drain()
        return await fut

    def call_stream(self, req: pb.Envelope) -> FrameStream:
        """Open a streaming call (machines.ask). Returns a :class:`FrameStream`
        whose first iteration sends the REQUEST and yields typed frames."""
        return FrameStream(self, req)

    async def _start_stream(self, req: pb.Envelope) -> tuple[int, asyncio.Queue]:
        """Internal: register the stream id + send its REQUEST. Called lazily by
        :class:`FrameStream` on first iteration so the same stream object can be
        re-iterated would-be-once semantics."""
        await self._ensure_started()
        req.id = self._alloc_id()
        req.kind = pb.Envelope.KIND_REQUEST
        queue: asyncio.Queue = asyncio.Queue()
        self._pending[req.id] = _StreamPending(queue)
        self._write(req)
        assert self._proc is not None and self._proc.stdin is not None
        await self._proc.stdin.drain()
        return req.id, queue
