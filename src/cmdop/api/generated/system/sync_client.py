from __future__ import annotations

from typing import Any

import httpx

from .helpers import APILogger, LoggerConfig
from .system__api__oauth.sync_client import SyncSystemOauthAPI
from .system__api__system.sync_client import SyncSystemSystemAPI


class SyncAPIClient:
    """
    Synchronous API client for Cmdop API.

    Usage:
        >>> with SyncAPIClient(base_url='https://api.example.com') as client:
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

        # Initialize logger
        self.logger: APILogger | None = None
        if logger_config is not None:
            self.logger = APILogger(logger_config)

        # Initialize sub-clients
        self.system_oauth = SyncSystemOauthAPI(self._client)
        self.system_system = SyncSystemSystemAPI(self._client)

    def __enter__(self) -> SyncAPIClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.close()

    def close(self) -> None:
        """Close HTTP client."""
        self._client.close()