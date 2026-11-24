"""The in-memory carrier: the contract with no channel, for tests and the conformance suite. `serve` plays the door:
it gets each request and yields what the door would (pieces, then the answer)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator

from .._errors import CarrierError
from ._carrier import Json, is_answer

Serve = Callable[[Json], Iterator[Json]]


class MemoryCarrier:
    name = "memory"

    def __init__(self, serve: Serve, machines: list[Json] | None = None) -> None:
        self._serve = serve
        self._machines = machines or []

    def call(self, req: Json) -> Json:
        last = None
        for line in self.stream(req):
            if is_answer(line):
                last = line
        if last is None:
            raise CarrierError("memory", "the door gave no answer")
        return last

    def stream(self, req: Json) -> Iterator[Json]:
        try:
            yield from self._serve(req)
        except GeneratorExit:
            raise
        except Exception as e:
            raise CarrierError("memory", f"the door broke: {e}") from e

    def machines(self) -> Json:
        return {"ok": self._machines}

    def close(self) -> None:
        pass


class AsyncMemoryCarrier:
    """The same door, awaited."""

    name = "memory"

    def __init__(self, serve: Serve, machines: list[Json] | None = None) -> None:
        self._sync = MemoryCarrier(serve, machines)

    async def call(self, req: Json) -> Json:
        return self._sync.call(req)

    async def stream(self, req: Json) -> AsyncIterator[Json]:
        for line in self._sync.stream(req):
            yield line

    async def machines(self) -> Json:
        return self._sync.machines()

    async def close(self) -> None:
        pass
