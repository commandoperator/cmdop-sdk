"""The seam for end-to-end calls: `connect(e2e=...)` takes any object with these methods. The client sends what it is
given and hands back what comes for it to open; it holds no key and never reads the sealed text itself."""

from __future__ import annotations

from typing import Any, Protocol

from .carriers import Json


class Sealing(Protocol):
    def seal(self, req: Json, rows: list[Json], now: float) -> tuple[Json, Any]:
        """The request to send for one call (`rows`: the contour's machines), and how to open what comes back."""
        ...

    def open_answer(self, answer: Json, replies: Any) -> Json: ...

    def open_line(self, line: Json, replies: Any) -> Json: ...

    def public_key(self) -> str:
        """This client's public key, for `cmdop pair <key>` on each machine."""
        ...
