from __future__ import annotations

import inspect
import json
from pathlib import Path

from cmdop.resources.machines import MachinesResource
from cmdop.resources.system import SystemResource

_MATRIX = Path(__file__).resolve().parents[2] / "core" / "parity" / "capabilities.v2.json"


def _expected() -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for capability in json.loads(_MATRIX.read_text())["capabilities"]:
        if capability["status"] == "shipped":
            namespace, method = capability["id"].split(".")
            result.setdefault(namespace, []).append(method)
    return {namespace: sorted(methods) for namespace, methods in result.items()}


def _methods(resource: type) -> list[str]:
    return sorted(
        name
        for name, member in vars(resource).items()
        if not name.startswith("_") and inspect.isfunction(member)
    )


def test_surface_matches_shipped_capabilities() -> None:
    assert {"system": _methods(SystemResource), "machines": _methods(MachinesResource)} == _expected()
