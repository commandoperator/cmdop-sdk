"""
CMDOP API Services.

High-level service wrappers for generated API clients.
"""

from __future__ import annotations

from cmdop.api.services.machines import MachinesService
from cmdop.api.services.workspaces import WorkspacesService
from cmdop.api.services.system import SystemService

__all__ = [
    "MachinesService",
    "WorkspacesService",
    "SystemService",
]
