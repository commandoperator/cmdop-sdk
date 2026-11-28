# Generated from cmdop/crates/tools/tools.schema.json (sha256 cef76f12c6264508, cmdop 0.1.16) by exports/sdk/gen/gen.ts. Do not edit.
# Types by datamodel-code-generator==0.30.2.

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, RootModel


class CallView(BaseModel):
    author: str
    id: int
    machine: str
    machine_name: str
    ms: int | None = Field(None, ge=0)
    outcome: str | None = None
    """
    `ok`, an error code, `cancelled` (the caller went away first) or `interrupted` (the
    server stopped first); none while it runs.
    """
    refused: bool
    """
    The caller was refused (the grant, an OS permission or the app list said no), as opposed
    to the tool failing.
    """
    sealed: bool
    """
    Sealed end to end: the server never saw its arguments or answer. False for MCP
    and the page, whose calls pass through the server in clear.
    """
    started: int = Field(..., ge=0)
    task: int | None = None
    """
    The task the call started (`task_start`) or named (a plain `task_output` / `task_stop`);
    none for other tools and for a sealed call that names a task.
    """
    token: int
    """
    The token that made the call: an agent's id on `/api/agents`, or the owner's token.
    """
    tool: str


class DockRunView(BaseModel):
    """
    A run of the owner's agent dock on that machine (persistent context S4), from the app's
    `dock.log`: start, stop and exit only, never keystrokes or output.
    """

    ended: int | None = Field(None, ge=0)
    """
    Unix milliseconds; absent while it runs, or when the app quit first (`exit` is `lost`).
    """
    exit: str | None = None
    """
    The exit code, `signal`, or `lost`.
    """
    started: int = Field(..., ge=0)
    """
    Unix milliseconds.
    """


class SessionView(BaseModel):
    """
    A kept vendor session file, or a run of the agent dock (`dock` set), as history shows it.
    """

    author: str
    cwd: str | None = None
    dock: DockRunView | None = None
    """
    Set when this row is a dock run, not a vendor file.
    """
    gone: bool
    kept: bool
    machine: str
    machine_name: str
    modified: int = Field(..., ge=0)
    path: str
    session: str
    size: int = Field(..., ge=0)
    vendor: str


class Activity(BaseModel):
    calls: int = Field(..., ge=0)
    """
    Tool calls the server could read made to it since `since`; calls from a paired client,
    encrypted end to end, are not counted.
    """
    since: int = Field(..., ge=0)
    """
    Unix seconds.
    """
    tasks: int = Field(..., ge=0)
    """
    Tasks started on the machine since `since`.
    """


class ProcView(BaseModel):
    """
    A process cmdop did not start, with who did.
    """

    argv: list[str]
    author: str
    cwd: str | None = None
    machine: str
    machine_name: str
    pid: int = Field(..., ge=0)
    started: int = Field(..., ge=0)


class ShownTask(BaseModel):
    """
    A task as the caller may see it.
    """

    argv: list[str] | None = None
    author: str
    code: int | None = None
    created: int = Field(..., ge=0)
    cwd: str | None = None
    ended: int | None = Field(None, ge=0)
    error: str | None = None
    hidden: str | None = None
    id: int
    machine: str
    machine_name: str
    pid: int | None = None
    sealed: bool
    """
    Started by a call from a paired client, encrypted end to end: the server never saw the
    command, so `argv` is empty.
    """
    signal: int | None = None
    state: Literal["running", "starting", "ended", "failed", "lost"] = Field(
        ..., title="TaskState"
    )
    """
    Where a task is in its life. The store keeps it as text (`cmdop-store` writes only these five).
    `starting`: Recorded; the machine has not said it started.
    `ended`: Exited: `code` or `signal` says how.
    `failed`: Did not start: `error` says why.
    `lost`: The machine went away while it ran; it may come back as `running`.
    """


class HistorySearchOut(BaseModel):
    """
    What `history_search` returns: each kind asked for, and only those.
    """

    calls: list[CallView] | None = None
    """
    Only calls the server could read: calls from a paired client, encrypted end to end, are
    left out.
    """
    sessions: list[SessionView] | None = None
    """
    Absent when `task` was given: a task has no sessions.
    """
    tasks: list[ShownTask] | None = None


class MachineRow(BaseModel):
    """
    One row of `machines_list`: the machine as `/api/v1/machines` shows it, and its activity.
    """

    activity: Activity | None = None
    """
    The last 7 days' counts; absent when the server's store could not count them.
    """
    arch: str
    behind: bool | None = None
    """
    Whether a newer CMDOP release than `program` is published. Null when this server cannot
    say (it does not follow releases, as a self-hosted server may not) or `program` is not a
    release version.
    """
    box_key: str | None = None
    """
    The machine's key for sealed calls. A client trusts it only with `box_sig`, checked
    against the machine id it pinned.
    """
    box_sig: str | None = None
    commit: str | None = None
    """
    The commit its program was built from (12 hex digits), as it said on its current or last
    link since the server started; null from an older program or before it dialled in.
    """
    dirty: bool
    """
    Its program had changes not in `commit` (a developer's build). Not required in the
    document, so a client also reads a row from an older server, which sends none.
    """
    epoch: int = Field(..., ge=0)
    id: str
    label: str | None = None
    """
    The name its owner gave it on the page; null when none, and `name` is `own_name`.
    """
    last_seen: int = Field(..., ge=0)
    """
    Unix seconds of the last message from the machine.
    """
    name: str
    """
    What to call it: the name its owner gave it on the page, else the machine's own.
    """
    newest_release: str | None = None
    """
    The newest published CMDOP release this server knows, `0.1.10`; null when it knows none.
    The same on every row.
    """
    online: bool
    """
    It has a live link (it may still be `stale` or `paused`; `state` says whether it can
    take a call).
    """
    os: str
    own_name: str
    """
    The name the machine gives itself (`machine.json` `name`), from its last `Hello`.
    """
    paused: bool | None = None
    """
    Whether its owner paused it (no tool runs there), as the machine reported on its live
    link; null while it is offline, or when its program is too old to report.
    """
    program: str
    since: int = Field(..., ge=0)
    """
    Unix seconds: when the current link came up, or when the machine was last seen.
    """
    state: Literal["online", "stale", "offline", "paused"] = Field(
        ..., title="Presence"
    )
    """
    Whether it can take a call now: `online`, `stale`, `offline` or `paused`. Only `online`
    takes calls; for any other, tell the user instead of retrying.
    """
    tools: list[str]
    """
    Tools the machine runs, as it announced them on its current or last link.
    """
    unpaired_risks: list[str] | None = None
    """
    Risk classes a call from the page or MCP may use on this machine: what its own ceiling
    allows, which no agent's grant can exceed. As the machine reported on its live link; null
    while it is offline, or when its program is too old to report.
    """


class Picture(BaseModel):
    """
    One machine's picture, or why there is none.
    """

    error: str | None = None
    machine: str
    machine_name: str
    others: int = Field(..., ge=0)
    """
    Processes of "the machine itself" (apps, daemons), only counted.
    """
    procs: list[ProcView]


class TasksListOut(BaseModel):
    """
    What `tasks_list` returns.
    """

    outside: list[Picture]
    """
    Other processes on each online machine (`proc_list` there), by who started them.
    """
    tasks: list[ShownTask]
    """
    Tasks started through cmdop that still run.
    """

