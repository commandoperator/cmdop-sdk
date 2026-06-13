#!/usr/bin/env python3
"""Print the Python SDK's actual public surface as JSON to stdout.

Consumed by the top-level cross-language parity orchestrator
(``parity/check.py``) and runnable directly (``uv run python
scripts/print_surface.py``) so it uses the project's pinned protobuf runtime.
Keep stdout JSON-only. Pagination helpers are excluded — they are ergonomic
extras, not part of the wire surface the manifest locks.
"""

from __future__ import annotations

import inspect
import json
import sys

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

_PAGINATION_HELPERS = {"iter", "pages", "iter_runs", "pages_runs"}


def _methods(cls: type) -> list[str]:
    return sorted(
        name
        for name, member in vars(cls).items()
        if not name.startswith("_")
        and name not in _PAGINATION_HELPERS
        and inspect.isfunction(member)
    )


def main() -> int:
    surface = {
        "machines": _methods(MachinesResource),
        "fleets": _methods(FleetsResource),
        "fleets.members": _methods(FleetMembersResource),
        "fleets.machines": _methods(FleetMachinesResource),
        "tunnels": _methods(TunnelsResource),
        "schedules": _methods(SchedulesResource),
        "keys": _methods(KeysResource),
        "skills": _methods(SkillsResource),
    }
    sys.stdout.write(json.dumps(surface))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
