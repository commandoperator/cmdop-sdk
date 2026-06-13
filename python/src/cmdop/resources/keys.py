"""keys namespace: list/issue/revoke (fleet api-keys). Fleet-scoped."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop._proto.cmdop.core.v1 import keys_pb2 as k_pb
from cmdop.resources.base import BaseResource

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from cmdop.types import ApiKeyList, IssueKeyResponse


class KeysResource(BaseResource):
    async def list(
        self, *, fleet_id: str | None = None, page: int = 1, per_page: int | None = None
    ) -> ApiKeyList:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            list_keys_req=k_pb.ListKeysRequest(fleet_id=fid, page=self._offset_page(page, per_page))
        )
        return (await self._unary(req)).api_key_list

    async def issue(
        self, name: str, *, expires_in_days: int | None = None, fleet_id: str | None = None
    ) -> IssueKeyResponse:
        """Mint a key. ``raw_token`` is returned only this once."""
        fid = self._fleet(fleet_id)
        req = pb.Envelope(
            issue_key_req=k_pb.IssueKeyRequest(
                fleet_id=fid, name=name, expires_in_days=expires_in_days or 0
            )
        )
        return (await self._unary(req)).issue_key_resp

    async def revoke(self, key_id: str, *, fleet_id: str | None = None) -> None:
        fid = self._fleet(fleet_id)
        req = pb.Envelope(revoke_key_req=k_pb.RevokeKeyRequest(fleet_id=fid, key_id=str(key_id)))
        await self._unary(req)

    # -- pagination --------------------------------------------------------

    async def iter(
        self, *, fleet_id: str | None = None, per_page: int | None = None
    ) -> AsyncIterator[Any]:
        async for page in self.pages(fleet_id=fleet_id, per_page=per_page):
            for item in page.items:
                yield item

    async def pages(
        self, *, fleet_id: str | None = None, per_page: int | None = None
    ) -> AsyncIterator[ApiKeyList]:
        async def fetch(page_number: int) -> ApiKeyList:
            return await self.list(fleet_id=fleet_id, page=page_number, per_page=per_page)

        async for page in self._paginate_offset(fetch):
            yield page
