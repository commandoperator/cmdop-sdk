"""skills namespace: the marketplace surface (Django platform plane).

Skills live on Django (``UserAPIKey`` / ``X-Api-Key``), NOT the relay — the
spawned ``cmdop-core`` reaches them with ``CMDOP_API_KEY`` (passed through at
spawn), distinct from the relay ``CMDOP_TOKEN`` that drives machines/fleets.

Browse / install / publish / manage your own skills + the read-only taxonomy
(categories, tags). Mirrors the ``cmdop_skill`` Python framework's marketplace
operations, but baked into the Go core so any language gets them.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cmdop._proto.cmdop.core.v1 import envelope_pb2 as pb
from cmdop._proto.cmdop.core.v1 import skills_pb2 as s_pb
from cmdop.resources.base import BaseResource

if TYPE_CHECKING:
    from cmdop.types import (
        SkillCategoryList,
        SkillCreated,
        SkillDetail,
        SkillInstall,
        SkillListPage,
        SkillReviewPage,
        SkillsPublishResponse,
        SkillsPublishStatusResponse,
        SkillStar,
        SkillTagList,
        SkillUpdated,
        SkillVersionList,
    )


class SkillsResource(BaseResource):
    # -- browse / detail ---------------------------------------------------

    async def list(
        self,
        *,
        category: str | None = None,
        tag: str | None = None,
        search: str | None = None,
        lang: str | None = None,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> SkillListPage:
        """Browse the public marketplace (page-number paginated)."""
        req = pb.Envelope(
            skills_list_req=s_pb.SkillsListRequest(
                category=category,
                tag=tag,
                search=search,
                lang=lang,
                ordering=ordering,
                page=page,
                page_size=page_size,
            )
        )
        return (await self._unary(req)).skill_list_page

    async def get(self, slug: str, *, lang: str | None = None) -> SkillDetail:
        req = pb.Envelope(skills_get_req=s_pb.SkillsGetRequest(slug=slug, lang=lang))
        return (await self._unary(req)).skill_detail

    async def my(
        self,
        *,
        search: str | None = None,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> SkillListPage:
        """Your own skills (incl. private / draft)."""
        req = pb.Envelope(
            skills_my_req=s_pb.SkillsMyRequest(
                search=search, ordering=ordering, page=page, page_size=page_size
            )
        )
        return (await self._unary(req)).skill_list_page

    # -- install / star ----------------------------------------------------

    async def install(self, slug: str) -> SkillInstall:
        """Get the install payload (command, README, files, deps) for a skill."""
        req = pb.Envelope(skills_install_req=s_pb.SkillsInstallRequest(slug=slug))
        return (await self._unary(req)).skill_install

    async def star(self, slug: str) -> SkillStar:
        req = pb.Envelope(skills_star_req=s_pb.SkillsStarRequest(slug=slug))
        return (await self._unary(req)).skill_star

    # -- versions / reviews ------------------------------------------------

    async def versions(self, slug: str) -> SkillVersionList:
        req = pb.Envelope(skills_versions_req=s_pb.SkillsVersionsRequest(slug=slug))
        return (await self._unary(req)).skill_version_list

    async def reviews(
        self,
        slug: str,
        *,
        search: str | None = None,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> SkillReviewPage:
        req = pb.Envelope(
            skills_reviews_req=s_pb.SkillsReviewsRequest(
                slug=slug, search=search, ordering=ordering, page=page, page_size=page_size
            )
        )
        return (await self._unary(req)).skill_review_page

    # -- create / update / delete ------------------------------------------

    async def create(self, name: str) -> SkillCreated:
        """Reserve a new skill by name (server fills the rest on publish)."""
        req = pb.Envelope(skills_create_req=s_pb.SkillsCreateRequest(name=name))
        return (await self._unary(req)).skill_created

    async def update(
        self,
        slug: str,
        *,
        name: str | None = None,
        category: str | None = None,
        visibility: str | None = None,
        status: str | None = None,
        icon: str | None = None,
        cover: str | None = None,
        repository_url: str | None = None,
    ) -> SkillUpdated:
        """Partial-update a skill you own. ``category`` is a category slug."""
        req = pb.Envelope(
            skills_update_req=s_pb.SkillsUpdateRequest(
                slug=slug,
                name=name,
                category=category,
                visibility=visibility,
                status=status,
                icon=icon,
                cover=cover,
                repository_url=repository_url,
            )
        )
        return (await self._unary(req)).skill_updated

    async def delete(self, slug: str) -> None:
        req = pb.Envelope(skills_delete_req=s_pb.SkillsDeleteRequest(slug=slug))
        await self._unary(req)

    # -- publish (async) ---------------------------------------------------

    async def publish(
        self,
        slug: str,
        raw_manifest: str,
        *,
        skill_md: str | None = None,
        readme: str | None = None,
        changelog: str | None = None,
    ) -> SkillsPublishResponse:
        """Publish a new version. The server LLM-parses ``raw_manifest`` async;
        poll :meth:`publish_status` for the result."""
        req = pb.Envelope(
            skills_publish_req=s_pb.SkillsPublishRequest(
                slug=slug,
                raw_manifest=raw_manifest,
                skill_md=skill_md,
                readme=readme,
                changelog=changelog,
            )
        )
        return (await self._unary(req)).skills_publish_resp

    async def publish_status(self, slug: str) -> SkillsPublishStatusResponse:
        req = pb.Envelope(
            skills_publish_status_req=s_pb.SkillsPublishStatusRequest(slug=slug)
        )
        return (await self._unary(req)).skills_publish_status_resp

    # -- taxonomy ----------------------------------------------------------

    async def categories(
        self, *, search: str | None = None, ordering: str | None = None
    ) -> SkillCategoryList:
        req = pb.Envelope(
            skills_categories_req=s_pb.SkillsCategoriesRequest(search=search, ordering=ordering)
        )
        return (await self._unary(req)).skill_category_list

    async def tags(
        self, *, search: str | None = None, ordering: str | None = None
    ) -> SkillTagList:
        req = pb.Envelope(skills_tags_req=s_pb.SkillsTagsRequest(search=search, ordering=ordering))
        return (await self._unary(req)).skill_tag_list
