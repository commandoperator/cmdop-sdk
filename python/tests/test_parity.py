"""Cross-language parity gate (Python half, Phase 5 §5.3).

Introspects the Python SDK's actual resource surface and asserts it equals the
checked-in ``parity/manifest.json``. The Node SDK runs the mirror test
(``sdk/node/tests/parity.test.ts``); ``parity/check.py`` runs both. Any namespace or
method that exists in one language but not the other — or drifts from the
manifest — fails CI.

Pagination helpers (``iter`` / ``pages`` / ``iter_runs`` / ``pages_runs``) are
ergonomic extras, not part of the wire surface the manifest locks, so they are
excluded here exactly as the Node ``_parity.ts`` excludes their camelCase forms.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from cmdop.resources.fleets import (
    FleetMachinesResource,
    FleetMembersResource,
    FleetsResource,
)
from cmdop.resources.keys import KeysResource
from cmdop.resources.machines import MachinesResource
from cmdop.resources.schedules import SchedulesResource
from cmdop.resources.skills import SkillsResource
from cmdop.resources.tunnels import TunnelsResource

_MANIFEST_PATH = Path(__file__).resolve().parents[3] / "core" / "parity" / "manifest.json"
_PAGINATION_HELPERS = {"iter", "pages", "iter_runs", "pages_runs"}


def _methods_of(cls: type) -> list[str]:
    """Public, non-pagination instance methods declared on ``cls`` itself."""
    out: list[str] = []
    for name, member in vars(cls).items():
        if name.startswith("_") or name in _PAGINATION_HELPERS:
            continue
        # Coroutine functions, plain methods, and the sync `ask`/`sessions`.
        if inspect.isfunction(member):
            out.append(name)
    return sorted(out)


def _actual_surface() -> dict[str, list[str]]:
    return {
        "machines": _methods_of(MachinesResource),
        "fleets": _methods_of(FleetsResource),
        "fleets.members": _methods_of(FleetMembersResource),
        "fleets.machines": _methods_of(FleetMachinesResource),
        "tunnels": _methods_of(TunnelsResource),
        "schedules": _methods_of(SchedulesResource),
        "keys": _methods_of(KeysResource),
        "skills": _methods_of(SkillsResource),
    }


_MANIFEST: dict[str, list[str]] = json.loads(_MANIFEST_PATH.read_text())["namespaces"]
_SURFACE = _actual_surface()


def test_namespaces_match_manifest() -> None:
    assert sorted(_SURFACE) == sorted(_MANIFEST)


@pytest.mark.parametrize("namespace", list(_MANIFEST))
def test_namespace_methods_match_manifest(namespace: str) -> None:
    assert _SURFACE[namespace] == sorted(_MANIFEST[namespace])
