"""The carrier vectors (`exports/sdk/vectors/carrier.json`, written from Rust) and how a client runs one: shared by
the conformance suite and `make sdk-live`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cmdop

VECTORS: list[dict[str, Any]] = json.loads((Path(__file__).parents[2] / "vectors" / "carrier.json").read_text())["vectors"]


def run_vector(v: dict[str, Any], c: cmdop.Client, machine: str | None = None) -> tuple[str, list[dict[str, str]], Any]:
    """Sends the vector's call through `c` and says what the caller saw: outcome, pieces, result."""
    call = v["call"]
    args: dict[str, Any] = dict(call.get("args") or {})
    if v.get("pad_command_to") is not None:
        args["command"] = f"{args['command']} #".ljust(v["pad_command_to"], "x")
    deadline = call["deadline_ms"] / 1000 if call.get("deadline_ms") is not None else None
    pieces: list[dict[str, str]] = []
    try:
        if not v["stream"]:
            return "ok", pieces, c.call(call["tool"], args, machine=machine, deadline=deadline)
        r = c.stream(call["tool"], args, machine=machine, deadline=deadline)
        for p in r:
            pieces.append({"stream": p.stream, "data": p.data})
            if v.get("cancel_after_pieces") is not None and len(pieces) >= v["cancel_after_pieces"]:
                break
        return "ok", pieces, r.result
    except cmdop.CmdopError as e:
        return e.code, pieces, None
    except cmdop.CarrierError:
        return "carrier_error", pieces, None


def differences(v: dict[str, Any], seen: tuple[str, list[dict[str, str]], Any]) -> list[str]:
    """How what the caller saw differs from the vector's `expect`; empty when it matches."""
    outcome, pieces, result = seen
    expect = v["expect"]
    out: list[str] = []
    if outcome != expect["outcome"]:
        out.append(f"outcome {outcome}, want {expect['outcome']}")
    if pieces != expect.get("pieces", []):
        out.append(f"pieces {pieces}, want {expect.get('pieces', [])}")
    want: dict[str, Any] = expect.get("result") or {}
    for k, value in want.items():
        got = result.get(k) if isinstance(result, dict) else None  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if got != value:
            out.append(f"result.{k} {got!r}, want {value!r}")
    return out
