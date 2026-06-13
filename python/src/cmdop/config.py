"""Client configuration + env-var resolution.

Precedence for every field: explicit arg > env var > default. The resolved
credentials + base URLs are passed to the spawned ``cmdop-core`` process via env
(never a port — report 07 §B.3):

* relay plane — ``CMDOP_TOKEN`` / ``CMDOP_BASE_URL`` (machines, fleets, …);
* Django platform plane — ``CMDOP_API_KEY`` / ``CMDOP_API_BASE_URL`` (skills).

The two credentials are SEPARATE (a skills call needs the UserAPIKey, a machine
call needs the relay token); they must not be conflated.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://cloud.cmdop.com"
DEFAULT_API_BASE_URL = "https://api.cmdop.com"
DEFAULT_TIMEOUT_MS = 30_000


@dataclass(frozen=True)
class ClientConfig:
    """Resolved, immutable per-client configuration."""

    token: str
    base_url: str = DEFAULT_BASE_URL
    fleet_id: str | None = None
    timeout_ms: int = DEFAULT_TIMEOUT_MS
    api_key: str | None = None
    api_base_url: str = DEFAULT_API_BASE_URL

    @classmethod
    def resolve(
        cls,
        *,
        token: str | None = None,
        base_url: str | None = None,
        fleet_id: str | None = None,
        timeout_ms: int | None = None,
        api_key: str | None = None,
        api_base_url: str | None = None,
    ) -> ClientConfig:
        """Build a config, applying explicit > env > default precedence.

        Relay token sources: ``CMDOP_TOKEN`` then ``CMDOP_API_KEY`` (token wins
        if both) — keeps single-credential setups working. The skills plane
        reads ``api_key`` from ``CMDOP_API_KEY`` independently.
        """
        token = token or os.environ.get("CMDOP_TOKEN") or os.environ.get("CMDOP_API_KEY")
        if not token:
            raise ValueError(
                "No token. Pass token= or set CMDOP_TOKEN (or CMDOP_API_KEY)."
            )

        resolved_base = base_url or os.environ.get("CMDOP_BASE_URL") or DEFAULT_BASE_URL

        resolved_fleet = fleet_id or os.environ.get("CMDOP_FLEET_ID") or None

        if timeout_ms is not None:
            resolved_timeout = timeout_ms
        else:
            env_timeout = os.environ.get("CMDOP_TIMEOUT_MS")
            resolved_timeout = int(env_timeout) if env_timeout else DEFAULT_TIMEOUT_MS

        resolved_api_key = api_key or os.environ.get("CMDOP_API_KEY") or None

        resolved_api_base = (
            api_base_url or os.environ.get("CMDOP_API_BASE_URL") or DEFAULT_API_BASE_URL
        )

        return cls(
            token=token,
            base_url=resolved_base.rstrip("/"),
            fleet_id=resolved_fleet,
            timeout_ms=resolved_timeout,
            api_key=resolved_api_key,
            api_base_url=resolved_api_base.rstrip("/"),
        )
