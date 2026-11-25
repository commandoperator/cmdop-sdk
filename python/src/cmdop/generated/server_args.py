# Generated from cmdop/crates/tools/tools.schema.json (sha256 7128f6bbae917b61, cmdop 0.1.16) by exports/sdk/gen/gen.ts. Do not edit.
# Types by datamodel-code-generator==0.30.2.

from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired


class DocsReadArgs(TypedDict):
    path: NotRequired[str | None]
    """
    The page: `guides/connect`, `/guides/connect`, its docs.cmdop.ai address or the `.md`
    link a page carries. Absent: the contents, every page with its path and title.
    """


class HistorySearchArgs(TypedDict):
    author: NotRequired[str | None]
    """
    Author or its start: `owner`, `agent:` (every agent), `agent:<name>`.
    """
    kind: NotRequired[list[Literal["tasks", "sessions", "calls"]]]
    """
    What to return. Default: tasks, sessions and calls.
    """
    limit: NotRequired[int | None]
    """
    At most this many of each kind, newest first (default 50, at most 200).
    """
    machine: NotRequired[str | None]
    """
    Only this machine (name or id).
    """
    since: NotRequired[int | None]
    """
    Started (sessions: last changed) at or after this time, unix seconds.
    """
    task: NotRequired[int | None]
    """
    Only this task (its row and the calls that started or named it; no sessions).
    """
    text: NotRequired[str | None]
    """
    Text, any case. Tasks: the command, the folder or the error (another author's only for an
    agent granted exec). Sessions: path, id, folder. Calls: the tool name.
    """
    until: NotRequired[int | None]
    """
    Started (sessions: last changed) before this time, unix seconds.
    """


class MachinesListArgs(TypedDict):
    """
    No arguments.
    """


class ShowtimeGuideArgs(TypedDict):
    language: NotRequired[str | None]
    """
    The language to speak to the user in, e.g. "Russian" or "de". Default: the user's.
    """
    os: NotRequired[Literal["macos", "linux"] | None]
    """
    The stage machine's OS (`sys_info` `os`). Default: the notes for every OS.
    """


class TasksListArgs(TypedDict):
    machine: NotRequired[str | None]
    """
    Only this machine (name or id). Default: all machines.
    """

