from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WaitUntil(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WAIT_LOAD: _ClassVar[WaitUntil]
    WAIT_DOMCONTENTLOADED: _ClassVar[WaitUntil]
    WAIT_NETWORKIDLE: _ClassVar[WaitUntil]
    WAIT_COMMIT: _ClassVar[WaitUntil]
WAIT_LOAD: WaitUntil
WAIT_DOMCONTENTLOADED: WaitUntil
WAIT_NETWORKIDLE: WaitUntil
WAIT_COMMIT: WaitUntil

class BrowserCreateSessionRequest(_message.Message):
    __slots__ = ("session_id", "provider", "profile_id", "start_url", "headless", "width", "height", "block_images", "block_media")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    PROFILE_ID_FIELD_NUMBER: _ClassVar[int]
    START_URL_FIELD_NUMBER: _ClassVar[int]
    HEADLESS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_IMAGES_FIELD_NUMBER: _ClassVar[int]
    BLOCK_MEDIA_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    provider: str
    profile_id: str
    start_url: str
    headless: bool
    width: int
    height: int
    block_images: bool
    block_media: bool
    def __init__(self, session_id: _Optional[str] = ..., provider: _Optional[str] = ..., profile_id: _Optional[str] = ..., start_url: _Optional[str] = ..., headless: bool = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., block_images: bool = ..., block_media: bool = ...) -> None: ...

class BrowserCreateSessionResponse(_message.Message):
    __slots__ = ("success", "browser_session_id", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    browser_session_id: str
    error: str
    def __init__(self, success: bool = ..., browser_session_id: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserCloseSessionRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ...) -> None: ...

class BrowserCloseSessionResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserNavigateRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "url", "timeout_ms", "wait_until")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    WAIT_UNTIL_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    url: str
    timeout_ms: int
    wait_until: WaitUntil
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., url: _Optional[str] = ..., timeout_ms: _Optional[int] = ..., wait_until: _Optional[_Union[WaitUntil, str]] = ...) -> None: ...

class BrowserNavigateResponse(_message.Message):
    __slots__ = ("success", "final_url", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FINAL_URL_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    final_url: str
    error: str
    def __init__(self, success: bool = ..., final_url: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserClickRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "selector", "timeout_ms", "move_cursor")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    MOVE_CURSOR_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    selector: str
    timeout_ms: int
    move_cursor: bool
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., selector: _Optional[str] = ..., timeout_ms: _Optional[int] = ..., move_cursor: bool = ...) -> None: ...

class BrowserClickResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserTypeRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "selector", "text", "human_like", "clear_first")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    HUMAN_LIKE_FIELD_NUMBER: _ClassVar[int]
    CLEAR_FIRST_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    selector: str
    text: str
    human_like: bool
    clear_first: bool
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., selector: _Optional[str] = ..., text: _Optional[str] = ..., human_like: bool = ..., clear_first: bool = ...) -> None: ...

class BrowserTypeResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserWaitRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "selector", "timeout_ms")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    selector: str
    timeout_ms: int
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., selector: _Optional[str] = ..., timeout_ms: _Optional[int] = ...) -> None: ...

class BrowserWaitResponse(_message.Message):
    __slots__ = ("success", "found", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    found: bool
    error: str
    def __init__(self, success: bool = ..., found: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserExtractRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "selector", "attribute", "limit")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    selector: str
    attribute: str
    limit: int
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., selector: _Optional[str] = ..., attribute: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class BrowserExtractResponse(_message.Message):
    __slots__ = ("success", "values", "count", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    values: _containers.RepeatedScalarFieldContainer[str]
    count: int
    error: str
    def __init__(self, success: bool = ..., values: _Optional[_Iterable[str]] = ..., count: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserExtractRegexRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "pattern", "from_html", "limit")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    FROM_HTML_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    pattern: str
    from_html: bool
    limit: int
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., pattern: _Optional[str] = ..., from_html: bool = ..., limit: _Optional[int] = ...) -> None: ...

class BrowserExtractRegexResponse(_message.Message):
    __slots__ = ("success", "matches", "count", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MATCHES_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    matches: _containers.RepeatedScalarFieldContainer[str]
    count: int
    error: str
    def __init__(self, success: bool = ..., matches: _Optional[_Iterable[str]] = ..., count: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserGetHTMLRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "selector")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    selector: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., selector: _Optional[str] = ...) -> None: ...

class BrowserGetHTMLResponse(_message.Message):
    __slots__ = ("success", "html", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    HTML_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    html: str
    error: str
    def __init__(self, success: bool = ..., html: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserGetTextRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "selector")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    selector: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., selector: _Optional[str] = ...) -> None: ...

class BrowserGetTextResponse(_message.Message):
    __slots__ = ("success", "text", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    text: str
    error: str
    def __init__(self, success: bool = ..., text: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserExecuteScriptRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "script")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    script: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., script: _Optional[str] = ...) -> None: ...

class BrowserExecuteScriptResponse(_message.Message):
    __slots__ = ("success", "result", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    result: str
    error: str
    def __init__(self, success: bool = ..., result: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserScreenshotRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "full_page", "format", "quality")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    FULL_PAGE_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    full_page: bool
    format: str
    quality: int
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., full_page: bool = ..., format: _Optional[str] = ..., quality: _Optional[int] = ...) -> None: ...

class BrowserScreenshotResponse(_message.Message):
    __slots__ = ("success", "data", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    data: bytes
    error: str
    def __init__(self, success: bool = ..., data: _Optional[bytes] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserGetStateRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ...) -> None: ...

class BrowserGetStateResponse(_message.Message):
    __slots__ = ("success", "url", "title", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    url: str
    title: str
    error: str
    def __init__(self, success: bool = ..., url: _Optional[str] = ..., title: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserGetPageInfoRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ...) -> None: ...

class BrowserGetPageInfoResponse(_message.Message):
    __slots__ = ("success", "error", "url", "title", "page_height", "viewport_height", "viewport_width", "scroll_x", "scroll_y", "at_top", "at_bottom", "load_time_ms", "cookies_count", "is_https", "has_iframes", "dom_nodes_raw", "dom_nodes_cleaned", "tokens_estimate", "cloudflare_detected", "captcha_detected")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PAGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    VIEWPORT_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    VIEWPORT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    SCROLL_X_FIELD_NUMBER: _ClassVar[int]
    SCROLL_Y_FIELD_NUMBER: _ClassVar[int]
    AT_TOP_FIELD_NUMBER: _ClassVar[int]
    AT_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    LOAD_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    COOKIES_COUNT_FIELD_NUMBER: _ClassVar[int]
    IS_HTTPS_FIELD_NUMBER: _ClassVar[int]
    HAS_IFRAMES_FIELD_NUMBER: _ClassVar[int]
    DOM_NODES_RAW_FIELD_NUMBER: _ClassVar[int]
    DOM_NODES_CLEANED_FIELD_NUMBER: _ClassVar[int]
    TOKENS_ESTIMATE_FIELD_NUMBER: _ClassVar[int]
    CLOUDFLARE_DETECTED_FIELD_NUMBER: _ClassVar[int]
    CAPTCHA_DETECTED_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    url: str
    title: str
    page_height: int
    viewport_height: int
    viewport_width: int
    scroll_x: int
    scroll_y: int
    at_top: bool
    at_bottom: bool
    load_time_ms: int
    cookies_count: int
    is_https: bool
    has_iframes: bool
    dom_nodes_raw: int
    dom_nodes_cleaned: int
    tokens_estimate: int
    cloudflare_detected: bool
    captcha_detected: bool
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., url: _Optional[str] = ..., title: _Optional[str] = ..., page_height: _Optional[int] = ..., viewport_height: _Optional[int] = ..., viewport_width: _Optional[int] = ..., scroll_x: _Optional[int] = ..., scroll_y: _Optional[int] = ..., at_top: bool = ..., at_bottom: bool = ..., load_time_ms: _Optional[int] = ..., cookies_count: _Optional[int] = ..., is_https: bool = ..., has_iframes: bool = ..., dom_nodes_raw: _Optional[int] = ..., dom_nodes_cleaned: _Optional[int] = ..., tokens_estimate: _Optional[int] = ..., cloudflare_detected: bool = ..., captcha_detected: bool = ...) -> None: ...

class BrowserCookie(_message.Message):
    __slots__ = ("name", "value", "domain", "path", "secure", "http_only", "same_site", "expires")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SECURE_FIELD_NUMBER: _ClassVar[int]
    HTTP_ONLY_FIELD_NUMBER: _ClassVar[int]
    SAME_SITE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    domain: str
    path: str
    secure: bool
    http_only: bool
    same_site: str
    expires: int
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., domain: _Optional[str] = ..., path: _Optional[str] = ..., secure: bool = ..., http_only: bool = ..., same_site: _Optional[str] = ..., expires: _Optional[int] = ...) -> None: ...

class BrowserSetCookiesRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "cookies")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    COOKIES_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    cookies: _containers.RepeatedCompositeFieldContainer[BrowserCookie]
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., cookies: _Optional[_Iterable[_Union[BrowserCookie, _Mapping]]] = ...) -> None: ...

class BrowserSetCookiesResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserGetCookiesRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "domain")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    domain: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., domain: _Optional[str] = ...) -> None: ...

class BrowserGetCookiesResponse(_message.Message):
    __slots__ = ("success", "cookies", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    COOKIES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    cookies: _containers.RepeatedCompositeFieldContainer[BrowserCookie]
    error: str
    def __init__(self, success: bool = ..., cookies: _Optional[_Iterable[_Union[BrowserCookie, _Mapping]]] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserMouseMoveRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "x", "y", "steps")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    x: int
    y: int
    steps: int
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., steps: _Optional[int] = ...) -> None: ...

class BrowserMouseMoveResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserHoverRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "selector", "timeout_ms")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    selector: str
    timeout_ms: int
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., selector: _Optional[str] = ..., timeout_ms: _Optional[int] = ...) -> None: ...

class BrowserHoverResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserScrollRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "direction", "amount", "selector", "container", "smooth")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_FIELD_NUMBER: _ClassVar[int]
    SMOOTH_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    direction: str
    amount: int
    selector: str
    container: str
    smooth: bool
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., direction: _Optional[str] = ..., amount: _Optional[int] = ..., selector: _Optional[str] = ..., container: _Optional[str] = ..., smooth: bool = ...) -> None: ...

class BrowserScrollResponse(_message.Message):
    __slots__ = ("success", "scroll_x", "scroll_y", "scrolled_by", "page_height", "viewport_height", "at_bottom", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    SCROLL_X_FIELD_NUMBER: _ClassVar[int]
    SCROLL_Y_FIELD_NUMBER: _ClassVar[int]
    SCROLLED_BY_FIELD_NUMBER: _ClassVar[int]
    PAGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    VIEWPORT_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    AT_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    scroll_x: int
    scroll_y: int
    scrolled_by: int
    page_height: int
    viewport_height: int
    at_bottom: bool
    error: str
    def __init__(self, success: bool = ..., scroll_x: _Optional[int] = ..., scroll_y: _Optional[int] = ..., scrolled_by: _Optional[int] = ..., page_height: _Optional[int] = ..., viewport_height: _Optional[int] = ..., at_bottom: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserValidateSelectorsRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "item", "fields")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    item: str
    fields: _containers.ScalarMap[str, str]
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., item: _Optional[str] = ..., fields: _Optional[_Mapping[str, str]] = ...) -> None: ...

class BrowserValidateSelectorsResponse(_message.Message):
    __slots__ = ("success", "valid", "counts", "samples", "errors", "error")
    class CountsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SamplesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    VALID_FIELD_NUMBER: _ClassVar[int]
    COUNTS_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    valid: bool
    counts: _containers.ScalarMap[str, int]
    samples: _containers.ScalarMap[str, str]
    errors: _containers.RepeatedScalarFieldContainer[str]
    error: str
    def __init__(self, success: bool = ..., valid: bool = ..., counts: _Optional[_Mapping[str, int]] = ..., samples: _Optional[_Mapping[str, str]] = ..., errors: _Optional[_Iterable[str]] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserExtractDataRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "item", "fields_json", "limit")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    FIELDS_JSON_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    item: str
    fields_json: str
    limit: int
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., item: _Optional[str] = ..., fields_json: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class BrowserExtractDataResponse(_message.Message):
    __slots__ = ("success", "items_json", "count", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ITEMS_JSON_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    items_json: str
    count: int
    error: str
    def __init__(self, success: bool = ..., items_json: _Optional[str] = ..., count: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserNetworkEnableRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "max_exchanges", "max_response_size")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_EXCHANGES_FIELD_NUMBER: _ClassVar[int]
    MAX_RESPONSE_SIZE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    max_exchanges: int
    max_response_size: int
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., max_exchanges: _Optional[int] = ..., max_response_size: _Optional[int] = ...) -> None: ...

class BrowserNetworkEnableResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserNetworkDisableRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ...) -> None: ...

class BrowserNetworkDisableResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserNetworkGetExchangesRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "url_pattern", "methods", "status_codes", "resource_types", "limit")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    URL_PATTERN_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    url_pattern: str
    methods: _containers.RepeatedScalarFieldContainer[str]
    status_codes: _containers.RepeatedScalarFieldContainer[int]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    limit: int
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., url_pattern: _Optional[str] = ..., methods: _Optional[_Iterable[str]] = ..., status_codes: _Optional[_Iterable[int]] = ..., resource_types: _Optional[_Iterable[str]] = ..., limit: _Optional[int] = ...) -> None: ...

class BrowserNetworkGetExchangesResponse(_message.Message):
    __slots__ = ("success", "exchanges", "count", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    EXCHANGES_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    exchanges: _containers.RepeatedCompositeFieldContainer[NetworkExchange]
    count: int
    error: str
    def __init__(self, success: bool = ..., exchanges: _Optional[_Iterable[_Union[NetworkExchange, _Mapping]]] = ..., count: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserNetworkGetExchangeRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "exchange_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    exchange_id: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., exchange_id: _Optional[str] = ...) -> None: ...

class BrowserNetworkGetExchangeResponse(_message.Message):
    __slots__ = ("success", "exchange", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    exchange: NetworkExchange
    error: str
    def __init__(self, success: bool = ..., exchange: _Optional[_Union[NetworkExchange, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserNetworkGetLastRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "url_pattern")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    URL_PATTERN_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    url_pattern: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., url_pattern: _Optional[str] = ...) -> None: ...

class BrowserNetworkGetLastResponse(_message.Message):
    __slots__ = ("success", "exchange", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    exchange: NetworkExchange
    error: str
    def __init__(self, success: bool = ..., exchange: _Optional[_Union[NetworkExchange, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserNetworkClearRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ...) -> None: ...

class BrowserNetworkClearResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class BrowserNetworkStatsRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ...) -> None: ...

class BrowserNetworkStatsResponse(_message.Message):
    __slots__ = ("success", "enabled", "total_captured", "total_errors", "total_bytes", "average_duration_ms", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CAPTURED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ERRORS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    enabled: bool
    total_captured: int
    total_errors: int
    total_bytes: int
    average_duration_ms: int
    error: str
    def __init__(self, success: bool = ..., enabled: bool = ..., total_captured: _Optional[int] = ..., total_errors: _Optional[int] = ..., total_bytes: _Optional[int] = ..., average_duration_ms: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class BrowserNetworkExportHARRequest(_message.Message):
    __slots__ = ("session_id", "browser_session_id", "url_pattern", "methods", "status_codes", "resource_types")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    BROWSER_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    URL_PATTERN_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    browser_session_id: str
    url_pattern: str
    methods: _containers.RepeatedScalarFieldContainer[str]
    status_codes: _containers.RepeatedScalarFieldContainer[int]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, session_id: _Optional[str] = ..., browser_session_id: _Optional[str] = ..., url_pattern: _Optional[str] = ..., methods: _Optional[_Iterable[str]] = ..., status_codes: _Optional[_Iterable[int]] = ..., resource_types: _Optional[_Iterable[str]] = ...) -> None: ...

class BrowserNetworkExportHARResponse(_message.Message):
    __slots__ = ("success", "har_data", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    HAR_DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    har_data: bytes
    error: str
    def __init__(self, success: bool = ..., har_data: _Optional[bytes] = ..., error: _Optional[str] = ...) -> None: ...

class NetworkRequest(_message.Message):
    __slots__ = ("url", "method", "headers", "body", "content_type", "resource_type")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URL_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    url: str
    method: str
    headers: _containers.ScalarMap[str, str]
    body: bytes
    content_type: str
    resource_type: str
    def __init__(self, url: _Optional[str] = ..., method: _Optional[str] = ..., headers: _Optional[_Mapping[str, str]] = ..., body: _Optional[bytes] = ..., content_type: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class NetworkResponse(_message.Message):
    __slots__ = ("status", "status_text", "headers", "body", "content_type", "size", "from_cache")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_TEXT_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    FROM_CACHE_FIELD_NUMBER: _ClassVar[int]
    status: int
    status_text: str
    headers: _containers.ScalarMap[str, str]
    body: bytes
    content_type: str
    size: int
    from_cache: bool
    def __init__(self, status: _Optional[int] = ..., status_text: _Optional[str] = ..., headers: _Optional[_Mapping[str, str]] = ..., body: _Optional[bytes] = ..., content_type: _Optional[str] = ..., size: _Optional[int] = ..., from_cache: bool = ...) -> None: ...

class NetworkTiming(_message.Message):
    __slots__ = ("started_at_ms", "ended_at_ms", "duration_ms", "wait_time_ms", "receive_time_ms")
    STARTED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    WAIT_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    RECEIVE_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    started_at_ms: int
    ended_at_ms: int
    duration_ms: int
    wait_time_ms: int
    receive_time_ms: int
    def __init__(self, started_at_ms: _Optional[int] = ..., ended_at_ms: _Optional[int] = ..., duration_ms: _Optional[int] = ..., wait_time_ms: _Optional[int] = ..., receive_time_ms: _Optional[int] = ...) -> None: ...

class NetworkExchange(_message.Message):
    __slots__ = ("id", "request", "response", "timing", "error", "frame_id", "initiator")
    ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    TIMING_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    INITIATOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    request: NetworkRequest
    response: NetworkResponse
    timing: NetworkTiming
    error: str
    frame_id: str
    initiator: str
    def __init__(self, id: _Optional[str] = ..., request: _Optional[_Union[NetworkRequest, _Mapping]] = ..., response: _Optional[_Union[NetworkResponse, _Mapping]] = ..., timing: _Optional[_Union[NetworkTiming, _Mapping]] = ..., error: _Optional[str] = ..., frame_id: _Optional[str] = ..., initiator: _Optional[str] = ...) -> None: ...
