from __future__ import annotations

import httpx

from .models import *


class SyncSystemOauthAPI:
    """Synchronous API endpoints for Oauth."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def system_oauth_authorize_create(self, data: DeviceAuthorizeRequest) -> DeviceAuthorizeResponse:
        """
        Authorize device

        User approves or denies device code in browser (requires
        authentication).
        """
        url = "/api/system/oauth/authorize/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return DeviceAuthorizeResponse.model_validate(response.json())


    def system_oauth_device_create(self, data: DeviceCodeRequestRequest) -> DeviceCodeResponse:
        """
        Request device code

        CLI initiates OAuth flow by requesting a device code and user code.
        """
        url = "/api/system/oauth/device/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return DeviceCodeResponse.model_validate(response.json())


    def system_oauth_revoke_create(self, data: TokenRevokeRequest) -> None:
        """
        Revoke token

        Revoke access token or refresh token.
        """
        url = "/api/system/oauth/revoke/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)


    def system_oauth_token_create(self, data: TokenRequestRequest) -> TokenResponse:
        """
        Request access token

        CLI polls for token (device flow) or refreshes expired token.
        """
        url = "/api/system/oauth/token/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return TokenResponse.model_validate(response.json())


    def system_oauth_token_info_retrieve(self) -> TokenInfo:
        """
        Get token info

        Get information about current access token (requires authentication).
        """
        url = "/api/system/oauth/token/info/"
        response = self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return TokenInfo.model_validate(response.json())


    def system_oauth_tokens_list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedTokenListList]:
        """
        List user tokens

        List all CLI tokens for authenticated user.
        """
        url = "/api/system/oauth/tokens/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            raise httpx.HTTPStatusError(f"{response.status_code}: {error_body}", request=response.request, response=response)
        return PaginatedTokenListList.model_validate(response.json())


