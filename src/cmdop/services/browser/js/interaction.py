"""Interaction JavaScript builders for browser automation."""

from __future__ import annotations

import json


def build_hover_js(selector: str) -> str:
    """Build JS to hover over element."""
    return f"""
    (function() {{
        const el = document.querySelector("{selector}");
        if (!el) return JSON.stringify({{ success: false, error: 'Element not found' }});

        const event = new MouseEvent('mouseover', {{
            bubbles: true,
            cancelable: true,
            view: window
        }});
        el.dispatchEvent(event);

        return JSON.stringify({{ success: true }});
    }})()
    """


def build_select_js(selector: str, value: str | None = None, text: str | None = None) -> str:
    """
    Build JS to select option from dropdown.

    Args:
        selector: CSS selector for <select> element
        value: Option value to select
        text: Option text to select (if value not provided)
    """
    if value is not None:
        select_code = f'select.value = "{value}";'
    elif text is not None:
        select_code = f'''
        const option = Array.from(select.options).find(o => o.text === "{text}");
        if (option) select.value = option.value;
        '''
    else:
        return 'JSON.stringify({ success: false, error: "Need value or text" })'

    return f"""
    (function() {{
        const select = document.querySelector("{selector}");
        if (!select) return JSON.stringify({{ success: false, error: 'Select not found' }});

        {select_code}

        // Trigger change event
        select.dispatchEvent(new Event('change', {{ bubbles: true }}));

        return JSON.stringify({{
            success: true,
            selected_value: select.value,
            selected_text: select.options[select.selectedIndex]?.text
        }});
    }})()
    """


def build_close_modal_js(
    selectors: list[str] | None = None,
) -> str:
    """
    Build JS to close modal dialogs.

    Args:
        selectors: Custom selectors to try. Default tries common patterns.
    """
    default_selectors = [
        '[aria-label="Close"]',
        '[aria-label="Dismiss"]',
        'button[class*="close"]',
        'button[class*="dismiss"]',
        '[data-testid="close"]',
        '.modal-close',
        '.dialog-close',
        'button:has(svg[class*="close"])',
        'div[role="dialog"] button:first-child',
    ]
    all_selectors = selectors or default_selectors
    selectors_json = json.dumps(all_selectors)

    return f"""
    (function() {{
        const selectors = {selectors_json};

        for (const sel of selectors) {{
            try {{
                const el = document.querySelector(sel);
                if (el && el.offsetParent !== null) {{
                    el.click();
                    return JSON.stringify({{ success: true, selector: sel }});
                }}
            }} catch(e) {{
                // Skip invalid selectors
            }}
        }}

        // Try pressing Escape
        document.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Escape', code: 'Escape' }}));

        return JSON.stringify({{ success: false, error: 'No modal close button found' }});
    }})()
    """


def build_press_key_js(key: str, selector: str | None = None) -> str:
    """
    Build JS to press a keyboard key.

    Args:
        key: Key to press (e.g., 'Escape', 'Enter', 'Tab', 'ArrowDown')
        selector: Optional selector to target. If None, targets activeElement or body.

    Returns:
        JS code that returns { success: true/false }
    """
    # Map common key names to key codes
    key_codes = {
        'Escape': 27, 'Enter': 13, 'Tab': 9, 'Space': 32,
        'ArrowUp': 38, 'ArrowDown': 40, 'ArrowLeft': 37, 'ArrowRight': 39,
        'Backspace': 8, 'Delete': 46,
    }
    key_code = key_codes.get(key, 0)

    target_js = f'document.querySelector("{selector}")' if selector else '(document.activeElement || document.body)'

    return f"""
    (function() {{
        const target = {target_js};
        if (!target) return JSON.stringify({{ success: false, error: 'Target not found' }});

        const events = ['keydown', 'keypress', 'keyup'];
        for (const eventType of events) {{
            target.dispatchEvent(new KeyboardEvent(eventType, {{
                key: '{key}',
                code: '{key}',
                keyCode: {key_code},
                which: {key_code},
                bubbles: true,
                cancelable: true
            }}));
        }}

        return JSON.stringify({{ success: true, key: '{key}' }});
    }})()
    """


def build_click_all_by_text_js(text: str, role: str = "button") -> str:
    """
    Build JS to click all elements containing specific text.

    Args:
        text: Text to match (case-insensitive)
        role: Element role to filter (default: "button")

    Returns:
        JS code that returns { clicked: number }
    """
    return f"""
    (function() {{
        const elements = document.querySelectorAll('[role="{role}"]');
        let clicked = 0;
        const targetText = "{text}".toLowerCase();
        elements.forEach(el => {{
            const elText = el.textContent.trim().toLowerCase();
            if (elText === targetText || elText.includes(targetText)) {{
                el.click();
                clicked++;
            }}
        }});
        return JSON.stringify({{ clicked: clicked }});
    }})()
    """


def build_click_js(selector: str, scroll_into_view: bool = True) -> str:
    """
    Build JS to click element via JavaScript (more reliable than CDP click).

    This is useful when native CDP click hangs or doesn't work properly.
    Uses document.querySelector to find element and calls .click() directly.

    Args:
        selector: CSS selector for the element to click
        scroll_into_view: If True, scroll element into view before clicking (default: True)

    Returns:
        JS code that returns { success: true/false, error?: string }
    """
    scroll_code = 'el.scrollIntoView({block: "center", behavior: "instant"});' if scroll_into_view else ''
    selector_escaped = json.dumps(selector)

    return f"""
    (function() {{
        const el = document.querySelector({selector_escaped});
        if (!el) {{
            return JSON.stringify({{ success: false, error: 'Element not found' }});
        }}
        try {{
            {scroll_code}
            el.click();
            return JSON.stringify({{ success: true }});
        }} catch (e) {{
            return JSON.stringify({{ success: false, error: e.message }});
        }}
    }})()
    """
