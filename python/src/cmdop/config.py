"""Immutable configuration for the local ``cmdop-core`` process."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_TIMEOUT_MS = 30_000


@dataclass(frozen=True)
class ClientConfig:
    """Resolved client configuration.

    ``Client()`` intentionally needs no arguments for the local relay. The Go
    core owns local config and credential discovery. An explicit remote
    ``base_url`` still requires a valid relay token; the core enforces that
    boundary fail-closed.
    """

    token: str | None = None
    base_url: str | None = None
    timeout_ms: int = DEFAULT_TIMEOUT_MS

    @classmethod
    def resolve(
        cls,
        *,
        token: str | None = None,
        base_url: str | None = None,
        timeout_ms: int | None = None,
    ) -> ClientConfig:
        resolved_timeout = timeout_ms
        if resolved_timeout is None:
            value = os.environ.get("CMDOP_TIMEOUT_MS")
            resolved_timeout = int(value) if value else DEFAULT_TIMEOUT_MS
        if resolved_timeout <= 0:
            raise ValueError("timeout_ms must be greater than zero")
        resolved_base = base_url or os.environ.get("CMDOP_BASE_URL") or None
        return cls(
            token=token or os.environ.get("CMDOP_TOKEN") or None,
            base_url=resolved_base.rstrip("/") if resolved_base else None,
            timeout_ms=resolved_timeout,
        )
