from __future__ import annotations

from typing import Any

import httpx

from .helpers import APILogger, LoggerConfig
from .machines__api__machine_sharing.sync_client import SyncMachinesMachineSharingAPI
from .machines__api__machines.sync_client import SyncMachinesMachinesAPI


class SyncAPIClient:
    """
    Synchronous API client for Cmdop API.

    Usage:
        >>> with SyncAPIClient(base_url='https://api.example.com') as client:
        ...     client.set_token('your-jwt-token')
        ...     users = client.users.list()
        ...     post = client.posts.create(data=new_post)
    """

    def __init__(
        self,
        base_url: str,
        logger_config: LoggerConfig | None = None,
        **kwargs: Any,
    ):
        """
        Initialize sync API client.

        Args:
            base_url: Base API URL (e.g., 'https://api.example.com')
            logger_config: Logger configuration (None to disable logging)
            **kwargs: Additional httpx.Client kwargs
        """
        self.base_url = base_url.rstrip('/')
        self._client = httpx.Client(
            base_url=self.base_url,
            **kwargs,
        )
        self._token: str | None = None

        # Initialize logger
        self.logger: APILogger | None = None
        if logger_config is not None:
            self.logger = APILogger(logger_config)

        # Initialize sub-clients
        self.machines_machine_sharing = SyncMachinesMachineSharingAPI(self._client)
        self.machines_machines = SyncMachinesMachinesAPI(self._client)

    def set_token(self, token: str) -> None:
        """
        Set JWT authentication token.

        Args:
            token: JWT access token
        """
        self._token = token
        self._client.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self) -> None:
        """Clear authentication token."""
        self._token = None
        self._client.headers.pop("Authorization", None)

    def is_authenticated(self) -> bool:
        """Check if token is set."""
        return self._token is not None

    def __enter__(self) -> SyncAPIClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.close()

    def close(self) -> None:
        """Close HTTP client."""
        self._client.close()