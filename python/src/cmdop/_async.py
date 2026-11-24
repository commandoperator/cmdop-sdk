"""The cmdop client, awaited: the same calls as `_client.py` on an async carrier."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator, Callable
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ._client import Piece, carrier_name, piece, request, settle, token_of, url_of
from ._errors import CarrierError, CmdopError
from ._sealing import Sealing
from .carriers import AsyncCarrier, AsyncHttpCarrier, Json
from .carriers._carrier import is_answer
from .generated.tools import AsyncTools

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")


class AsyncRun(Generic[R]):
    """A call with its output followed: `async for` the pieces, then `await run.result()`. Leaving the loop early
    stops the call, and `result()` then raises `cancelled`."""

    def __init__(self, lines: AsyncIterator[Json], parse: Callable[[Any], R]) -> None:
        self._lines = lines
        self._parse = parse
        self._result: tuple[R] | None = None
        self._error: BaseException | None = None
        self._started = False

    async def __aiter__(self) -> AsyncIterator[Piece]:
        self._started = True
        try:
            async for line in self._lines:
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
            await self.cancel()

    async def result(self) -> R:
        """The call's result. Awaiting it before iterating skips the pieces."""
        if not self._started:
            async for _ in self:
                pass
        if self._result is not None:
            return self._result[0]
        if self._error is not None:
            raise self._error
        raise CmdopError("cancelled", "the call was stopped by its caller")

    async def cancel(self) -> None:
        close = getattr(self._lines, "aclose", None)
        if callable(close):
            await close()  # pyright: ignore[reportUnknownVariableType, reportGeneralTypeIssues]


class AsyncMachine(AsyncTools):
    def __init__(self, client: AsyncClient, name: str | None) -> None:
        self._client = client
        self.name = name

    async def _tool(self, name: str, args: dict[str, Any], out: type[T], deadline: float | None) -> T:
        return out.model_validate(await self._client.call(name, args, machine=self.name, deadline=deadline))

    def _stream(self, name: str, args: dict[str, Any], out: type[T], deadline: float | None) -> AsyncRun[T]:
        return self._client.stream(name, args, machine=self.name, deadline=deadline, out=out)


class AsyncClient:
    def __init__(self, carrier: AsyncCarrier, e2e: Sealing | None = None) -> None:
        self.carrier_impl = carrier
        self._sealer = e2e

    @property
    def carrier(self) -> str:
        return self.carrier_impl.name

    async def machines(self) -> list[Json]:
        rows: list[Json] = settle(await self.carrier_impl.machines())
        return rows

    def machine(self, name: str | None = None) -> AsyncMachine:
        return AsyncMachine(self, name)

    async def call(self, tool: str, args: dict[str, Any], *, machine: str | None = None, deadline: float | None = None) -> Any:
        req = request(tool, args, machine, deadline)
        if self._sealer is None:
            return settle(await self.carrier_impl.call(req))
        sealed, replies = self._sealer.seal(req, await self.machines(), time.time())
        return settle(self._sealer.open_answer(await self.carrier_impl.call(sealed), replies))

    def stream(
        self, tool: str, args: dict[str, Any], *, machine: str | None = None, deadline: float | None = None, out: type[T] | None = None
    ) -> AsyncRun[Any]:
        """Runs any tool by name as a streamed call, awaited."""
        req = request(tool, args, machine, deadline)
        if self._sealer is None:
            return AsyncRun(self.carrier_impl.stream(req), out.model_validate if out is not None else (lambda v: v))
        return AsyncRun(self._sealed_lines(req), out.model_validate if out is not None else (lambda v: v))

    async def _sealed_lines(self, req: Json) -> AsyncIterator[Json]:
        sealer = self._sealer
        assert sealer is not None
        sealed, replies = sealer.seal(req, await self.machines(), time.time())
        async for line in self.carrier_impl.stream(sealed):
            yield sealer.open_line(line, replies)

    async def close(self) -> None:
        await self.carrier_impl.close()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()


def connect_async(
    token: str | None = None,
    url: str | None = None,
    *,
    contour: str | None = None,
    carrier: str | AsyncCarrier | None = None,
    e2e: Sealing | None = None,
) -> AsyncClient:
    """`connect`, awaited: `async with cmdop.connect_async() as c: ...`."""
    if carrier is not None and not isinstance(carrier, str):
        return AsyncClient(carrier, e2e)
    carrier_name(carrier)
    return AsyncClient(AsyncHttpCarrier(url_of(url, contour), token_of(token)), e2e)
