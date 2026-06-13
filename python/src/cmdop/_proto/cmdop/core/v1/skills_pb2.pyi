from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SkillTag(_message.Message):
    __slots__ = ("id", "name", "slug")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    slug: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., slug: _Optional[str] = ...) -> None: ...

class SkillCategory(_message.Message):
    __slots__ = ("id", "name", "slug", "description", "icon", "ordering", "skill_count")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    ORDERING_FIELD_NUMBER: _ClassVar[int]
    SKILL_COUNT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    slug: str
    description: str
    icon: str
    ordering: int
    skill_count: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., slug: _Optional[str] = ..., description: _Optional[str] = ..., icon: _Optional[str] = ..., ordering: _Optional[int] = ..., skill_count: _Optional[int] = ...) -> None: ...

class SkillVersion(_message.Message):
    __slots__ = ("id", "skill", "version", "skill_md", "changelog", "model", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SKILL_MD_FIELD_NUMBER: _ClassVar[int]
    CHANGELOG_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    skill: str
    version: str
    skill_md: str
    changelog: str
    model: str
    created_at: str
    def __init__(self, id: _Optional[str] = ..., skill: _Optional[str] = ..., version: _Optional[str] = ..., skill_md: _Optional[str] = ..., changelog: _Optional[str] = ..., model: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class SkillReview(_message.Message):
    __slots__ = ("id", "author_handle", "author_display_name", "author_avatar_url", "body", "is_rewritten", "source", "upstream_created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    IS_REWRITTEN_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    author_handle: str
    author_display_name: str
    author_avatar_url: str
    body: str
    is_rewritten: bool
    source: str
    upstream_created_at: str
    def __init__(self, id: _Optional[str] = ..., author_handle: _Optional[str] = ..., author_display_name: _Optional[str] = ..., author_avatar_url: _Optional[str] = ..., body: _Optional[str] = ..., is_rewritten: _Optional[bool] = ..., source: _Optional[str] = ..., upstream_created_at: _Optional[str] = ...) -> None: ...

class SkillSummary(_message.Message):
    __slots__ = ("id", "slug", "name", "short_description", "author", "author_username", "category", "category_name", "tags", "visibility", "status", "is_verified", "icon", "cover", "install_count", "star_count", "download_count", "review_count", "is_starred", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_USERNAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IS_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    COVER_FIELD_NUMBER: _ClassVar[int]
    INSTALL_COUNT_FIELD_NUMBER: _ClassVar[int]
    STAR_COUNT_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_COUNT_FIELD_NUMBER: _ClassVar[int]
    REVIEW_COUNT_FIELD_NUMBER: _ClassVar[int]
    IS_STARRED_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    slug: str
    name: str
    short_description: str
    author: int
    author_username: str
    category: str
    category_name: str
    tags: _containers.RepeatedCompositeFieldContainer[SkillTag]
    visibility: str
    status: str
    is_verified: bool
    icon: str
    cover: str
    install_count: int
    star_count: int
    download_count: int
    review_count: int
    is_starred: bool
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., slug: _Optional[str] = ..., name: _Optional[str] = ..., short_description: _Optional[str] = ..., author: _Optional[int] = ..., author_username: _Optional[str] = ..., category: _Optional[str] = ..., category_name: _Optional[str] = ..., tags: _Optional[_Iterable[_Union[SkillTag, _Mapping]]] = ..., visibility: _Optional[str] = ..., status: _Optional[str] = ..., is_verified: _Optional[bool] = ..., icon: _Optional[str] = ..., cover: _Optional[str] = ..., install_count: _Optional[int] = ..., star_count: _Optional[int] = ..., download_count: _Optional[int] = ..., review_count: _Optional[int] = ..., is_starred: _Optional[bool] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class SkillDetail(_message.Message):
    __slots__ = ("id", "slug", "name", "short_description", "description", "readme", "author", "author_username", "category", "tags", "visibility", "status", "is_verified", "icon", "cover", "install_count", "star_count", "download_count", "repository_url", "latest_version", "is_starred", "reviews", "review_count", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    README_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_USERNAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IS_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    COVER_FIELD_NUMBER: _ClassVar[int]
    INSTALL_COUNT_FIELD_NUMBER: _ClassVar[int]
    STAR_COUNT_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_COUNT_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_URL_FIELD_NUMBER: _ClassVar[int]
    LATEST_VERSION_FIELD_NUMBER: _ClassVar[int]
    IS_STARRED_FIELD_NUMBER: _ClassVar[int]
    REVIEWS_FIELD_NUMBER: _ClassVar[int]
    REVIEW_COUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    slug: str
    name: str
    short_description: str
    description: str
    readme: str
    author: int
    author_username: str
    category: SkillCategory
    tags: _containers.RepeatedCompositeFieldContainer[SkillTag]
    visibility: str
    status: str
    is_verified: bool
    icon: str
    cover: str
    install_count: int
    star_count: int
    download_count: int
    repository_url: str
    latest_version: SkillVersion
    is_starred: bool
    reviews: _containers.RepeatedCompositeFieldContainer[SkillReview]
    review_count: int
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., slug: _Optional[str] = ..., name: _Optional[str] = ..., short_description: _Optional[str] = ..., description: _Optional[str] = ..., readme: _Optional[str] = ..., author: _Optional[int] = ..., author_username: _Optional[str] = ..., category: _Optional[_Union[SkillCategory, _Mapping]] = ..., tags: _Optional[_Iterable[_Union[SkillTag, _Mapping]]] = ..., visibility: _Optional[str] = ..., status: _Optional[str] = ..., is_verified: _Optional[bool] = ..., icon: _Optional[str] = ..., cover: _Optional[str] = ..., install_count: _Optional[int] = ..., star_count: _Optional[int] = ..., download_count: _Optional[int] = ..., repository_url: _Optional[str] = ..., latest_version: _Optional[_Union[SkillVersion, _Mapping]] = ..., is_starred: _Optional[bool] = ..., reviews: _Optional[_Iterable[_Union[SkillReview, _Mapping]]] = ..., review_count: _Optional[int] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class SkillFile(_message.Message):
    __slots__ = ("path", "content")
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    path: str
    content: str
    def __init__(self, path: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class SkillPackages(_message.Message):
    __slots__ = ("pip", "npm")
    PIP_FIELD_NUMBER: _ClassVar[int]
    NPM_FIELD_NUMBER: _ClassVar[int]
    pip: _containers.RepeatedScalarFieldContainer[str]
    npm: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, pip: _Optional[_Iterable[str]] = ..., npm: _Optional[_Iterable[str]] = ...) -> None: ...

class SkillMeta(_message.Message):
    __slots__ = ("installed_at", "installed_from", "installed_version", "updated_at")
    INSTALLED_AT_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_FROM_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_VERSION_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    installed_at: str
    installed_from: str
    installed_version: str
    updated_at: str
    def __init__(self, installed_at: _Optional[str] = ..., installed_from: _Optional[str] = ..., installed_version: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class SkillInstall(_message.Message):
    __slots__ = ("slug", "version", "model", "install_command", "readme", "skill_md", "files", "packages", "run_check", "meta")
    SLUG_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    INSTALL_COMMAND_FIELD_NUMBER: _ClassVar[int]
    README_FIELD_NUMBER: _ClassVar[int]
    SKILL_MD_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    PACKAGES_FIELD_NUMBER: _ClassVar[int]
    RUN_CHECK_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    slug: str
    version: str
    model: str
    install_command: str
    readme: str
    skill_md: str
    files: _containers.RepeatedCompositeFieldContainer[SkillFile]
    packages: SkillPackages
    run_check: str
    meta: SkillMeta
    def __init__(self, slug: _Optional[str] = ..., version: _Optional[str] = ..., model: _Optional[str] = ..., install_command: _Optional[str] = ..., readme: _Optional[str] = ..., skill_md: _Optional[str] = ..., files: _Optional[_Iterable[_Union[SkillFile, _Mapping]]] = ..., packages: _Optional[_Union[SkillPackages, _Mapping]] = ..., run_check: _Optional[str] = ..., meta: _Optional[_Union[SkillMeta, _Mapping]] = ...) -> None: ...

class SkillStar(_message.Message):
    __slots__ = ("starred", "star_count")
    STARRED_FIELD_NUMBER: _ClassVar[int]
    STAR_COUNT_FIELD_NUMBER: _ClassVar[int]
    starred: bool
    star_count: int
    def __init__(self, starred: _Optional[bool] = ..., star_count: _Optional[int] = ...) -> None: ...

class SkillsListRequest(_message.Message):
    __slots__ = ("category", "tag", "search", "lang", "ordering", "page", "page_size")
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    LANG_FIELD_NUMBER: _ClassVar[int]
    ORDERING_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    category: str
    tag: str
    search: str
    lang: str
    ordering: str
    page: int
    page_size: int
    def __init__(self, category: _Optional[str] = ..., tag: _Optional[str] = ..., search: _Optional[str] = ..., lang: _Optional[str] = ..., ordering: _Optional[str] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class SkillsMyRequest(_message.Message):
    __slots__ = ("search", "ordering", "page", "page_size")
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    ORDERING_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    search: str
    ordering: str
    page: int
    page_size: int
    def __init__(self, search: _Optional[str] = ..., ordering: _Optional[str] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class SkillListPage(_message.Message):
    __slots__ = ("count", "page", "pages", "page_size", "has_next", "has_previous", "next_page", "previous_page", "results")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    HAS_NEXT_FIELD_NUMBER: _ClassVar[int]
    HAS_PREVIOUS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_PAGE_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    count: int
    page: int
    pages: int
    page_size: int
    has_next: bool
    has_previous: bool
    next_page: int
    previous_page: int
    results: _containers.RepeatedCompositeFieldContainer[SkillSummary]
    def __init__(self, count: _Optional[int] = ..., page: _Optional[int] = ..., pages: _Optional[int] = ..., page_size: _Optional[int] = ..., has_next: _Optional[bool] = ..., has_previous: _Optional[bool] = ..., next_page: _Optional[int] = ..., previous_page: _Optional[int] = ..., results: _Optional[_Iterable[_Union[SkillSummary, _Mapping]]] = ...) -> None: ...

class SkillsGetRequest(_message.Message):
    __slots__ = ("slug", "lang")
    SLUG_FIELD_NUMBER: _ClassVar[int]
    LANG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    lang: str
    def __init__(self, slug: _Optional[str] = ..., lang: _Optional[str] = ...) -> None: ...

class SkillsInstallRequest(_message.Message):
    __slots__ = ("slug",)
    SLUG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    def __init__(self, slug: _Optional[str] = ...) -> None: ...

class SkillsStarRequest(_message.Message):
    __slots__ = ("slug",)
    SLUG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    def __init__(self, slug: _Optional[str] = ...) -> None: ...

class SkillsVersionsRequest(_message.Message):
    __slots__ = ("slug",)
    SLUG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    def __init__(self, slug: _Optional[str] = ...) -> None: ...

class SkillVersionList(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SkillVersion]
    def __init__(self, items: _Optional[_Iterable[_Union[SkillVersion, _Mapping]]] = ...) -> None: ...

class SkillsReviewsRequest(_message.Message):
    __slots__ = ("slug", "search", "ordering", "page", "page_size")
    SLUG_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    ORDERING_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    slug: str
    search: str
    ordering: str
    page: int
    page_size: int
    def __init__(self, slug: _Optional[str] = ..., search: _Optional[str] = ..., ordering: _Optional[str] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class SkillReviewPage(_message.Message):
    __slots__ = ("count", "page", "pages", "page_size", "has_next", "has_previous", "next_page", "previous_page", "results")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGES_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    HAS_NEXT_FIELD_NUMBER: _ClassVar[int]
    HAS_PREVIOUS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_PAGE_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    count: int
    page: int
    pages: int
    page_size: int
    has_next: bool
    has_previous: bool
    next_page: int
    previous_page: int
    results: _containers.RepeatedCompositeFieldContainer[SkillReview]
    def __init__(self, count: _Optional[int] = ..., page: _Optional[int] = ..., pages: _Optional[int] = ..., page_size: _Optional[int] = ..., has_next: _Optional[bool] = ..., has_previous: _Optional[bool] = ..., next_page: _Optional[int] = ..., previous_page: _Optional[int] = ..., results: _Optional[_Iterable[_Union[SkillReview, _Mapping]]] = ...) -> None: ...

class SkillsCreateRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class SkillCreated(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class SkillsUpdateRequest(_message.Message):
    __slots__ = ("slug", "name", "category", "visibility", "status", "icon", "cover", "repository_url")
    SLUG_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    COVER_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_URL_FIELD_NUMBER: _ClassVar[int]
    slug: str
    name: str
    category: str
    visibility: str
    status: str
    icon: str
    cover: str
    repository_url: str
    def __init__(self, slug: _Optional[str] = ..., name: _Optional[str] = ..., category: _Optional[str] = ..., visibility: _Optional[str] = ..., status: _Optional[str] = ..., icon: _Optional[str] = ..., cover: _Optional[str] = ..., repository_url: _Optional[str] = ...) -> None: ...

class SkillUpdated(_message.Message):
    __slots__ = ("name", "category", "visibility", "status", "icon", "cover", "repository_url")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    COVER_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_URL_FIELD_NUMBER: _ClassVar[int]
    name: str
    category: str
    visibility: str
    status: str
    icon: str
    cover: str
    repository_url: str
    def __init__(self, name: _Optional[str] = ..., category: _Optional[str] = ..., visibility: _Optional[str] = ..., status: _Optional[str] = ..., icon: _Optional[str] = ..., cover: _Optional[str] = ..., repository_url: _Optional[str] = ...) -> None: ...

class SkillsDeleteRequest(_message.Message):
    __slots__ = ("slug",)
    SLUG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    def __init__(self, slug: _Optional[str] = ...) -> None: ...

class SkillsPublishRequest(_message.Message):
    __slots__ = ("slug", "raw_manifest", "skill_md", "readme", "changelog")
    SLUG_FIELD_NUMBER: _ClassVar[int]
    RAW_MANIFEST_FIELD_NUMBER: _ClassVar[int]
    SKILL_MD_FIELD_NUMBER: _ClassVar[int]
    README_FIELD_NUMBER: _ClassVar[int]
    CHANGELOG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    raw_manifest: str
    skill_md: str
    readme: str
    changelog: str
    def __init__(self, slug: _Optional[str] = ..., raw_manifest: _Optional[str] = ..., skill_md: _Optional[str] = ..., readme: _Optional[str] = ..., changelog: _Optional[str] = ...) -> None: ...

class SkillsPublishResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class SkillsPublishStatusRequest(_message.Message):
    __slots__ = ("slug",)
    SLUG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    def __init__(self, slug: _Optional[str] = ...) -> None: ...

class SkillsPublishStatusResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class SkillsCategoriesRequest(_message.Message):
    __slots__ = ("search", "ordering")
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    ORDERING_FIELD_NUMBER: _ClassVar[int]
    search: str
    ordering: str
    def __init__(self, search: _Optional[str] = ..., ordering: _Optional[str] = ...) -> None: ...

class SkillCategoryList(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SkillCategory]
    def __init__(self, items: _Optional[_Iterable[_Union[SkillCategory, _Mapping]]] = ...) -> None: ...

class SkillsTagsRequest(_message.Message):
    __slots__ = ("search", "ordering")
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    ORDERING_FIELD_NUMBER: _ClassVar[int]
    search: str
    ordering: str
    def __init__(self, search: _Optional[str] = ..., ordering: _Optional[str] = ...) -> None: ...

class SkillTagList(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SkillTag]
    def __init__(self, items: _Optional[_Iterable[_Union[SkillTag, _Mapping]]] = ...) -> None: ...
