# Generated from cmdop/crates/tools/tools.schema.json (sha256 cef76f12c6264508, cmdop 0.1.16) by exports/sdk/gen/gen.ts. Do not edit.
"""The tools the server answers itself, as methods of `Client` and `AsyncClient`. No machine, never sealed."""

from __future__ import annotations

from typing import Any

from typing_extensions import Unpack

from . import server_args as sa
from . import server_models as sm

SERVER_TOOLS: dict[str, str] = {
    "docs_read": "Read the docs",
    "history_search": "Search history",
    "machines_list": "List machines",
    "showtime_guide": "Showtime guide",
    "tasks_list": "List running work",
}
"""Every server tool and its title."""


class ServerTools:
    def _server(self, name: str, args: dict[str, Any], out: Any, deadline: float | None) -> Any:
        raise NotImplementedError

    def docs_read(self, *, deadline: float | None = None, **args: Unpack[sa.DocsReadArgs]) -> str:
        """Call before answering how CMDOP works, is set up or is priced: no `path` lists every page of docs.cmdop.ai (path and title); a `path` returns that page as Markdown."""
        return self._server("docs_read", dict(args), str, deadline)

    def history_search(self, *, deadline: float | None = None, **args: Unpack[sa.HistorySearchArgs]) -> sm.HistorySearchOut:
        """Past tasks, tool calls and agent sessions by machine, author, task, time and text, newest first. Calls carry no arguments; journal_search on the machine has them."""
        return self._server("history_search", dict(args), sm.HistorySearchOut, deadline)

    def machines_list(self, *, deadline: float | None = None, **args: Unpack[sa.MachinesListArgs]) -> list[sm.MachineRow]:
        """The owner's machines: name, id, `state` (online; stale = not answering; paused; offline), `last_seen`, `activity`, `tools` (screen and control are here), build, `behind`. Only online ones take calls."""
        return self._server("machines_list", dict(args), list[sm.MachineRow], deadline)

    def showtime_guide(self, *, deadline: float | None = None, **args: Unpack[sa.ShowtimeGuideArgs]) -> str:
        """Call when the user asks to see what CMDOP can do (a demo or a show), or offer it to a user new to CMDOP: returns a guide for a short live demonstration on their machines."""
        return self._server("showtime_guide", dict(args), str, deadline)

    def tasks_list(self, *, deadline: float | None = None, **args: Unpack[sa.TasksListArgs]) -> sm.TasksListOut:
        """Everything running now, by author. `tasks`: started through cmdop. `outside`: other processes per machine, by agent:claude-code, agent:codex or user. Ended ones: history_search."""
        return self._server("tasks_list", dict(args), sm.TasksListOut, deadline)


class AsyncServerTools:
    async def _server(self, name: str, args: dict[str, Any], out: Any, deadline: float | None) -> Any:
        raise NotImplementedError

    async def docs_read(self, *, deadline: float | None = None, **args: Unpack[sa.DocsReadArgs]) -> str:
        """Call before answering how CMDOP works, is set up or is priced: no `path` lists every page of docs.cmdop.ai (path and title); a `path` returns that page as Markdown."""
        return await self._server("docs_read", dict(args), str, deadline)

    async def history_search(self, *, deadline: float | None = None, **args: Unpack[sa.HistorySearchArgs]) -> sm.HistorySearchOut:
        """Past tasks, tool calls and agent sessions by machine, author, task, time and text, newest first. Calls carry no arguments; journal_search on the machine has them."""
        return await self._server("history_search", dict(args), sm.HistorySearchOut, deadline)

    async def machines_list(self, *, deadline: float | None = None, **args: Unpack[sa.MachinesListArgs]) -> list[sm.MachineRow]:
        """The owner's machines: name, id, `state` (online; stale = not answering; paused; offline), `last_seen`, `activity`, `tools` (screen and control are here), build, `behind`. Only online ones take calls."""
        return await self._server("machines_list", dict(args), list[sm.MachineRow], deadline)

    async def showtime_guide(self, *, deadline: float | None = None, **args: Unpack[sa.ShowtimeGuideArgs]) -> str:
        """Call when the user asks to see what CMDOP can do (a demo or a show), or offer it to a user new to CMDOP: returns a guide for a short live demonstration on their machines."""
        return await self._server("showtime_guide", dict(args), str, deadline)

    async def tasks_list(self, *, deadline: float | None = None, **args: Unpack[sa.TasksListArgs]) -> sm.TasksListOut:
        """Everything running now, by author. `tasks`: started through cmdop. `outside`: other processes per machine, by agent:claude-code, agent:codex or user. Ended ones: history_search."""
        return await self._server("tasks_list", dict(args), sm.TasksListOut, deadline)
