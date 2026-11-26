"""The carrier conformance suite (developer SDK S3b): every vector of `exports/sdk/vectors/carrier.json`, written
from Rust, against every carrier of this package."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx
import pytest

import cmdop
from cmdop.carriers import Carrier, HttpCarrier, Json, MemoryCarrier

from vectors import VECTORS, differences, run_vector

def is_answer(line: Json) -> bool:
    return "ok" in line or "error" in line or "sealed" in line


def memory(v: dict[str, Any]) -> Carrier:
    def serve(_req: Json) -> Iterator[Json]:
        yield from v["door"]
        if not any(is_answer(line) for line in v["door"]):
            raise ConnectionError("connection dropped")

    return MemoryCarrier(serve)


def http(v: dict[str, Any]) -> Carrier:
    door: list[Json] = v["door"]
    answer = next((line for line in door if is_answer(line)), None)

    def body() -> Iterator[bytes]:
        for line in door:
            yield (json.dumps(line) + "\n").encode()
        if answer is None:
            raise httpx.ReadError("connection dropped")

    def handler(r: httpx.Request) -> httpx.Response:
        if not r.url.path.endswith("/call/stream"):
            if answer is None:
                return httpx.Response(502, text="")
            return httpx.Response(200 if "ok" in answer else 400, json=answer)
        return httpx.Response(200, content=body(), headers={"content-type": "application/x-ndjson"})

    return HttpCarrier("https://door.test", "cmdop_test", transport=httpx.MockTransport(handler))


@pytest.mark.parametrize("make", [memory, http], ids=["memory", "http"])
@pytest.mark.parametrize("v", VECTORS, ids=[v["name"] for v in VECTORS])
def test_vector(v: dict[str, Any], make: Any) -> None:
    assert differences(v, run_vector(v, cmdop.connect(carrier=make(v)))) == []
