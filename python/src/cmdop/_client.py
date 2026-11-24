"""The cmdop client, sync (developer SDK plan, section 4). `_async.py` is the same, awaited.

Every tool, its arguments and result, the error codes and the call shapes come from `generated/`. This file speaks the
call contract only; which channel carries it is the carrier's business (`carriers/`), and nothing here knows it.
End-to-end calls come through a sealer (`e2e`, `_sealing.py`): this file holds no key and reads no sealed text.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterator
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from typing_extensions import Unpack

from ._errors import CarrierError, CmdopError
from ._sealing import Sealing
from .carriers import Carrier, HttpCarrier, Json
from .carriers._carrier import is_answer
from .generated import args as a
from .generated import models as m
from .generated.call import OutputChunk
from .generated.tools import Tools

T = TypeVar("T", bound=BaseModel)


def url_of(url: str | None = None, contour: str | None = None) -> str:
    """`url` as given, else `https://<contour>.cmdop.dev`; `CMDOP_URL` when neither is given."""
    if url and contour:
        raise ValueError("connect: give url or contour, not both")
    if contour is not None:
        if not contour or not all(c.isascii() and (c.isalnum() or c == "-") and not c.isupper() for c in contour):
            raise ValueError(f"connect: {contour!r} is not a contour address")
        return f"https://{contour}.cmdop.dev"
    url = url or os.environ.get("CMDOP_URL")
    if not url:
        raise ValueError("connect: no address; set CMDOP_URL (your page's address, https://<address>.cmdop.dev) or pass url")
    return url.rstrip("/")


def token_of(token: str | None) -> str:
    token = token or os.environ.get("CMDOP_TOKEN")
    if not token:
        raise ValueError("connect: no token; set CMDOP_TOKEN or pass token")
    return token


def carrier_name(carrier: str | None) -> str:
    want = carrier or os.environ.get("CMDOP_CARRIER") or "auto"
    # One door exists today, so `auto` is HTTP. A second carrier adds its probe here, never a branch in the client.
    if want in ("auto", "http"):
        return "http"
    raise ValueError(f"connect: unknown carrier {want!r} (auto, http)")


def request(tool: str, args: dict[str, Any], machine: str | None, deadline: float | None) -> Json:
    """The contract's `CallRequest`. `deadline` is in seconds; the call keeps the shorter of it and the tool's time."""
    req: Json = {"tool": tool, "args": args}
    if machine is not None:
        req["machine"] = machine
    if deadline is not None:
        req["deadline_ms"] = max(0, round(deadline * 1000))
    return req


def settle(answer: Json) -> Any:
    """The result of an answer, or its refusal as a `CmdopError`."""
    if "ok" in answer:
        return answer["ok"]
    e = answer.get("error")
    if isinstance(e, dict):
        err: dict[str, Any] = e  # pyright: ignore[reportUnknownVariableType]
        details = err.get("details")
        raise CmdopError(str(err.get("code", "other")), str(err.get("message", "")), details if isinstance(details, dict) else None)  # pyright: ignore[reportUnknownArgumentType]
    raise CmdopError("not_sealed", "a sealed answer reached a call that was not sealed")


class Piece(OutputChunk):
    """One piece of a running command's output, with its place in the call."""

    seq: int


def piece(line: Json) -> Piece | None:
    if "chunk" in line:
        return Piece.model_validate({**line["chunk"], "seq": line["seq"]})
    if "sealed_chunk" in line:
        raise CmdopError("not_sealed", "a sealed piece reached a call that was not sealed")
    return None


R = TypeVar("R")


class Run(Generic[R]):
    """A call with its output followed: iterate for the pieces, then read `result`. Leaving the loop early, or
    `cancel()`, stops the call, and `result` then raises `cancelled`."""

    def __init__(self, lines: Iterator[Json], parse: Callable[[Any], R]) -> None:
        self._lines = lines
        self._parse = parse
        self._result: tuple[R] | None = None
        self._error: BaseException | None = None
        self._started = False

    def __iter__(self) -> Iterator[Piece]:
        self._started = True
        try:
            for line in self._lines:
                if is_answer(line):
                    self._result = (self._parse(settle(line)),)
                    return
                p = piece(line)
                if p is not None:
                    yield p
            raise CarrierError("stream", "the stream ended without an answer")
        except BaseException as e:
            if not isinstance(e, GeneratorExit):
                self._error = e
            raise
        finally:
            self.cancel()

    @property
    def result(self) -> R:
        """The call's result. Reading it before iterating skips the pieces."""
        if not self._started:
            for _ in self:
                pass
        if self._result is not None:
            return self._result[0]
        if self._error is not None:
            raise self._error
        raise CmdopError("cancelled", "the call was stopped by its caller")

    def cancel(self) -> None:
        close = getattr(self._lines, "close", None)
        if callable(close):
            close()

    def __enter__(self) -> Run[R]:
        return self

    def __exit__(self, *_: object) -> None:
        self.cancel()


class Machine(Tools):
    """One machine: every tool as a method (`box.fs_read(path=...)`) and two short forms."""

    def __init__(self, client: Client, name: str | None) -> None:
        self._client = client
        self.name = name

    def _tool(self, name: str, args: dict[str, Any], out: type[T], deadline: float | None) -> T:
        return out.model_validate(self._client.call(name, args, machine=self.name, deadline=deadline))

    def run(self, command: str, /, *, deadline: float | None = None, **args: Unpack[a.ExecRunArgs]) -> m.ExecRunOut:
        """`exec_run` with a shell command line."""
        return self.exec_run(deadline=deadline, **{**args, "command": command})

    def stream(self, command: str, /, *, deadline: float | None = None, **args: Unpack[a.ExecRunArgs]) -> Run[m.ExecRunOut]:
        """`exec_run` with its output as it comes."""
        return self._client.stream("exec_run", {**args, "command": command}, machine=self.name, deadline=deadline, out=m.ExecRunOut)


class Client:
    """Your machines. Use `cmdop.connect()`; close it, or use it as a context manager."""

    def __init__(self, carrier: Carrier, e2e: Sealing | None = None) -> None:
        self.carrier_impl = carrier
        self._sealer = e2e

    @property
    def carrier(self) -> str:
        """Which carrier is in use (`"http"`, …): what `auto` picked."""
        return self.carrier_impl.name

    def machines(self) -> list[Json]:
        """The contour's machines: name, id, online, os, tools."""
        rows: list[Json] = settle(self.carrier_impl.machines())
        return rows

    def machine(self, name: str | None = None) -> Machine:
        """One machine; no name: the one online machine (the server decides)."""
        return Machine(self, name)

    def call(self, tool: str, args: dict[str, Any], *, machine: str | None = None, deadline: float | None = None) -> Any:
        """Runs any tool by name; the result as JSON."""
        req = request(tool, args, machine, deadline)
        if self._sealer is None:
            return settle(self.carrier_impl.call(req))
        sealed, replies = self._sealer.seal(req, self.machines(), time.time())
        return settle(self._sealer.open_answer(self.carrier_impl.call(sealed), replies))

    def stream(
        self, tool: str, args: dict[str, Any], *, machine: str | None = None, deadline: float | None = None, out: type[T] | None = None
    ) -> Run[Any]:
        """Runs any tool by name as a streamed call: its pieces as they come (only `exec_run` sends any), then its
        result, as `out` when given, else as JSON."""
        req = request(tool, args, machine, deadline)
        if self._sealer is None:
            lines = iter(self.carrier_impl.stream(req))
        else:
            sealer = self._sealer
            sealed, replies = sealer.seal(req, self.machines(), time.time())
            lines = (sealer.open_line(line, replies) for line in self.carrier_impl.stream(sealed))
        return Run(lines, out.model_validate if out is not None else (lambda v: v))

    def public_key(self) -> str:
        """With `e2e`: this client's public key, for `cmdop pair <key>` on each machine."""
        if self._sealer is None:
            raise CmdopError("bad_args", "this client was made without e2e")
        return self._sealer.public_key()

    def close(self) -> None:
        self.carrier_impl.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def connect(
    token: str | None = None,
    url: str | None = None,
    *,
    contour: str | None = None,
    carrier: str | Carrier | None = None,
    e2e: Sealing | None = None,
) -> Client:
    """Connect to your contour: the token from `CMDOP_TOKEN`, the address from `CMDOP_URL` unless given. `carrier` is
    `"auto"` (default, or `CMDOP_CARRIER`), `"http"`, or a carrier of your own (tests: `MemoryCarrier`). With `e2e`
    every call is sealed for the machine by that sealer."""
    if carrier is not None and not isinstance(carrier, str):
        return Client(carrier, e2e)
    carrier_name(carrier)
    return Client(HttpCarrier(url_of(url, contour), token_of(token)), e2e)
