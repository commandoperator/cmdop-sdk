# Generated from cmdop/crates/tools/tools.schema.json (sha256 d9aba5e354666f95, cmdop 0.1.10) by exports/sdk/gen/gen.ts. Do not edit.
# Types by datamodel-code-generator==0.30.2.

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, RootModel


class Geometry(BaseModel):
    """
    How an image's pixels map to the screen. Coordinates an agent sends are pixels of the image
    of the same `display`.
    """

    display: int = Field(..., ge=0)
    image_h: int = Field(..., ge=0)
    image_w: int = Field(..., ge=0)
    origin_x: int
    """
    The image's top-left corner, in screen points of the display.
    """
    origin_y: int
    scale: float
    """
    Screen points one image pixel covers (above 1 when the image was shrunk).
    """


class Image(BaseModel):
    """
    A picture. `data` is base64 of the encoded bytes.
    """

    data: str
    """
    Base64 of the encoded image.
    """
    format: str
    """
    `png` (the only one now).
    """
    height: int = Field(..., ge=0)
    width: int = Field(..., ge=0)


class Observation(BaseModel):
    """
    The state after an action, as asked with `observe`.
    """

    geometry: Geometry | None = None
    image: Image | None = None
    ui: str | None = None


class AppOpenOut(BaseModel):
    """
    What every input tool answers. `dispatched` means the event reached the OS, not that the app
    did what the agent hoped: look (`observe`, or a capture) to know.
    """

    audit_id: str
    """
    Id of the audit line on the machine.
    """
    dispatched: bool
    foreground_changed: bool
    """
    The frontmost app or window changed because of the action.
    """
    observation: Observation | None = None
    settled_ms: int = Field(..., ge=0)
    """
    How long the screen took to go quiet after the action, in milliseconds.
    """


class ControlReleaseOut(BaseModel):
    released: bool
    """
    A lease was held and is given back.
    """


class ExecRunOut(BaseModel):
    cancelled: bool
    """
    Stopped because the call was cancelled.
    """
    duration_ms: int = Field(..., ge=0)
    exit_code: int | None = None
    """
    Exit code; absent when the command was ended by a signal.
    """
    signal: int | None = None
    """
    The signal that ended it (Unix).
    """
    stderr: str
    """
    The end of standard error, at most 64 KiB.
    """
    stderr_file: str | None = None
    """
    When stderr was longer than 64 KiB: a file on the machine with all of it (up to 100 MiB),
    readable with `fs_read`.
    """
    stdout: str
    """
    The end of standard output, at most 64 KiB, as text (invalid UTF-8 replaced).
    """
    stdout_file: str | None = None
    """
    When stdout was longer than 64 KiB: a file on the machine with all of it (up to 100 MiB),
    readable with `fs_read`.
    """
    timed_out: bool
    """
    Stopped because it ran longer than `timeout_secs`.
    """
    truncated: bool
    """
    Output was longer than what is returned; the whole of it is in the files below.
    """


class FsDeleteOut(BaseModel):
    path: str
    trashed_to: str | None = None
    """
    Where it went in the trash; absent when removed for good.
    """


class FsEditOut(BaseModel):
    path: str
    replaced: int = Field(..., ge=0)
    """
    Occurrences replaced.
    """
    sha256: str
    """
    SHA-256 of the new content.
    """
    size: int = Field(..., ge=0)


class FsReadOut(BaseModel):
    data: str
    encoding: Literal["utf8", "base64"] = Field(..., title="Encoding")
    """
    `utf8` when `data` is the text itself, `base64` when the bytes are not valid UTF-8.
    """
    offset: int = Field(..., ge=0)
    path: str
    """
    The file, resolved to an absolute path.
    """
    size: int = Field(..., ge=0)
    """
    The file's whole size in bytes.
    """
    truncated: bool
    """
    The file goes on after what was returned; read again with a larger offset.
    """


class SearchMatch(BaseModel):
    kind: Literal["file", "dir", "symlink", "other"] = Field(..., title="EntryKind")
    line: int | None = Field(None, ge=0)
    """
    With `content`: the first matching line's number, from 1.
    """
    path: str
    """
    Absolute path.
    """
    size: int = Field(..., ge=0)
    text: str | None = None
    """
    With `content`: that line, cut to 300 characters.
    """


class FsSearchOut(BaseModel):
    matches: list[SearchMatch]
    root: str
    """
    The root, resolved to an absolute path.
    """
    scanned: int = Field(..., ge=0)
    """
    Files looked at.
    """
    truncated: bool
    """
    Stopped early: the limit, the time cap (20 s) or the file count cap was reached.
    """


class FsStatOut(BaseModel):
    created: int | None = Field(None, ge=0)
    """
    Unix seconds, where the file system keeps it.
    """
    kind: Literal["file", "dir", "symlink", "other"] = Field(..., title="EntryKind")
    link_target: str | None = None
    """
    When `path` itself is a symlink: where it points.
    """
    mode: str | None = None
    """
    Permission bits in octal, for example `644`.
    """
    modified: int | None = Field(None, ge=0)
    """
    Unix seconds.
    """
    path: str
    """
    Resolved absolute path (symlinks followed).
    """
    sha256: str | None = None
    """
    Lower-case hex, when `hash` was asked and the path is a file of at most 64 MiB.
    """
    size: int = Field(..., ge=0)
    """
    Bytes; 0 for folders.
    """
    writable: bool
    """
    Whether the user the machine program runs as may write it.
    """


class FsWriteOut(BaseModel):
    created: bool
    """
    The file did not exist before.
    """
    path: str
    """
    The file, as an absolute path.
    """
    sha256: str
    """
    SHA-256 of the new content.
    """
    size: int = Field(..., ge=0)
    """
    Bytes written.
    """


class JournalSearchOut(BaseModel):
    events: list
    """
    Journal lines, oldest first; `t` is unix milliseconds. `call` lines: `tool`, `author`,
    `task`, `sealed`, `args` as the journal keeps them (paths, command lines and flags in clear,
    other values as length and hash), `outcome`, `ms`. `task` lines: `event` `start` (`pid`,
    `argv`, `cwd`) or `end` (`code`, `signal`), with the `author` of their `task_start` when it
    is still in the journal. `hidden` names what this caller may not see.
    """
    more: bool
    """
    The answer stopped at its limit or size: older matching lines may exist.
    """


class KeyPressOut(BaseModel):
    """
    What every input tool answers. `dispatched` means the event reached the OS, not that the app
    did what the agent hoped: look (`observe`, or a capture) to know.
    """

    audit_id: str
    """
    Id of the audit line on the machine.
    """
    dispatched: bool
    foreground_changed: bool
    """
    The frontmost app or window changed because of the action.
    """
    observation: Observation | None = None
    settled_ms: int = Field(..., ge=0)
    """
    How long the screen took to go quiet after the action, in milliseconds.
    """


class PointerClickOut(BaseModel):
    """
    What every input tool answers. `dispatched` means the event reached the OS, not that the app
    did what the agent hoped: look (`observe`, or a capture) to know.
    """

    audit_id: str
    """
    Id of the audit line on the machine.
    """
    dispatched: bool
    foreground_changed: bool
    """
    The frontmost app or window changed because of the action.
    """
    observation: Observation | None = None
    settled_ms: int = Field(..., ge=0)
    """
    How long the screen took to go quiet after the action, in milliseconds.
    """


class PointerDragOut(BaseModel):
    """
    What every input tool answers. `dispatched` means the event reached the OS, not that the app
    did what the agent hoped: look (`observe`, or a capture) to know.
    """

    audit_id: str
    """
    Id of the audit line on the machine.
    """
    dispatched: bool
    foreground_changed: bool
    """
    The frontmost app or window changed because of the action.
    """
    observation: Observation | None = None
    settled_ms: int = Field(..., ge=0)
    """
    How long the screen took to go quiet after the action, in milliseconds.
    """


class PointerMoveOut(BaseModel):
    """
    What every input tool answers. `dispatched` means the event reached the OS, not that the app
    did what the agent hoped: look (`observe`, or a capture) to know.
    """

    audit_id: str
    """
    Id of the audit line on the machine.
    """
    dispatched: bool
    foreground_changed: bool
    """
    The frontmost app or window changed because of the action.
    """
    observation: Observation | None = None
    settled_ms: int = Field(..., ge=0)
    """
    How long the screen took to go quiet after the action, in milliseconds.
    """


class PointerScrollOut(BaseModel):
    """
    What every input tool answers. `dispatched` means the event reached the OS, not that the app
    did what the agent hoped: look (`observe`, or a capture) to know.
    """

    audit_id: str
    """
    Id of the audit line on the machine.
    """
    dispatched: bool
    foreground_changed: bool
    """
    The frontmost app or window changed because of the action.
    """
    observation: Observation | None = None
    settled_ms: int = Field(..., ge=0)
    """
    How long the screen took to go quiet after the action, in milliseconds.
    """


class ProcKillOut(BaseModel):
    exited: bool
    """
    The process was gone within `wait_secs`.
    """
    pid: int = Field(..., ge=0)
    signal: Literal["term", "int", "hup", "kill"] = Field(..., title="KillSignal")


class Proc(BaseModel):
    argv: list[str]
    """
    Program and arguments, each cut to a sane length.
    """
    author: str
    """
    `agent:claude-code`, `agent:codex`, or `user` (started from a shell, not by an agent).
    """
    cwd: str | None = None
    pid: int = Field(..., ge=0)
    ppid: int | None = Field(None, ge=0)
    started: int = Field(..., ge=0)
    """
    Unix seconds.
    """


class ProcListOut(BaseModel):
    others: int = Field(..., ge=0)
    """
    The user's other processes, not listed (system helpers, or over the list's cap).
    """
    procs: list[Proc]


class ScreenCaptureOut(BaseModel):
    audit_id: str
    """
    Id of the audit line (and of the saved copy) on the machine.
    """
    geometry: Geometry
    image: Image


class DisplayInfo(BaseModel):
    height: int = Field(..., ge=0)
    id: int = Field(..., ge=0)
    name: str | None = None
    primary: bool
    scale: float
    """
    Physical pixels per point (2.0 on a Retina display).
    """
    width: int = Field(..., ge=0)
    """
    Size in screen points.
    """
    x: int
    y: int


class Permissions(BaseModel):
    accessibility: str
    screen_capture: str
    """
    `granted`, `denied`, `unknown` or `not_needed`.
    """


class Point(BaseModel):
    """
    A point in image pixels.
    """

    x: int
    y: int


class ScreenInfoOut(BaseModel):
    backend: str
    """
    Which backend runs here: `x11`, `macos`.
    """
    control_paused: bool
    """
    The owner paused control on this machine.
    """
    cursor: Point | None = None
    displays: list[DisplayInfo]
    frontmost_app: str | None = None
    locked: bool
    """
    The screen is locked or asleep: captures and input will fail with `screen_locked`.
    """
    permissions: Permissions


class Disk(BaseModel):
    available: int = Field(..., ge=0)
    mount: str
    total: int = Field(..., ge=0)


class SysInfoOut(BaseModel):
    arch: str
    """
    `aarch64`, `x86_64`.
    """
    cpus: int = Field(..., ge=0)
    disks: list[Disk]
    """
    Mounted file systems with their space, in bytes.
    """
    home: str | None = None
    hostname: str
    kernel: str | None = None
    memory_available: int = Field(..., ge=0)
    memory_total: int = Field(..., ge=0)
    os: str
    """
    `macos`, `linux`, `windows`.
    """
    os_version: str | None = None
    """
    OS release, for example `15.5` or `Ubuntu 24.04`.
    """
    uptime: int = Field(..., ge=0)
    """
    Seconds since boot.
    """
    user: str | None = None
    """
    The user the machine program runs as.
    """


class TaskOutputOut(BaseModel):
    running: bool
    """
    False once the task has ended.
    """
    task: int = Field(..., ge=0)
    text: str
    """
    The terminal's screen and recent scrollback as text, terminal codes applied.
    """


class TaskStartOut(BaseModel):
    pid: int = Field(..., ge=0)
    task: int = Field(..., ge=0)
    """
    The task's id: pass it to `task_output` and `task_stop`.
    """


class TaskStopOut(BaseModel):
    stopping: bool
    """
    The stop was sent; the ending arrives a moment later (`tasks_list`, `history_search`).
    """
    task: int = Field(..., ge=0)


class TextTypeOut(BaseModel):
    """
    What every input tool answers. `dispatched` means the event reached the OS, not that the app
    did what the agent hoped: look (`observe`, or a capture) to know.
    """

    audit_id: str
    """
    Id of the audit line on the machine.
    """
    dispatched: bool
    foreground_changed: bool
    """
    The frontmost app or window changed because of the action.
    """
    observation: Observation | None = None
    settled_ms: int = Field(..., ge=0)
    """
    How long the screen took to go quiet after the action, in milliseconds.
    """


class UiActOut(BaseModel):
    """
    What every input tool answers. `dispatched` means the event reached the OS, not that the app
    did what the agent hoped: look (`observe`, or a capture) to know.
    """

    audit_id: str
    """
    Id of the audit line on the machine.
    """
    dispatched: bool
    foreground_changed: bool
    """
    The frontmost app or window changed because of the action.
    """
    observation: Observation | None = None
    settled_ms: int = Field(..., ge=0)
    """
    How long the screen took to go quiet after the action, in milliseconds.
    """


class UiSnapshotOut(BaseModel):
    elements: int = Field(..., ge=0)
    snapshot: str
    """
    Valid until the next snapshot; element ids belong to it.
    """
    text: str
    """
    The tree as indented text, one element per line: `[id] role "name" value (state)`.
    """
    truncated: str | None = None
    """
    `depth`, `max_elements` or `time` when a limit cut the tree; absent when complete.
    """
    window: int | None = Field(None, ge=0)


class UiWaitOut(BaseModel):
    met: bool
    """
    The condition held before the timeout.
    """
    waited_ms: int = Field(..., ge=0)


class WindowInfo(BaseModel):
    app: str
    consent: str
    """
    What `control` may do here: `allowed`, `ask` (not on the owner's list) or `denied`.
    """
    display: int | None = Field(None, ge=0)
    focused: bool
    h: int = Field(..., ge=0)
    id: int = Field(..., ge=0)
    on_screen: bool
    title: str
    w: int = Field(..., ge=0)
    x: int
    """
    Bounds in screen points.
    """
    y: int


class WindowListOut(BaseModel):
    truncated: bool
    windows: list[WindowInfo]


class Entry(BaseModel):
    kind: Literal["file", "dir", "symlink", "other"] = Field(..., title="EntryKind")
    modified: int | None = Field(None, ge=0)
    """
    Unix seconds.
    """
    name: str
    size: int = Field(..., ge=0)
    """
    Bytes; 0 for folders.
    """


class FsListOut(BaseModel):
    entries: list[Entry]
    path: str
    """
    The folder, resolved to an absolute path.
    """
    truncated: bool
    """
    More entries exist than were returned.
    """

