"""Scroll JavaScript builders for browser automation."""

from __future__ import annotations

import json


def build_scroll_js(
    direction: str = "down",
    amount: int = 500,
    selector: str | None = None,
    smooth: bool = True,
    human_like: bool = False,
    container: str | None = None,
) -> str:
    """
    Build JS for scrolling.

    Args:
        direction: "up", "down", "left", "right"
        amount: Pixels to scroll (ignored if selector provided)
        selector: CSS selector to scroll element into view
        smooth: Use smooth scroll animation (default True)
        human_like: Add random variations for natural scrolling
        container: CSS selector for scroll container (default: window)
    """
    if selector:
        behavior = "smooth" if smooth else "instant"
        # Escape selector for JS string (handle quotes)
        selector_escaped = selector.replace("\\", "\\\\").replace('"', '\\"')
        return f"""
        (async function() {{
            const el = document.querySelector("{selector_escaped}");
            if (el) {{
                el.scrollIntoView({{ behavior: '{behavior}', block: 'center' }});
                await new Promise(r => setTimeout(r, {300 if smooth else 50}));
                return JSON.stringify({{ success: true, scrollY: window.scrollY }});
            }}
            return JSON.stringify({{ success: false, error: 'Element not found' }});
        }})()
        """

    behavior = "smooth" if smooth else "instant"

    # Container scroll target
    container_js = f'document.querySelector("{container}")' if container else "null"

    if human_like:
        # Human-like scroll with random variation and micro-scrolls
        return f"""
        (async function() {{
            const container = {container_js};
            const scrollTarget = container || window;
            const getScrollY = () => container ? container.scrollTop : window.scrollY;
            const getMaxScroll = () => container
                ? container.scrollHeight - container.clientHeight
                : document.body.scrollHeight - window.innerHeight;

            const before = getScrollY();
            const baseAmount = {amount};
            const direction = "{direction}";

            // Random variation ±15%
            const variation = 0.85 + Math.random() * 0.3;
            const actualAmount = Math.round(baseAmount * variation);

            // Split into 2-4 micro-scrolls
            const steps = 2 + Math.floor(Math.random() * 3);
            const stepAmount = actualAmount / steps;

            for (let i = 0; i < steps; i++) {{
                const stepVariation = 0.8 + Math.random() * 0.4;
                const thisStep = Math.round(stepAmount * stepVariation);

                let x = 0, y = 0;
                if (direction === "down") y = thisStep;
                else if (direction === "up") y = -thisStep;
                else if (direction === "right") x = thisStep;
                else if (direction === "left") x = -thisStep;

                if (container) {{
                    container.scrollBy({{ left: x, top: y, behavior: '{behavior}' }});
                }} else {{
                    window.scrollBy({{ left: x, top: y, behavior: '{behavior}' }});
                }}

                // Random micro-pause 50-150ms between steps
                if (i < steps - 1) {{
                    await new Promise(r => setTimeout(r, 50 + Math.random() * 100));
                }}
            }}

            // Wait for smooth scroll to finish
            await new Promise(r => setTimeout(r, {250 if smooth else 50}));

            const after = getScrollY();
            return JSON.stringify({{
                success: true,
                scrollY: after,
                scrolledBy: after - before,
                atBottom: after >= getMaxScroll() - 50
            }});
        }})()
        """
    else:
        # Standard scroll
        scroll_x = 0
        scroll_y = 0
        if direction == "down":
            scroll_y = amount
        elif direction == "up":
            scroll_y = -amount
        elif direction == "right":
            scroll_x = amount
        elif direction == "left":
            scroll_x = -amount

        return f"""
        (async function() {{
            const container = {container_js};
            const getScrollY = () => container ? container.scrollTop : window.scrollY;
            const getMaxScroll = () => container
                ? container.scrollHeight - container.clientHeight
                : document.body.scrollHeight - window.innerHeight;

            const before = getScrollY();

            if (container) {{
                container.scrollBy({{ left: {scroll_x}, top: {scroll_y}, behavior: '{behavior}' }});
            }} else {{
                window.scrollBy({{ left: {scroll_x}, top: {scroll_y}, behavior: '{behavior}' }});
            }}

            // Wait for scroll to complete
            await new Promise(r => setTimeout(r, {200 if smooth else 30}));

            const after = getScrollY();
            return JSON.stringify({{
                success: true,
                scrollY: after,
                scrolledBy: after - before,
                atBottom: after >= getMaxScroll() - 50
            }});
        }})()
        """


def build_scroll_to_bottom_js() -> str:
    """Build JS to scroll to page bottom."""
    return """
    (function() {
        const before = window.scrollY;
        window.scrollTo(0, document.body.scrollHeight);
        return JSON.stringify({
            success: true,
            scrollY: window.scrollY,
            scrolledBy: window.scrollY - before,
            atBottom: true
        });
    })()
    """


def build_infinite_scroll_js(
    seen_keys: list[str],
    key_selector: str = "a[href]",
    key_attr: str = "href",
    container_selector: str = "body",
) -> str:
    """
    Build JS for infinite scroll with deduplication.

    Args:
        seen_keys: List of already seen keys (e.g., URLs)
        key_selector: CSS selector for key elements
        key_attr: Attribute to use as key (default: href)
        container_selector: Container to find elements in

    Returns:
        JS that returns {new_keys: [...], at_bottom: bool}
    """
    seen_json = json.dumps(seen_keys)
    return f"""
    (function() {{
        const seen = new Set({seen_json});
        const container = document.querySelector("{container_selector}");
        if (!container) return JSON.stringify({{ new_keys: [], at_bottom: true, error: 'Container not found' }});

        const elements = container.querySelectorAll("{key_selector}");
        const newKeys = [];

        elements.forEach(el => {{
            const key = el.getAttribute("{key_attr}") || el.textContent.trim();
            if (key && !seen.has(key)) {{
                seen.add(key);
                newKeys.push(key);
            }}
        }});

        const atBottom = (window.innerHeight + window.scrollY) >= document.body.scrollHeight - 100;

        return JSON.stringify({{
            new_keys: newKeys,
            at_bottom: atBottom,
            total_seen: seen.size
        }});
    }})()
    """


def build_get_scroll_info_js() -> str:
    """Build JS to get current scroll position and page dimensions."""
    return """
    (function() {
        return JSON.stringify({
            scrollX: window.scrollX,
            scrollY: window.scrollY,
            pageHeight: document.body.scrollHeight,
            pageWidth: document.body.scrollWidth,
            viewportHeight: window.innerHeight,
            viewportWidth: window.innerWidth,
            atBottom: (window.innerHeight + window.scrollY) >= document.body.scrollHeight - 10,
            atTop: window.scrollY <= 10
        });
    })()
    """
