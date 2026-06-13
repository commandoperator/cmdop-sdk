"""Public async :class:`Client` with lazy resource accessors.

Spawns one persistent ``cmdop-core`` subprocess (on first call) and speaks
protobuf over its stdio. Use as an async context manager so the child is reaped::

    async with Client(token="...") as c:
        page = await c.machines.list(presence="online")
        text = await c.machines.ask(mid, "uptime").collect()
"""

from __future__ import annotations

from functools import cached_property
from typing import Any

from cmdop._locate import locate_binary
from cmdop._transport import Transport
from cmdop.config import ClientConfig
from cmdop.resources.fleets import FleetsResource
from cmdop.resources.keys import KeysResource
from cmdop.resources.machines import MachinesResource
from cmdop.resources.schedules import SchedulesResource
from cmdop.resources.skills import SkillsResource
from cmdop.resources.tunnels import TunnelsResource


class Client:
    """Async client backed by the baked-in ``cmdop-core`` Go binary."""

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str | None = None,
        fleet_id: str | None = None,
        timeout_ms: int | None = None,
        binary_path: str | None = None,
        api_key: str | None = None,
        api_base_url: str | None = None,
    ) -> None:
        self._cfg = ClientConfig.resolve(
            token=token,
            base_url=base_url,
            fleet_id=fleet_id,
            timeout_ms=timeout_ms,
            api_key=api_key,
            api_base_url=api_base_url,
        )
        self._t = Transport(self._cfg, binary_path or locate_binary())

    @classmethod
    def from_env(cls) -> Client:
        """Build a client from the ``CMDOP_*`` environment variables."""
        return cls()

    @property
    def config(self) -> ClientConfig:
        return self._cfg

    @property
    def fleet_id(self) -> str | None:
        return self._cfg.fleet_id

    @property
    def base_url(self) -> str:
        return self._cfg.base_url

    # -- lazy resource accessors ------------------------------------------

    @cached_property
    def machines(self) -> MachinesResource:
        return MachinesResource(self)

    @cached_property
    def fleets(self) -> FleetsResource:
        return FleetsResource(self)

    @cached_property
    def tunnels(self) -> TunnelsResource:
        return TunnelsResource(self)

    @cached_property
    def schedules(self) -> SchedulesResource:
        return SchedulesResource(self)

    @cached_property
    def keys(self) -> KeysResource:
        return KeysResource(self)

    @cached_property
    def skills(self) -> SkillsResource:
        return SkillsResource(self)

    # -- lifecycle ---------------------------------------------------------

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close stdin (graceful drain) and reap the core process."""
        await self._t.aclose()
