"""JavaScript builders for browser automation.

This module provides JavaScript code generators for common browser operations:
- Core: JSON parsing, async wrappers
- Fetch: HTTP requests from browser context
- Scroll: Page scrolling and infinite scroll
- Interaction: Hover, select, modals
"""

from .core import (
    parse_json_result,
    build_async_js,
)

from .fetch import (
    build_fetch_js,
    build_fetch_all_js,
)

from .scroll import (
    build_scroll_js,
    build_scroll_to_bottom_js,
    build_infinite_scroll_js,
    build_get_scroll_info_js,
)

from .interaction import (
    build_hover_js,
    build_select_js,
    build_close_modal_js,
    build_click_all_by_text_js,
    build_press_key_js,
    build_click_js,
)

__all__ = [
    # Core
    "parse_json_result",
    "build_async_js",
    # Fetch
    "build_fetch_js",
    "build_fetch_all_js",
    # Scroll
    "build_scroll_js",
    "build_scroll_to_bottom_js",
    "build_infinite_scroll_js",
    "build_get_scroll_info_js",
    # Interaction
    "build_hover_js",
    "build_select_js",
    "build_close_modal_js",
    "build_click_all_by_text_js",
    "build_press_key_js",
    "build_click_js",
]
