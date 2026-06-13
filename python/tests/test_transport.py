"""Transport demux tests: feed canned length-delimited Envelope frames through
the read loop and assert unary + streamed-ask (all frame types) + pin/confirm.

No real ``cmdop-core`` is spawned. A :class:`FakeProc` provides:
  * ``stdin``  — a writer that captures bytes the transport sends, and that a
    test "core" coroutine reads (so it can learn the id the transport allocated
    and reply on it).
  * ``stdout`` — an :class:`asyncio.StreamReader` the test core feeds canned
    response frames into (varint-length-delimited, exactly the wire format).
"""

from __future__ import annotations

import asyncio

import pytest
from google.protobuf.internal.encoder import _VarintBytes

from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop._proto.cmdop.core.v1 import machines_pb2 as m_pb
from cmdop._transport import Transport, _read_delimited
from cmdop.config import ClientConfig
from cmdop.errors import (
    AgentStreamError,
    AuthError,
    ConflictError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    ValidationError,
)

# --- fakes ----------------------------------------------------------------


class _CaptureWriter:
    """A StreamWriter-like sink: bytes land on an asyncio.StreamReader the test
    'core' reads, so the core sees exactly what the transport wrote."""

    def __init__(self, sink: asyncio.StreamReader) -> None:
        self._sink = sink

    def write(self, data: bytes) -> None:
        self._sink.feed_data(data)

    def close(self) -> None:
        self._sink.feed_eof()

    async def drain(self) -> None:
        return None


class FakeProc:
    def __init__(self) -> None:
        self.stdout = asyncio.StreamReader()  # core -> client
        self.stderr = asyncio.StreamReader()
        self.stderr.feed_eof()
        self._client_to_core = asyncio.StreamReader()  # client -> core
        self.stdin = _CaptureWriter(self._client_to_core)
        self.returncode = None

    async def wait(self) -> int:
        return 0

    def kill(self) -> None:
        self.returncode = -9


def _make_transport() -> tuple[Transport, FakeProc]:
    cfg = ClientConfig.resolve(token="t", base_url="https://x")
    t = Transport(cfg, "/nonexistent/cmdop-core")
    proc = FakeProc()
    # Wire the fake proc in without spawning.
    t._proc = proc  # type: ignore[assignment]
    t._reader_task = asyncio.get_running_loop().create_task(t._read_loop())
    return t, proc


def _feed(proc: FakeProc, env: pb.Envelope) -> None:
    """Feed one length-delimited Envelope into the core->client stream."""
    data = env.SerializeToString()
    proc.stdout.feed_data(_VarintBytes(len(data)))
    proc.stdout.feed_data(data)


async def _read_request(proc: FakeProc) -> pb.Envelope:
    body = await _read_delimited(proc._client_to_core)
    env = pb.Envelope()
    env.ParseFromString(body)
    return env


# --- tests ----------------------------------------------------------------


@pytest.mark.asyncio
async def test_unary_response_round_trip() -> None:
    t, proc = _make_transport()

    async def core() -> None:
        req = await _read_request(proc)
        assert req.kind == pb.Envelope.KIND_REQUEST
        assert req.WhichOneof("payload") == "list_machines_req"
        _feed(
            proc,
            pb.Envelope(
                id=req.id,
                kind=pb.Envelope.KIND_RESPONSE,
                machine_list=m_pb.MachineList(
                    items=[m_pb.MachineSummary(id="m1", hostname="work")]
                ),
            ),
        )

    core_task = asyncio.create_task(core())
    resp = await t.call_unary(pb.Envelope(list_machines_req=m_pb.ListMachinesRequest(presence="any")))
    await core_task

    assert resp.kind == pb.Envelope.KIND_RESPONSE
    assert resp.machine_list.items[0].hostname == "work"
    await t.aclose()


@pytest.mark.asyncio
async def test_unary_error_maps_to_typed_exception() -> None:
    t, proc = _make_transport()

    async def core() -> None:
        req = await _read_request(proc)
        _feed(
            proc,
            pb.Envelope(
                id=req.id,
                kind=pb.Envelope.KIND_ERROR,
                error=m_pb.ErrorInfo(code="auth", message="missing token"),
            ),
        )

    core_task = asyncio.create_task(core())
    with pytest.raises(AuthError, match="missing token"):
        await t.call_unary(pb.Envelope(list_machines_req=m_pb.ListMachinesRequest()))
    await core_task
    await t.aclose()


@pytest.mark.asyncio
async def test_ask_stream_all_frame_types_with_pin_and_confirm() -> None:
    t, proc = _make_transport()

    async def core() -> None:
        req = await _read_request(proc)
        assert req.WhichOneof("payload") == "ask_req"
        i = req.id
        # event
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_EVENT,
              ask_frame=m_pb.AskFrame(event=m_pb.StreamEvent(event_type=1, payload_json='{"delta":"hi "}'))))
        # pin_required (CALLBACK) -> expect a pin ANSWER on the same id
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_CALLBACK,
              pin_required=m_pb.PinRequired(challenge_id="c9", label="Connect PIN")))
        ans = await _read_request(proc)
        assert ans.kind == pb.Envelope.KIND_ANSWER
        assert ans.id == i
        assert ans.pin_answer.pin == "1234"
        # pin_denied (EVENT)
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_EVENT,
              ask_frame=m_pb.AskFrame(pin_denied=m_pb.PinDenied(challenge_id="c9", reason="bad"))))
        # confirm_required (CALLBACK) -> expect a confirm ANSWER
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_CALLBACK,
              confirm_required=m_pb.ConfirmRequired(token="tok", plan="rm -rf", danger_level="high")))
        ans2 = await _read_request(proc)
        assert ans2.kind == pb.Envelope.KIND_ANSWER
        assert ans2.confirm_answer.token == "tok"
        assert ans2.confirm_answer.accept is True
        # another event delta, then done
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_EVENT,
              ask_frame=m_pb.AskFrame(event=m_pb.StreamEvent(event_type=1, payload_json='{"delta":"done"}'))))
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_DONE,
              done=m_pb.DoneInfo(success=True, text="hi done", duration_ms=42)))

    core_task = asyncio.create_task(core())

    stream = t.call_stream(pb.Envelope(ask_req=m_pb.AskRequest(machine_id="m1", prompt="x")))
    kinds: list[str] = []
    async for frame in stream:
        kinds.append(frame.type)
        if frame.type == "pin_required":
            await stream.pin(frame.challenge_id, "1234")
        elif frame.type == "confirm_required":
            await stream.confirm(frame.token, accept=True)
        elif frame.type == "done":
            assert frame.text == "hi done"
            assert frame.duration_ms == 42

    await core_task
    assert kinds == ["event", "pin_required", "pin_denied", "confirm_required", "event", "done"]
    await t.aclose()


@pytest.mark.asyncio
async def test_ask_stream_error_frame_raises() -> None:
    t, proc = _make_transport()

    async def core() -> None:
        req = await _read_request(proc)
        _feed(proc, pb.Envelope(id=req.id, kind=pb.Envelope.KIND_ERROR,
              error=m_pb.ErrorInfo(code="connection", message="machine offline")))

    core_task = asyncio.create_task(core())
    stream = t.call_stream(pb.Envelope(ask_req=m_pb.AskRequest(machine_id="m1", prompt="x")))
    with pytest.raises(AgentStreamError, match="machine offline"):
        async for _ in stream:
            pass
    await core_task
    await t.aclose()


@pytest.mark.asyncio
async def test_collect_accumulates_deltas() -> None:
    t, proc = _make_transport()

    async def core() -> None:
        req = await _read_request(proc)
        i = req.id
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_EVENT,
              ask_frame=m_pb.AskFrame(event=m_pb.StreamEvent(event_type=1, payload_json='{"delta":"foo"}'))))
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_EVENT,
              ask_frame=m_pb.AskFrame(event=m_pb.StreamEvent(event_type=1, payload_json='{"delta":"bar"}'))))
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_DONE, done=m_pb.DoneInfo(success=True)))

    core_task = asyncio.create_task(core())
    stream = t.call_stream(pb.Envelope(ask_req=m_pb.AskRequest(machine_id="m1", prompt="x")))
    text = await stream.collect()
    await core_task
    assert text == "foobar"
    await t.aclose()


@pytest.mark.asyncio
async def test_large_frame_over_64kb_round_trips() -> None:
    """A single >64 KB Envelope survives the delimited framing whole — the
    report-11 §2.2 regression guard (no readline/readexactly 64 KB cap)."""
    t, proc = _make_transport()
    big = "z" * (256 * 1024)  # 256 KB, well past the old 64 KB NDJSON trap

    async def core() -> None:
        req = await _read_request(proc)
        # The big payload round-tripped IN (request prompt) too: prove it.
        assert len(req.ask_req.prompt) == len(big)
        i = req.id
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_EVENT,
              ask_frame=m_pb.AskFrame(event=m_pb.StreamEvent(
                  event_type=1, payload_json='{"delta":"' + big + '"}'))))
        _feed(proc, pb.Envelope(id=i, kind=pb.Envelope.KIND_DONE, done=m_pb.DoneInfo(success=True)))

    core_task = asyncio.create_task(core())
    stream = t.call_stream(pb.Envelope(ask_req=m_pb.AskRequest(machine_id="m1", prompt=big)))
    deltas = ""
    async for frame in stream:
        if frame.type == "event":
            deltas += frame.payload.get("delta", "")
    await core_task
    assert len(deltas) == len(big)
    await t.aclose()


@pytest.mark.asyncio
async def test_core_crash_rejects_pending_unary() -> None:
    """Killing the core mid-call: the in-flight unary Future rejects with a
    ConnectionError (read loop hits EOF → _fail_all)."""
    t, proc = _make_transport()

    async def core() -> None:
        await _read_request(proc)  # receive the request, then die without replying
        proc.stdout.feed_eof()

    core_task = asyncio.create_task(core())
    with pytest.raises(ConnectionError):
        await t.call_unary(pb.Envelope(list_machines_req=m_pb.ListMachinesRequest()))
    await core_task
    await t.aclose()


@pytest.mark.asyncio
async def test_core_crash_raises_on_open_stream() -> None:
    """Killing the core mid-stream surfaces a ConnectionError on the iterator."""
    t, proc = _make_transport()

    async def core() -> None:
        req = await _read_request(proc)
        # one event, then crash (EOF) before done
        _feed(proc, pb.Envelope(id=req.id, kind=pb.Envelope.KIND_EVENT,
              ask_frame=m_pb.AskFrame(event=m_pb.StreamEvent(event_type=1, payload_json='{"delta":"hi"}'))))
        proc.stdout.feed_eof()

    core_task = asyncio.create_task(core())
    stream = t.call_stream(pb.Envelope(ask_req=m_pb.AskRequest(machine_id="m1", prompt="x")))
    with pytest.raises(ConnectionError):
        async for _ in stream:
            pass
    await core_task
    await t.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("code", "exc"),
    [
        ("auth", AuthError),
        ("permission", PermissionError),
        ("not_found", NotFoundError),
        ("conflict", ConflictError),
        ("validation", ValidationError),
        ("rate_limit", RateLimitError),
        ("server", ServerError),
        ("connection", ConnectionError),
    ],
)
async def test_unary_error_code_maps_to_typed_exception(code: str, exc: type) -> None:
    """Every core ErrorInfo.code maps to its typed exception on a unary call."""
    t, proc = _make_transport()

    async def core() -> None:
        req = await _read_request(proc)
        _feed(proc, pb.Envelope(id=req.id, kind=pb.Envelope.KIND_ERROR,
              error=m_pb.ErrorInfo(code=code, message="boom")))

    core_task = asyncio.create_task(core())
    with pytest.raises(exc, match="boom"):
        await t.call_unary(pb.Envelope(get_machine_req=m_pb.GetMachineRequest(machine_id="x")))
    await core_task
    await t.aclose()
