"""The client-door seam (developer SDK plan, section 4), the same as the TypeScript one.

The client speaks the call contract (`cmdop.generated.call`) and nothing else; an adapter moves the contract's shapes
over one channel. A carrier defines no semantics: codes, deadlines, cancel and the order of pieces come from the
contract. Requests and lines are plain JSON values (dicts), exactly as the contract's schemas describe them.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, Protocol

Json = dict[str, Any]


class Carrier(Protocol):
    name: str

    def call(self, req: Json) -> Json:
        """One call, answered once. A refusal is an answer with `error`, never an exception."""
        ...

    def stream(self, req: Json) -> Iterator[Json]:
        """One call: its pieces as they come, its answer as the last line. Closing the iterator cancels the call."""
        ...

    def machines(self) -> Json:
        """The contour's machines, a server-answered operation: `ok` is a list of rows."""
        ...

    def close(self) -> None: ...


class AsyncCarrier(Protocol):
    name: str

    async def call(self, req: Json) -> Json: ...

    def stream(self, req: Json) -> AsyncIterator[Json]: ...

    async def machines(self) -> Json: ...

    async def close(self) -> None: ...


def is_answer(line: Json) -> bool:
    return "ok" in line or "error" in line or "sealed" in line
