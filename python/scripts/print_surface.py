#!/usr/bin/env python3
"""Print the actual v2 Python resource surface as JSON-only stdout."""

from __future__ import annotations

import inspect
import json
import sys

from cmdop.resources.machines import MachinesResource
from cmdop.resources.system import SystemResource


def _methods(cls: type) -> list[str]:
    return sorted(
        name
        for name, member in vars(cls).items()
        if not name.startswith("_") and inspect.isfunction(member)
    )


def main() -> int:
    sys.stdout.write(
        json.dumps(
            {
                "system": _methods(SystemResource),
                "machines": _methods(MachinesResource),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
