"""
Full TUI application using Textual.

Provides a rich terminal interface with:
- Machine list sidebar
- Multiple terminal tabs
- Real-time terminal rendering
- Status bar with connection info
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Footer,
    Header,
    ListItem,
    ListView,
    RichLog,
    Static,
    TabbedContent,
    TabPane,
)

if TYPE_CHECKING:
    from cmdop import AsyncCMDOPClient
    from cmdop.streaming.terminal import TerminalStream


class MachineItem(ListItem):
    """A machine in the sidebar list."""

    def __init__(
        self,
        hostname: str,
        session_id: str,
        status: str = "connected",
        os: str = "unknown",
    ) -> None:
        super().__init__()
        self.hostname = hostname
        self.session_id = session_id
        self.machine_status = status
        self.os = os

    def compose(self) -> ComposeResult:
        status_icon = "[green]●[/green]" if self.machine_status == "connected" else "[red]●[/red]"
        yield Static(f"{status_icon} {self.hostname[:25]}", classes="machine-name")


class TerminalPane(TabPane):
    """A terminal tab with streaming output."""

    def __init__(
        self,
        hostname: str,
        session_id: str,
        api_key: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(hostname, *args, **kwargs)
        self.hostname = hostname
        self.session_id = session_id
        self.api_key = api_key
        self._stream: TerminalStream | None = None
        self._connected = False

    def compose(self) -> ComposeResult:
        yield RichLog(id=f"terminal-{self.session_id}", highlight=True, markup=True)

    async def on_mount(self) -> None:
        """Connect when tab is mounted."""
        await self._connect()

    async def _connect(self) -> None:
        """Connect to terminal stream."""
        from cmdop import AsyncCMDOPClient

        log = self.query_one(RichLog)
        log.write(f"[dim]Connecting to {self.hostname}...[/dim]")

        try:
            self._client = AsyncCMDOPClient.remote(api_key=self.api_key)
            await self._client.__aenter__()

            self._stream = self._client.terminal.stream()

            # Setup callbacks
            def on_output(data: bytes) -> None:
                text = data.decode("utf-8", errors="replace")
                self.call_later(lambda: log.write(Text.from_ansi(text)))

            def on_error(code: str, message: str, _is_fatal: bool) -> None:
                self.call_later(lambda: log.write(f"[red]Error: {code}: {message}[/red]"))

            self._stream.on_output(on_output)
            self._stream.on_error(on_error)

            await self._stream.connect(timeout=10.0)
            await self._stream.wait_ready(timeout=5.0)

            self._connected = True
            log.write(f"[green]Connected to {self.hostname}[/green]\n")

        except Exception as e:
            log.write(f"[red]Connection failed: {e}[/red]")

    async def send_input(self, data: str) -> None:
        """Send input to terminal."""
        if self._stream and self._connected:
            await self._stream.send_input(data)

    async def disconnect(self) -> None:
        """Disconnect from terminal."""
        if self._stream:
            await self._stream.close()
        if hasattr(self, "_client"):
            await self._client.__aexit__(None, None, None)


class CMDOPApp(App):
    """CMDOP Terminal User Interface."""

    CSS = """
    #sidebar {
        width: 30;
        background: $surface;
        border-right: solid $primary;
    }

    #sidebar-header {
        height: 3;
        content-align: center middle;
        background: $primary;
    }

    #main-content {
        width: 1fr;
    }

    .machine-name {
        padding: 0 1;
    }

    ListView > ListItem.--highlight {
        background: $accent;
    }

    RichLog {
        background: $surface;
    }

    #status-bar {
        height: 1;
        background: $surface-darken-1;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("n", "new_tab", "New Tab"),
        Binding("w", "close_tab", "Close Tab"),
    ]

    def __init__(self, api_key: str) -> None:
        super().__init__()
        self.api_key = api_key
        self._machines: list[dict] = []
        self._active_tabs: dict[str, TerminalPane] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("Machines", id="sidebar-header")
                yield ListView(id="machine-list")
            with Vertical(id="main-content"):
                yield TabbedContent(id="terminals")
        yield Static("Ready", id="status-bar")
        yield Footer()

    async def on_mount(self) -> None:
        """Load machines on mount."""
        await self._load_machines()

    async def _load_machines(self) -> None:
        """Load machine list from API."""
        from cmdop import AsyncCMDOPClient

        status_bar = self.query_one("#status-bar", Static)
        status_bar.update("Loading machines...")

        try:
            async with AsyncCMDOPClient.remote(api_key=self.api_key) as client:
                response = await client.terminal.list_sessions()

                machine_list = self.query_one("#machine-list", ListView)
                await machine_list.clear()

                for session in response.sessions:
                    item = MachineItem(
                        hostname=session.machine_hostname,
                        session_id=session.session_id,
                        status=session.status,
                        os=session.os or "unknown",
                    )
                    await machine_list.append(item)
                    self._machines.append({
                        "hostname": session.machine_hostname,
                        "session_id": session.session_id,
                    })

                status_bar.update(f"{len(response.sessions)} machines")

        except Exception as e:
            status_bar.update(f"Error: {e}")

    @on(ListView.Selected, "#machine-list")
    async def on_machine_selected(self, event: ListView.Selected) -> None:
        """Handle machine selection."""
        item = event.item
        if isinstance(item, MachineItem):
            await self._open_terminal(item.hostname, item.session_id)

    async def _open_terminal(self, hostname: str, session_id: str) -> None:
        """Open terminal tab for machine."""
        # Check if already open
        if session_id in self._active_tabs:
            tabs = self.query_one("#terminals", TabbedContent)
            tabs.active = f"tab-{session_id}"
            return

        # Create new tab
        pane = TerminalPane(
            hostname=hostname,
            session_id=session_id,
            api_key=self.api_key,
            id=f"tab-{session_id}",
        )

        tabs = self.query_one("#terminals", TabbedContent)
        await tabs.add_pane(pane)
        tabs.active = f"tab-{session_id}"

        self._active_tabs[session_id] = pane

        status_bar = self.query_one("#status-bar", Static)
        status_bar.update(f"Connected to {hostname}")

    async def action_refresh(self) -> None:
        """Refresh machine list."""
        await self._load_machines()

    async def action_new_tab(self) -> None:
        """Open new terminal tab."""
        # Select first machine if available
        if self._machines:
            machine = self._machines[0]
            await self._open_terminal(machine["hostname"], machine["session_id"])

    async def action_close_tab(self) -> None:
        """Close current terminal tab."""
        tabs = self.query_one("#terminals", TabbedContent)
        active_id = tabs.active

        if active_id and active_id.startswith("tab-"):
            session_id = active_id[4:]
            if session_id in self._active_tabs:
                pane = self._active_tabs.pop(session_id)
                await pane.disconnect()
                await tabs.remove_pane(active_id)

    async def on_unmount(self) -> None:
        """Cleanup on exit."""
        for pane in self._active_tabs.values():
            await pane.disconnect()


async def run_tui(api_key: str) -> int:
    """Run the TUI application.

    Args:
        api_key: CMDOP API key.

    Returns:
        Exit code.
    """
    app = CMDOPApp(api_key)
    await app.run_async()
    return 0


def main() -> None:
    """CLI entry point for TUI."""
    import os
    import sys

    api_key = os.getenv("CMDOP_API_KEY", "")
    if not api_key:
        print("Error: Set CMDOP_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run_tui(api_key))


if __name__ == "__main__":
    main()
