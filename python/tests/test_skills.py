"""skills resource: surface presence + a transport round-trip through a skills op.

The transport is faked (no real ``cmdop-core`` spawned) exactly like
``test_transport.py``: a canned length-delimited Envelope is fed back on the
core->client stream, and the request the resource wrote is read off the
client->core stream and asserted. This proves the second-plane (skills) op path
builds the right Envelope arm and reads the right response arm.
"""

from __future__ import annotations

import asyncio

import pytest
from google.protobuf.internal.encoder import _VarintBytes

from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop._proto.cmdop.core.v1 import skills_pb2 as s_pb
from cmdop._transport import Transport, _read_delimited
from cmdop.config import ClientConfig
from cmdop.errors import AuthError
from cmdop.resources.skills import SkillsResource


class _CaptureWriter:
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
        self.stdout = asyncio.StreamReader()
        self.stderr = asyncio.StreamReader()
        self.stderr.feed_eof()
        self._client_to_core = asyncio.StreamReader()
        self.stdin = _CaptureWriter(self._client_to_core)
        self.returncode = None

    async def wait(self) -> int:
        return 0

    def kill(self) -> None:
        self.returncode = -9


class _FakeClient:
    """Minimal stand-in for cmdop.client.Client that SkillsResource needs."""

    def __init__(self, transport: Transport) -> None:
        self._t = transport
        self.fleet_id = None


def _make_transport() -> tuple[Transport, FakeProc]:
    cfg = ClientConfig.resolve(token="t", base_url="https://x", api_key="cmd_fake")
    t = Transport(cfg, "/nonexistent/cmdop-core")
    proc = FakeProc()
    t._proc = proc  # type: ignore[assignment]
    t._reader_task = asyncio.get_running_loop().create_task(t._read_loop())
    return t, proc


def _feed(proc: FakeProc, env: pb.Envelope) -> None:
    data = env.SerializeToString()
    proc.stdout.feed_data(_VarintBytes(len(data)))
    proc.stdout.feed_data(data)


async def _read_request(proc: FakeProc) -> pb.Envelope:
    body = await _read_delimited(proc._client_to_core)
    env = pb.Envelope()
    env.ParseFromString(body)
    return env


def test_api_key_flows_into_config() -> None:
    cfg = ClientConfig.resolve(token="t", api_key="cmd_xyz", api_base_url="https://api.example")
    assert cfg.api_key == "cmd_xyz"
    assert cfg.api_base_url == "https://api.example"


def test_surface_has_all_skills_methods() -> None:
    for name in (
        "list",
        "get",
        "my",
        "install",
        "star",
        "versions",
        "reviews",
        "create",
        "update",
        "delete",
        "publish",
        "publish_status",
        "categories",
        "tags",
    ):
        assert callable(getattr(SkillsResource, name))


@pytest.mark.asyncio
async def test_skills_list_round_trip() -> None:
    t, proc = _make_transport()
    skills = SkillsResource(_FakeClient(t))  # type: ignore[arg-type]

    async def core() -> None:
        req = await _read_request(proc)
        assert req.kind == pb.Envelope.KIND_REQUEST
        assert req.WhichOneof("payload") == "skills_list_req"
        assert req.skills_list_req.category == "ai"
        _feed(
            proc,
            pb.Envelope(
                id=req.id,
                kind=pb.Envelope.KIND_RESPONSE,
                skill_list_page=s_pb.SkillListPage(
                    count=1,
                    page=1,
                    results=[s_pb.SkillSummary(slug="browser", name="Browser")],
                ),
            ),
        )

    core_task = asyncio.create_task(core())
    page = await skills.list(category="ai")
    await core_task

    assert page.count == 1
    assert page.results[0].slug == "browser"
    await t.aclose()


@pytest.mark.asyncio
async def test_skills_install_auth_error() -> None:
    """A 401 from Django (bad/absent UserAPIKey) maps to a typed AuthError."""
    t, proc = _make_transport()
    skills = SkillsResource(_FakeClient(t))  # type: ignore[arg-type]

    # ErrorInfo lives in machines_pb2 (shared across namespaces).
    from cmdop._proto.cmdop.core.v1 import machines_pb2 as m_pb

    async def core() -> None:
        req = await _read_request(proc)
        assert req.WhichOneof("payload") == "skills_install_req"
        _feed(
            proc,
            pb.Envelope(
                id=req.id,
                kind=pb.Envelope.KIND_ERROR,
                error=m_pb.ErrorInfo(code="auth", message="invalid api key"),
            ),
        )

    core_task = asyncio.create_task(core())
    with pytest.raises(AuthError, match="invalid api key"):
        await skills.install("browser")
    await core_task
    await t.aclose()
