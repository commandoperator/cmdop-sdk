"""Typed resource namespaces driving the cmdop-core stdio transport."""

from __future__ import annotations

from cmdop.resources.fleets import FleetsResource
from cmdop.resources.keys import KeysResource
from cmdop.resources.machines import MachinesResource
from cmdop.resources.schedules import SchedulesResource
from cmdop.resources.tunnels import TunnelsResource

__all__ = [
    "FleetsResource",
    "KeysResource",
    "MachinesResource",
    "SchedulesResource",
    "TunnelsResource",
]
