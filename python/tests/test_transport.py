from __future__ import annotations

import asyncio

import pytest
from google.protobuf.internal.encoder import _VarintBytes

from cmdop._proto.cmdop.core.v2 import contract_pb2 as pb
from cmdop._transport import (
    _MAX_REQUEST_FRAME_BYTES,
    _STREAM_END,
    _STREAM_QUEUE_SIZE,
    Transport,
    _read_delimited,
)
from cmdop.config import ClientConfig
from cmdop.errors import AgentStreamError, AuthError, ConnectionError


class _Writer:
    def __init__(self, sink: asyncio.StreamReader) -> None:
        self.sink = sink

    def write(self, data: bytes) -> None:
        self.sink.feed_data(data)

    def close(self) -> None:
        self.sink.feed_eof()

    async def drain(self) -> None:
        pass


class _Process:
    def __init__(self) -> None:
        self.stdout = asyncio.StreamReader()
        self.stderr = asyncio.StreamReader()
        self.stderr.feed_eof()
        self.requests = asyncio.StreamReader()
        self.stdin = _Writer(self.requests)

    async def wait(self) -> int:
        return 0

    def kill(self) -> None:
        pass


def _transport() -> tuple[Transport, _Process]:
    transport = Transport(ClientConfig(token="t", base_url="https://relay", timeout_ms=1000), "/none")
    process = _Process()
    transport._process = process  # type: ignore[assignment]
    transport._reader_task = asyncio.create_task(transport._read_loop())
    return transport, process


def _feed(process: _Process, envelope: pb.Envelope) -> None:
    data = envelope.SerializeToString()
    process.stdout.feed_data(_VarintBytes(len(data)) + data)


async def _request(process: _Process) -> pb.Envelope:
    return pb.Envelope.FromString(await _read_delimited(process.requests))


@pytest.mark.asyncio
async def test_unary_round_trip_and_error_mapping() -> None:
    transport, process = _transport()
    call = asyncio.create_task(
        transport.call_unary(pb.Envelope(system_bootstrap_req=pb.SystemBootstrapRequest()))
    )
    request = await _request(process)
    _feed(
        process,
        pb.Envelope(
            id=request.id,
            kind=pb.Envelope.KIND_RESPONSE,
            system_bootstrap_resp=pb.SystemBootstrapResponse(bundle_id="bundle"),
        ),
    )
    assert (await call).system_bootstrap_resp.bundle_id == "bundle"

    failed = asyncio.create_task(
        transport.call_unary(pb.Envelope(list_machines_req=pb.ListMachinesRequest()))
    )
    request = await _request(process)
    _feed(
        process,
        pb.Envelope(
            id=request.id,
            kind=pb.Envelope.KIND_ERROR,
            error=pb.ErrorInfo(
                code=pb.ERROR_CODE_UNAUTHENTICATED, message="missing token"
            ),
        ),
    )
    with pytest.raises(AuthError, match="missing token"):
        await failed
    await transport.aclose()


@pytest.mark.asyncio
async def test_stream_collects_events_and_rejects_failed_done() -> None:
    transport, process = _transport()
    stream = transport.call_stream(
        pb.Envelope(
            ask_machine_req=pb.AskMachineRequest(machine_id="m1", prompt="hello")
        )
    )
    collected = asyncio.create_task(stream.collect())
    request = await _request(process)
    _feed(
        process,
        pb.Envelope(
            id=request.id,
            kind=pb.Envelope.KIND_EVENT,
            ask_event=pb.AskEvent(event_type=pb.AGENT_EVENT_TYPE_TOKEN, payload_json='{"delta":"hi"}'),
        ),
    )
    _feed(
        process,
        pb.Envelope(
            id=request.id,
            kind=pb.Envelope.KIND_DONE,
            ask_done=pb.AskDone(success=True),
        ),
    )
    assert await collected == "hi"
    await transport.aclose()

    transport, process = _transport()
    failed = asyncio.create_task(
        transport.call_stream(
            pb.Envelope(ask_machine_req=pb.AskMachineRequest(machine_id="m1", prompt="x"))
        ).collect()
    )
    request = await _request(process)
    _feed(
        process,
        pb.Envelope(
            id=request.id,
            kind=pb.Envelope.KIND_EVENT,
            ask_stream_error=pb.AskStreamError(
                code=pb.ASK_STREAM_ERROR_CODE_MACHINE_OFFLINE, message="offline"
            ),
        ),
    )
    _feed(
        process,
        pb.Envelope(
            id=request.id,
            kind=pb.Envelope.KIND_DONE,
            ask_done=pb.AskDone(success=False, error="offline"),
        ),
    )
    with pytest.raises(AgentStreamError, match="offline"):
        await failed
    await transport.aclose()


@pytest.mark.asyncio
async def test_large_frame_round_trip() -> None:
    transport, process = _transport()
    large = "x" * (256 * 1024)
    call = asyncio.create_task(
        transport.call_unary(pb.Envelope(system_bootstrap_req=pb.SystemBootstrapRequest()))
    )
    request = await _request(process)
    _feed(
        process,
        pb.Envelope(
            id=request.id,
            kind=pb.Envelope.KIND_RESPONSE,
            system_bootstrap_resp=pb.SystemBootstrapResponse(bundle_id=large),
        ),
    )
    assert len((await call).system_bootstrap_resp.bundle_id) == len(large)
    await transport.aclose()


@pytest.mark.asyncio
async def test_slow_stream_consumer_fails_closed_without_stopping_reader() -> None:
    transport, process = _transport()
    stream_request = pb.Envelope(
        ask_machine_req=pb.AskMachineRequest(machine_id="slow", prompt="hello")
    )
    call_id, queue = await transport._start_stream(stream_request)
    assert (await _request(process)).id == call_id

    event = pb.Envelope(
        id=call_id,
        kind=pb.Envelope.KIND_EVENT,
        ask_event=pb.AskEvent(event_type=pb.AGENT_EVENT_TYPE_TOKEN),
    )
    for _ in range(_STREAM_QUEUE_SIZE + 1):
        _feed(process, event)

    for _ in range(100):
        if call_id not in transport._pending:
            break
        await asyncio.sleep(0)

    assert call_id not in transport._pending
    error = queue.get_nowait()
    assert isinstance(error, ConnectionError)
    assert str(error) == "agent stream consumer is too slow"
    assert queue.get_nowait() is _STREAM_END
    assert transport._reader_task is not None
    assert not transport._reader_task.done()

    other = asyncio.create_task(
        transport.call_unary(
            pb.Envelope(system_bootstrap_req=pb.SystemBootstrapRequest())
        )
    )
    request = await _request(process)
    _feed(
        process,
        pb.Envelope(
            id=request.id,
            kind=pb.Envelope.KIND_RESPONSE,
            system_bootstrap_resp=pb.SystemBootstrapResponse(bundle_id="still-alive"),
        ),
    )
    assert (await other).system_bootstrap_resp.bundle_id == "still-alive"
    await transport.aclose()


@pytest.mark.asyncio
async def test_oversized_request_is_rejected_locally_and_reader_survives() -> None:
    transport, process = _transport()
    oversized = asyncio.create_task(
        transport.call_unary(
            pb.Envelope(
                ask_machine_req=pb.AskMachineRequest(
                    machine_id="m1", prompt="x" * _MAX_REQUEST_FRAME_BYTES
                )
            )
        )
    )
    with pytest.raises(ConnectionError, match="request frame exceeds"):
        await oversized
    assert not transport._pending
    assert transport._reader_task is not None
    assert not transport._reader_task.done()
    assert process.requests.at_eof() is False
    await transport.aclose()
