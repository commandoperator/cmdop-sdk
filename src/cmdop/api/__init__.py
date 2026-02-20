"""
CMDOP SDK API Client.

Provides unified access to all CMDOP HTTP APIs.

Usage:
    >>> from cmdop.api import CMDOPAPI
    >>>
    >>> async with CMDOPAPI(api_key="cmd_xxx") as api:
    ...     machines = await api.machines.list()
    ...     workspaces = await api.workspaces.list()

For direct access to generated clients:
    >>> from cmdop.api import machines, workspaces, system
"""

from __future__ import annotations

# Main unified client
from cmdop.api.client import CMDOPAPI

# Configuration
from cmdop.api.config import get_base_url, BASE_URLS

# Services (high-level wrappers)
from cmdop.api.services import (
    MachinesService,
    WorkspacesService,
    SystemService,
)

# Re-export generated clients for direct access
from cmdop.api.generated import machines, workspaces, system

__all__ = [
    # Main client
    "CMDOPAPI",
    # Config
    "get_base_url",
    "BASE_URLS",
    # Services
    "MachinesService",
    "WorkspacesService",
    "SystemService",
    # Generated clients
    "machines",
    "workspaces",
    "system",
]
