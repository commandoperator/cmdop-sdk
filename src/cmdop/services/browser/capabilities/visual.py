"""Visual capability - CMDOP plugin overlay effects."""

from __future__ import annotations

import time

from ._base import BaseCapability


class VisualCapability(BaseCapability):
    """Visual effects via CMDOP browser plugin.

    Provides toast notifications, click effects, highlights, etc.

    Usage:
        b.visual.toast("Hello!")
        b.visual.countdown(10)  # Smart countdown with early exit
        b.visual.highlight(".button")
    """

    def _dispatch(self, action: str, data: dict) -> None:
        """Dispatch visual action via CMDOP Visual extension.

        Uses "mw:" prefix for main world execution to access __CMDOP_VISUAL__.
        The extension API internally handles postMessage to content script.
        """
        import json
        data_json = json.dumps(data)
        # "mw:" prefix tells Go backend to execute in main world context
        self._js(f"""mw:(() => {{
                const data = {data_json};
                const api = window.__CMDOP_VISUAL__;
                if (!api) return;

                switch ('{action}') {{
                    case 'toast': api.showToast?.(data.message); break;
                    case 'clearToasts': api.clearToasts?.(); break;
                    case 'click': api.showClick?.(data.x, data.y, data.type || 'left'); break;
                    case 'move': api.showMouseMove?.(data.fromX, data.fromY, data.toX, data.toY); break;
                    case 'highlight': api.showHighlight?.(data.selector); break;
                    case 'hideHighlight': api.hideHighlight?.(); break;
                    case 'clearTrail': api.clearTrail?.(); break;
                    case 'state': api.setAutomationState?.(data.state); break;
                }}
            }})()
        """)

    def toast(self, message: str) -> None:
        """Show toast notification in browser."""
        self._dispatch("toast", {"message": message})

    def clear_toasts(self) -> None:
        """Clear all toast notifications."""
        self._dispatch("clearToasts", {})

    def click(self, x: int, y: int, click_type: str = "left") -> None:
        """Show click effect at coordinates."""
        self._dispatch("click", {"x": x, "y": y, "type": click_type})

    def move(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None:
        """Show mouse movement trail."""
        self._dispatch("move", {"fromX": from_x, "fromY": from_y, "toX": to_x, "toY": to_y})

    def highlight(self, selector: str) -> None:
        """Highlight element by selector."""
        self._dispatch("highlight", {"selector": selector})

    def hide_highlight(self) -> None:
        """Hide element highlight."""
        self._dispatch("hideHighlight", {})

    def clear_trail(self) -> None:
        """Clear cursor trail."""
        self._dispatch("clearTrail", {})

    def set_state(self, state: str) -> None:
        """Set automation state: 'idle', 'active', 'busy'."""
        self._dispatch("state", {"state": state})

    def countdown(self, seconds: int, message: str = "Click pagination!") -> None:
        """Visual countdown timer with toast notifications.

        Shows countdown in browser while user interacts with page.
        No early exit - just waits the full duration.

        Args:
            seconds: Seconds to wait
            message: Message to show with countdown
        """
        for i in range(seconds, 0, -1):
            try:
                self.clear_toasts()
                self.toast(f"⏱️ {i}s - {message}")
            except Exception:
                pass

            print(f"{i}", end=" ", flush=True)
            time.sleep(1)

        print("done", flush=True)
