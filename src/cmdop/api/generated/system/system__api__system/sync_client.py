from __future__ import annotations

import httpx

from .models import (
    Alert,
    AlertCreate,
    AlertCreateRequest,
    AlertRequest,
    ApiKey,
    ApiKeyCreateRequest,
    ApiKeyResponse,
    PaginatedAlertList,
    PaginatedApiKeyList,
    PatchedAlertRequest,
)


class SyncSystemSystemAPI:
    """Synchronous API endpoints for System."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def alerts_list(
        self,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        read: bool | None = None,
        search: str | None = None,
        type: str | None = None,
        workspace: str | None = None,
    ) -> list[PaginatedAlertList]:
        """
        List alerts with filters.
        """
        url = "/api/system/alerts/"
        _params = {
            k: v for k, v in {
                "ordering": ordering,
                "page": page,
                "page_size": page_size,
                "read": read,
                "search": search,
                "type": type,
                "workspace": workspace,
            }.items() if v is not None
        }
        response = self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return PaginatedAlertList.model_validate(response.json())


    def alerts_create(self, data: AlertCreateRequest) -> AlertCreate:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = "/api/system/alerts/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return AlertCreate.model_validate(response.json())


    def alerts_retrieve(self, id: str) -> Alert:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = f"/api/system/alerts/{id}/"
        response = self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return Alert.model_validate(response.json())


    def alerts_update(self, id: str, data: AlertRequest) -> Alert:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = f"/api/system/alerts/{id}/"
        response = self._client.put(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return Alert.model_validate(response.json())


    def alerts_partial_update(
        self,
        id: str,
        data: PatchedAlertRequest | None = None,
    ) -> Alert:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = f"/api/system/alerts/{id}/"
        _json = data.model_dump(mode="json", exclude_unset=True, exclude_none=True) if data else None
        response = self._client.patch(url, json=_json)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return Alert.model_validate(response.json())


    def alerts_destroy(self, id: str) -> None:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = f"/api/system/alerts/{id}/"
        response = self._client.delete(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )


    def alerts_mark_as_read_create(self, id: str) -> Alert:
        """
        Mark alert as read
        """
        url = f"/api/system/alerts/{id}/mark-as-read/"
        response = self._client.post(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return Alert.model_validate(response.json())


    def alerts_mark_all_as_read_create(self) -> None:
        """
        Mark all unread alerts as read for current workspace
        """
        url = "/api/system/alerts/mark-all-as-read/"
        response = self._client.post(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )


    def api_keys_list(
        self,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        search: str | None = None,
        workspace: str | None = None,
    ) -> list[PaginatedApiKeyList]:
        """
        List API keys with filters.
        """
        url = "/api/system/api-keys/"
        _params = {
            k: v for k, v in {
                "ordering": ordering,
                "page": page,
                "page_size": page_size,
                "search": search,
                "workspace": workspace,
            }.items() if v is not None
        }
        response = self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return PaginatedApiKeyList.model_validate(response.json())


    def api_keys_create(self, data: ApiKeyCreateRequest) -> ApiKeyResponse:
        """
        Create new API key (raw key shown only once).
        """
        url = "/api/system/api-keys/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ApiKeyResponse.model_validate(response.json())


    def api_keys_retrieve(self, id: str) -> ApiKey:
        """
        ViewSet for ApiKey operations. Manage API keys for workspace
        integrations. Note: Raw key is only shown once during creation.
        """
        url = f"/api/system/api-keys/{id}/"
        response = self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ApiKey.model_validate(response.json())


    def api_keys_update(self, id: str) -> ApiKey:
        """
        ViewSet for ApiKey operations. Manage API keys for workspace
        integrations. Note: Raw key is only shown once during creation.
        """
        url = f"/api/system/api-keys/{id}/"
        response = self._client.put(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ApiKey.model_validate(response.json())


    def api_keys_partial_update(self, id: str) -> ApiKey:
        """
        ViewSet for ApiKey operations. Manage API keys for workspace
        integrations. Note: Raw key is only shown once during creation.
        """
        url = f"/api/system/api-keys/{id}/"
        response = self._client.patch(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ApiKey.model_validate(response.json())


    def api_keys_destroy(self, id: str) -> None:
        """
        ViewSet for ApiKey operations. Manage API keys for workspace
        integrations. Note: Raw key is only shown once during creation.
        """
        url = f"/api/system/api-keys/{id}/"
        response = self._client.delete(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )


    def api_keys_regenerate_create(self, id: str) -> ApiKeyResponse:
        """
        Regenerate API key (deletes old key and creates new one)
        """
        url = f"/api/system/api-keys/{id}/regenerate/"
        response = self._client.post(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ApiKeyResponse.model_validate(response.json())


