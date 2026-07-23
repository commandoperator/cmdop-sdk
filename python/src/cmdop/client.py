"""Public asynchronous Cmdop SDK client."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from cmdop._locate import locate_binary
from cmdop._transport import Transport
from cmdop.config import ClientConfig
from cmdop.resources.machines import MachinesResource
from cmdop.resources.system import SystemResource


class Client:
    """Thin client backed by one lazily started ``cmdop-core`` process."""

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str | None = None,
        timeout_ms: int | None = None,
        binary_path: str | None = None,
    ) -> None:
        self._cfg = ClientConfig.resolve(
            token=token, base_url=base_url, timeout_ms=timeout_ms
        )
        self._t = Transport(self._cfg, binary_path or locate_binary())

    @classmethod
    def from_env(cls) -> Client:
        return cls()

    @property
    def config(self) -> ClientConfig:
        return self._cfg

    @property
    def base_url(self) -> str | None:
        return self._cfg.base_url

    @cached_property
    def system(self) -> SystemResource:
        return SystemResource(self)

    @cached_property
    def machines(self) -> MachinesResource:
        return MachinesResource(self)

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._t.aclose()
