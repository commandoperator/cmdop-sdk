# Generated from cmdop/crates/tools/tools.schema.json (sha256 6e1a72817fe1ae37, cmdop 0.1.13) by exports/sdk/gen/gen.ts. Do not edit.
# Types by datamodel-code-generator==0.30.2.

from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired


class AgentCancelArgs(TypedDict):
    task: int
    """
    The `task` of an `agent_prompt` answer.
    """


class AgentListArgs(TypedDict):
    """
    No arguments.
    """


class AgentPromptArgs(TypedDict):
    agent: NotRequired[str | None]
    """
    Catalog id from `agent_list`. Absent: the machine's default agent.
    """
    cwd: NotRequired[str | None]
    """
    Folder the agent works in. Absent: the agent's own folder on the machine, the same for
    every prompt, so a `session` continues there.
    """
    prompt: str
    """
    What to ask, at most 16 KiB. The agent reads it as an instruction.
    """
    session: NotRequired[str | None]
    """
    A `session` from an earlier answer, to continue that conversation.
    """
    tier: NotRequired[Literal["text_only", "read_only"] | None]
    """
    Ask for less than the machine allows; never more.
    """
    wait_secs: NotRequired[int | None]
    """
    Seconds to wait for the answer (default 50, at most 240). A run still going then keeps
    going: follow it with `task_output` on `task`.
    """


class AgentSessionsArgs(TypedDict):
    agent: NotRequired[str | None]
    """
    Catalog id. Absent: every agent `agent_list` shows.
    """
    limit: NotRequired[int | None]
    """
    At most this many, newest first (default 20, at most 200).
    """


class AppOpenArgs(TypedDict):
    app: NotRequired[str | None]
    """
    App name or bundle id. Must be allowed for `control`.
    """
    background: NotRequired[bool]
    """
    Do not bring it to the front (default true).
    """
    observe: NotRequired[Literal["none", "ui", "image"]]
    """
    What an input call returns next to `dispatched`, when asked with `observe`.
    `none`: Nothing more.
    `ui`: The accessibility tree of the frontmost window, as `ui_snapshot` gives it.
    `image`: A fresh screenshot of the display the action touched.
    """
    path: NotRequired[str | None]
    """
    A file or folder to open (with `app`, in that app).
    """


class ControlReleaseArgs(TypedDict):
    """
    No arguments.
    """


class DiskCleanArgs(TypedDict):
    dry_run: NotRequired[bool]
    """
    Say what would be removed and remove nothing.
    """
    older_than_days: NotRequired[int | None]
    """
    Remove only files unchanged for at least this many days. It can only raise an item's own
    age.
    """
    targets: NotRequired[list[str]]
    """
    As in `disk_usage`: `agent:<id>` or `cache:<id>`. Absent: every one known.
    """


class DiskUsageArgs(TypedDict):
    older_than_days: NotRequired[int | None]
    """
    Count only files unchanged for at least this many days. It can only raise an item's own
    age.
    """
    targets: NotRequired[list[str]]
    """
    `agent:<id>` for one agent's own files (`agent:claude-code`), `cache:<id>` for a developer
    cache no agent owns (`cache:cargo`, `cache:npm`, `cache:pnpm`). Absent: every one known.
    """


class ExecRunArgs(TypedDict):
    argv: NotRequired[list[str]]
    """
    Program and arguments, run directly without a shell. Give this or `command`.
    """
    command: NotRequired[str | None]
    """
    A shell command line, run as `/bin/sh -c <command>`. Give this or `argv`.
    """
    cwd: NotRequired[str | None]
    """
    Working folder. Default: the user's home folder.
    """
    env: NotRequired[dict[str, str]]
    """
    Extra environment variables for this command. It gets these and a small base (PATH, HOME,
    USER, SHELL, the locale, the desktop session); nothing else of cmdop's own environment.
    """
    stdin: NotRequired[str | None]
    """
    Text written to the command's standard input, then closed. Default: no input.
    """
    timeout_secs: NotRequired[int | None]
    """
    Seconds before the command and its whole process group are stopped (default 120, at most
    600). Long work goes to `task_start`.
    """


class FsDeleteArgs(TypedDict):
    path: str
    """
    File or folder on the machine. Absolute, or relative to the user's home folder. The home
    folder, the file system root and the machine's allowed roots themselves are refused.
    """
    permanent: NotRequired[bool]
    """
    Remove for good instead of moving to the trash (macOS ~/.Trash, Linux the freedesktop
    trash). Only where the trash cannot take it.
    """
    recursive: NotRequired[bool]
    """
    Allow a folder that is not empty.
    """


class FsEditArgs(TypedDict):
    expect_sha256: NotRequired[str | None]
    """
    Refuse unless the file's SHA-256 is this: from `fs_stat` with hash=true, or the sha256 the
    last write of it returned.
    """
    new: str
    """
    What replaces it.
    """
    old: str
    """
    The exact text to replace, whitespace included; no regular expressions, no fuzzy matching.
    Must occur once, unless `replace_all`.
    """
    path: str
    """
    Text file on the machine. Absolute, or relative to the user's home folder.
    """
    replace_all: NotRequired[bool]
    """
    Replace every occurrence instead of exactly one.
    """


class FsListArgs(TypedDict):
    hidden: NotRequired[bool]
    """
    Include names starting with a dot.
    """
    limit: NotRequired[int | None]
    """
    At most this many entries (default 500, at most 5000), sorted by name.
    """
    path: str
    """
    Folder on the machine. Absolute, or relative to the user's home folder; `~` is the home.
    """


class FsReadArgs(TypedDict):
    max_bytes: NotRequired[int | None]
    """
    Read at most this many bytes (default 262144, at most 4194304).
    """
    offset: NotRequired[int | None]
    """
    Start at this byte (default 0).
    """
    path: str
    """
    File on the machine. Absolute, or relative to the user's home folder; `~` is the home.
    """


class FsSearchArgs(TypedDict):
    content: NotRequired[str | None]
    """
    Text to find inside files (plain text, not a regular expression). Files over 4 MiB and
    files that are not text are skipped. Default: match by name only.
    """
    hidden: NotRequired[bool]
    """
    Also enter and match names starting with a dot.
    """
    ignore_case: NotRequired[bool]
    """
    Compare `name` and `content` ignoring letter case.
    """
    limit: NotRequired[int | None]
    """
    At most this many matches (default 200, at most 2000).
    """
    max_depth: NotRequired[int | None]
    """
    Folder levels below `root` to enter (default 12, at most 64).
    """
    name: NotRequired[str | None]
    """
    File name pattern with `*` and `?`, matched against the name only, for example `*.rs`.
    Default: every name.
    """
    root: str
    """
    Folder to search under. Absolute, or relative to the user's home folder. Symlinks are not
    followed; folders holding keys and credentials are skipped.
    """


class FsStatArgs(TypedDict):
    hash: NotRequired[bool]
    """
    Also return the file's SHA-256 (files up to 64 MiB). Pass it as `expect_sha256` to
    `fs_write` or `fs_edit` to refuse a write when the file changed in between.
    """
    path: str
    """
    File or folder on the machine. Absolute, or relative to the user's home folder.
    """


class FsWriteArgs(TypedDict):
    create_only: NotRequired[bool]
    """
    Refuse when the file already exists.
    """
    data: str
    """
    The whole new content.
    """
    encoding: NotRequired[Literal["utf8", "base64"] | None]
    """
    How `data` is written: `utf8` (default) or `base64`.
    """
    expect_sha256: NotRequired[str | None]
    """
    The file's SHA-256 from `fs_stat` with hash=true, or as the last `fs_write` or `fs_edit` of it
    returned. Required to replace an existing file; the write is refused when the file changed since or does not exist.
    """
    mkdirs: NotRequired[bool]
    """
    Create missing parent folders.
    """
    path: str
    """
    File on the machine. Absolute, or relative to the user's home folder. An existing file
    keeps its permissions.
    """


class JournalSearchArgs(TypedDict):
    author: NotRequired[str | None]
    """
    Author or its start: `owner`, `agent:` (every agent), `agent:<name>`. A task's lines match
    through the `task_start` call that began it.
    """
    kind: NotRequired[Literal["call", "task"] | None]
    """
    Only calls or only task lines. Default: both.
    """
    limit: NotRequired[int | None]
    """
    At most this many lines, the newest (default 100, at most 500).
    """
    since: NotRequired[int | None]
    """
    At or after this time, unix seconds.
    """
    task: NotRequired[int | None]
    """
    Only the lines of this task (the server's task id).
    """
    text: NotRequired[str | None]
    """
    Text, any case, in what this caller may see of a line: the tool, the outcome, the
    arguments, a task's command and folder.
    """
    tool: NotRequired[str | None]
    """
    Only calls of this tool.
    """
    until: NotRequired[int | None]
    """
    Before this time, unix seconds. The next older page: the oldest line's `t` / 1000, plus 1
    (lines of that second may repeat).
    """


class KeyPressArgs(TypedDict):
    hold_ms: NotRequired[int | None]
    """
    Hold the key this long, in ms (at most 5000).
    """
    key: str
    """
    A key name: `a`, `Enter`, `Tab`, `Escape`, `ArrowDown`, `F5`, `Space`. One key; the
    modifiers go in `modifiers`, never as `"ctrl+s"`.
    """
    modifiers: NotRequired[list[Literal["shift", "ctrl", "alt", "meta"]]]
    observe: NotRequired[Literal["none", "ui", "image"]]
    """
    What an input call returns next to `dispatched`, when asked with `observe`.
    `none`: Nothing more.
    `ui`: The accessibility tree of the frontmost window, as `ui_snapshot` gives it.
    `image`: A fresh screenshot of the display the action touched.
    """
    repeat: NotRequired[int | None]
    """
    Press this many times (default 1, at most 100).
    """


class PointerClickArgs(TypedDict):
    """
    Where a pointer action lands: an element from `ui_snapshot`, or image pixels.
    """

    button: NotRequired[Literal["left", "right", "middle"]]
    count: NotRequired[int | None]
    """
    1 click, 2 double, 3 triple (default 1).
    """
    display: NotRequired[int | None]
    """
    Display the pixel belongs to (default: the one last captured).
    """
    element: NotRequired[str | None]
    """
    An element id from the latest `ui_snapshot`. Preferred; a stale id is `element_gone`.
    """
    hold_ms: NotRequired[int | None]
    """
    Hold the button this long before release, in ms (at most 5000).
    """
    modifiers: NotRequired[list[Literal["shift", "ctrl", "alt", "meta"]]]
    """
    Keys held during the click.
    """
    observe: NotRequired[Literal["none", "ui", "image"]]
    """
    What an input call returns next to `dispatched`, when asked with `observe`.
    `none`: Nothing more.
    `ui`: The accessibility tree of the frontmost window, as `ui_snapshot` gives it.
    `image`: A fresh screenshot of the display the action touched.
    """
    x: NotRequired[int | None]
    """
    Image pixel, with `y`. Needs a `screen_capture` of the display first.
    """
    y: NotRequired[int | None]


class Point(TypedDict):
    """
    A point in image pixels.
    """

    x: int
    y: int


class PointerDragArgs(TypedDict):
    button: NotRequired[Literal["left", "right", "middle"]]
    display: NotRequired[int | None]
    duration_ms: NotRequired[int | None]
    """
    Total time of the drag (default 400, at most 10000).
    """
    from_element: NotRequired[str | None]
    """
    Or two elements: from and to.
    """
    modifiers: NotRequired[list[Literal["shift", "ctrl", "alt", "meta"]]]
    observe: NotRequired[Literal["none", "ui", "image"]]
    """
    What an input call returns next to `dispatched`, when asked with `observe`.
    `none`: Nothing more.
    `ui`: The accessibility tree of the frontmost window, as `ui_snapshot` gives it.
    `image`: A fresh screenshot of the display the action touched.
    """
    path: NotRequired[list[Point]]
    """
    Points to follow, in image pixels, at least two. The button goes down at the first and
    up at the last.
    """
    to_element: NotRequired[str | None]


class PointerMoveArgs(TypedDict):
    """
    Where a pointer action lands: an element from `ui_snapshot`, or image pixels.
    """

    display: NotRequired[int | None]
    """
    Display the pixel belongs to (default: the one last captured).
    """
    element: NotRequired[str | None]
    """
    An element id from the latest `ui_snapshot`. Preferred; a stale id is `element_gone`.
    """
    observe: NotRequired[Literal["none", "ui", "image"]]
    """
    What an input call returns next to `dispatched`, when asked with `observe`.
    `none`: Nothing more.
    `ui`: The accessibility tree of the frontmost window, as `ui_snapshot` gives it.
    `image`: A fresh screenshot of the display the action touched.
    """
    x: NotRequired[int | None]
    """
    Image pixel, with `y`. Needs a `screen_capture` of the display first.
    """
    y: NotRequired[int | None]


class PointerScrollArgs(TypedDict):
    """
    Where a pointer action lands: an element from `ui_snapshot`, or image pixels.
    """

    display: NotRequired[int | None]
    """
    Display the pixel belongs to (default: the one last captured).
    """
    dx: NotRequired[int]
    """
    Lines to the right (negative: left), -10..10.
    """
    dy: NotRequired[int]
    """
    Lines down (negative: up), -10..10.
    """
    element: NotRequired[str | None]
    """
    An element id from the latest `ui_snapshot`. Preferred; a stale id is `element_gone`.
    """
    observe: NotRequired[Literal["none", "ui", "image"]]
    """
    What an input call returns next to `dispatched`, when asked with `observe`.
    `none`: Nothing more.
    `ui`: The accessibility tree of the frontmost window, as `ui_snapshot` gives it.
    `image`: A fresh screenshot of the display the action touched.
    """
    x: NotRequired[int | None]
    """
    Image pixel, with `y`. Needs a `screen_capture` of the display first.
    """
    y: NotRequired[int | None]


class ProcKillArgs(TypedDict):
    pid: int
    signal: NotRequired[Literal["term", "int", "hup", "kill"] | None]
    """
    `term` (default), `int`, `hup` or `kill`.
    """
    wait_secs: NotRequired[int | None]
    """
    Seconds to wait for the process to end (default 3, at most 30).
    """


class ProcListArgs(TypedDict):
    filter: NotRequired[str | None]
    """
    Only processes whose program name or command line contains this text.
    """


class Region(TypedDict):
    """
    A rectangle in image pixels.
    """

    h: int
    w: int
    x: int
    y: int


class ScreenCaptureArgs(TypedDict):
    cursor: NotRequired[bool]
    """
    Draw the cursor into the image.
    """
    display: NotRequired[int | None]
    """
    Display id from `screen_info` (default: the primary one).
    """
    max_edge: NotRequired[int | None]
    """
    Longest side of the image in pixels (default 1280, at most 2000; a larger value is
    lowered to 2000, the most an agent client shows unscaled).
    """
    region: NotRequired[Region | None]
    """
    Zoom: only this rectangle, in pixels of the latest capture of the display. The answer is
    not shrunk, so small text becomes readable.
    """
    window: NotRequired[int | None]
    """
    Capture one window (id from `window_list`) instead of the display.
    """


class ScreenInfoArgs(TypedDict):
    """
    No arguments.
    """


class SysInfoArgs(TypedDict):
    """
    No arguments.
    """


class TaskOutputArgs(TypedDict):
    lines: NotRequired[int | None]
    """
    Return only the last this many lines (default 200, 0 for all the machine keeps).
    """
    task: int
    """
    Task id, as `task_start` or `tasks_list` returned it.
    """


class TaskStartArgs(TypedDict):
    argv: NotRequired[list[str]]
    """
    Program and arguments, run directly without a shell. Give this or `command`.
    """
    cols: NotRequired[int | None]
    """
    Terminal width (default 120).
    """
    command: NotRequired[str | None]
    """
    A shell command line, run as `/bin/sh -c <command>` in the terminal. Give this or `argv`.
    """
    cwd: NotRequired[str | None]
    """
    Working folder. Default: the machine program's folder.
    """
    rows: NotRequired[int | None]
    """
    Terminal height (default 40).
    """


class TaskStopArgs(TypedDict):
    task: int
    """
    Task id, as `task_start` or `tasks_list` returned it.
    """


class TextTypeArgs(TypedDict):
    method: NotRequired[Literal["auto", "keys", "paste"]]
    """
    `auto`: Pick by the text: keys for plain ASCII, paste otherwise.
    `keys`: Key events, one per character.
    `paste`: Through the clipboard; the clipboard is restored afterwards.
    """
    observe: NotRequired[Literal["none", "ui", "image"]]
    """
    What an input call returns next to `dispatched`, when asked with `observe`.
    `none`: Nothing more.
    `ui`: The accessibility tree of the frontmost window, as `ui_snapshot` gives it.
    `image`: A fresh screenshot of the display the action touched.
    """
    submit: NotRequired[bool]
    """
    Press Enter afterwards.
    """
    text: str
    """
    The text, literally (at most 10 000 characters). Not logged in clear in the audit.
    """


class UiActArgs(TypedDict):
    action: Literal[
        "focus", "toggle", "expand", "collapse", "invoke", "set_value", "select_text"
    ]
    """
    `invoke`: Press, click or activate the element.
    `set_value`: Replace the element's value with `value`.
    `select_text`: Select the element's text.
    """
    element: str
    """
    Element id from the latest `ui_snapshot`.
    """
    observe: NotRequired[Literal["none", "ui", "image"]]
    """
    What an input call returns next to `dispatched`, when asked with `observe`.
    `none`: Nothing more.
    `ui`: The accessibility tree of the frontmost window, as `ui_snapshot` gives it.
    `image`: A fresh screenshot of the display the action touched.
    """
    value: NotRequired[str | None]
    """
    The new value for `set_value`.
    """


class UiSnapshotArgs(TypedDict):
    depth: NotRequired[int | None]
    """
    Tree depth (default 12).
    """
    max_elements: NotRequired[int | None]
    """
    At most this many elements (default 400, at most 3000).
    """
    window: NotRequired[int | None]
    """
    Window id from `window_list` (default: the frontmost window).
    """


class UiWaitArgs(TypedDict):
    timeout_ms: NotRequired[int | None]
    """
    Give up after this long (default 5000, at most 30000).
    """
    until: Literal[
        "element_gone",
        "text_gone",
        "element_appears",
        "text_appears",
        "window_appears",
        "screen_stable",
    ]
    """
    `element_appears`: An element whose name or value contains `value` is there.
    `text_appears`: The text `value` is in the tree.
    `window_appears`: A window of an app whose name contains `value` is on screen.
    `screen_stable`: The screen stopped changing.
    """
    value: NotRequired[str | None]
    """
    What to look for, for the first five conditions.
    """


class WindowListArgs(TypedDict):
    app: NotRequired[str | None]
    """
    Only windows of this app (name or bundle id).
    """

