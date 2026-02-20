"""
System service for CMDOP API.

Provides high-level interface for system operations (OAuth, API keys, alerts).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cmdop.api.generated.system import API as SystemAPI


class SystemService:
    """
    High-level system service.

    Wraps the generated system API with convenient methods.

    Example:
        >>> async with CMDOPAPI(api_key="cmd_xxx") as api:
        ...     # OAuth operations
        ...     tokens = await api.system.exchange_code(code="...")
    """

    def __init__(self, api: SystemAPI) -> None:
        """
        Initialize system service.

        Args:
            api: Generated system API client
        """
        self._api = api
        self._oauth = api.system_oauth
        self._system = api.system_system

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str | None = None,
    ) -> dict[str, Any]:
        """
        Exchange authorization code for tokens.

        Args:
            code: Authorization code
            redirect_uri: Redirect URI used in authorization

        Returns:
            Token response with access_token, refresh_token, etc.
        """
        from cmdop.api.generated.system.system__api__oauth.models import (
            TokenExchangeRequest,
        )

        data = TokenExchangeRequest(
            code=code,
            redirect_uri=redirect_uri or "",
        )
        response = await self._oauth.oauth_token_exchange_create(data=data)
        return response

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Refresh access token.

        Args:
            refresh_token: Refresh token

        Returns:
            New token response
        """
        from cmdop.api.generated.system.system__api__oauth.models import (
            TokenRefreshRequest,
        )

        data = TokenRefreshRequest(refresh_token=refresh_token)
        response = await self._oauth.oauth_token_refresh_create(data=data)
        return response

    async def get_user_info(self) -> dict[str, Any]:
        """
        Get current user info.

        Returns:
            User information
        """
        return await self._oauth.oauth_userinfo_retrieve()

    async def health_check(self) -> dict[str, Any]:
        """
        Check API health status.

        Returns:
            Health status
        """
        return await self._system.system_health_retrieve()
