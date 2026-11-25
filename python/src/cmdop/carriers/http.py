"""HTTP + NDJSON, the first carrier: `POST /api/v1/call`, `POST /api/v1/call/stream` (one JSON value per line, the
answer last) and `GET /api/v1/machines` on the contour's address. Every answer of these routes is shaped like the
contract's `Answer`, refusals included. Cancel is closing the response: the server tells the machine. `gen.ts` checks
these paths against `openapi.json`.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterator
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import httpx

from .._errors import CarrierError
from ._carrier import Json, is_answer

# Room for the server to answer after the call's own time ran out, and the longest tool time (exec_run, 620 s).
SLACK_SECS = 10.0
LONGEST_SECS = 620.0


def _client() -> str:
    """Which SDK and version make the calls, as `python/<version>`. The server keeps `python` and a semver only,
    never this text. A copy that is not installed as a package says `python`."""
    try:
        return f"python/{version('cmdop')}"
    except PackageNotFoundError:
        return "python"


CLIENT = _client()


def _headers(token: str) -> dict[str, str]:
    # The server takes writes under /api only with `x-cmdop` (a browser form cannot send it).
    return {
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "x-cmdop": "1",
        "x-cmdop-client": CLIENT,
    }


def _timeout(req: Json) -> httpx.Timeout:
    ms = req.get("deadline_ms")
    wait = (ms / 1000 if isinstance(ms, (int, float)) else LONGEST_SECS) + SLACK_SECS
    return httpx.Timeout(wait, connect=10.0)


def _answer(res: httpx.Response) -> Json:
    try:
        body: Any = res.json()
    except ValueError:
        raise CarrierError("http", f"server answered {res.status_code} without JSON") from None
    if not isinstance(body, dict) or not is_answer(body):  # pyright: ignore[reportUnknownArgumentType]
        raise CarrierError("http", f"server answered {res.status_code} without a call answer")
    return body  # pyright: ignore[reportUnknownVariableType]


def _rows(res: httpx.Response) -> Json:
    try:
        body: Any = res.json()
    except ValueError:
        raise CarrierError("http", f"server answered {res.status_code} without JSON for the machine list") from None
    if isinstance(body, dict) and is_answer(body):  # pyright: ignore[reportUnknownArgumentType]
        return body  # pyright: ignore[reportUnknownVariableType]
    ok = res.is_success and isinstance(body, list)
    if not ok or not all(isinstance(r, dict) and isinstance(r.get("id"), str) and isinstance(r.get("name"), str) and isinstance(r.get("online"), bool) for r in body):  # pyright: ignore
        raise CarrierError("http", f"server answered {res.status_code} without a machine list")
    return {"ok": body}


def _line(text: str) -> Json | None:
    text = text.strip()
    if not text:
        return None
    v: Any = json.loads(text)
    if not isinstance(v, dict):
        raise CarrierError("http", "a stream line is not an object")
    return v  # pyright: ignore[reportUnknownVariableType]


class HttpCarrier:
    name = "http"

    def __init__(self, url: str, token: str, transport: httpx.BaseTransport | None = None) -> None:
        self._http = httpx.Client(base_url=url.rstrip("/"), headers=_headers(token), transport=transport)

    def call(self, req: Json) -> Json:
        try:
            return _answer(self._http.post("/api/v1/call", json=req, timeout=_timeout(req)))
        except httpx.TransportError as e:
            raise CarrierError("http", f"could not reach the door: {e}") from e

    def stream(self, req: Json) -> Iterator[Json]:
        try:
            with self._http.stream("POST", "/api/v1/call/stream", json=req, timeout=_timeout(req)) as res:
                if not res.is_success:
                    res.read()
                    yield _answer(res)
                    return
                for text in res.iter_lines():
                    line = _line(text)
                    if line is not None:
                        yield line
        except httpx.TransportError as e:
            raise CarrierError("http", f"the stream broke: {e}") from e

    def machines(self) -> Json:
        try:
            return _rows(self._http.get("/api/v1/machines"))
        except httpx.TransportError as e:
            raise CarrierError("http", f"could not reach the door: {e}") from e

    def close(self) -> None:
        self._http.close()


class AsyncHttpCarrier:
    name = "http"

    def __init__(self, url: str, token: str, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._http = httpx.AsyncClient(base_url=url.rstrip("/"), headers=_headers(token), transport=transport)

    async def call(self, req: Json) -> Json:
        try:
            return _answer(await self._http.post("/api/v1/call", json=req, timeout=_timeout(req)))
        except httpx.TransportError as e:
            raise CarrierError("http", f"could not reach the door: {e}") from e

    async def stream(self, req: Json) -> AsyncIterator[Json]:
        try:
            async with self._http.stream("POST", "/api/v1/call/stream", json=req, timeout=_timeout(req)) as res:
                if not res.is_success:
                    await res.aread()
                    yield _answer(res)
                    return
                async for text in res.aiter_lines():
                    line = _line(text)
                    if line is not None:
                        yield line
        except httpx.TransportError as e:
            raise CarrierError("http", f"the stream broke: {e}") from e

    async def machines(self) -> Json:
        try:
            return _rows(await self._http.get("/api/v1/machines"))
        except httpx.TransportError as e:
            raise CarrierError("http", f"could not reach the door: {e}") from e

    async def close(self) -> None:
        await self._http.aclose()
