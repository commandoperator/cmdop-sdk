// Generated from cmdop/crates/tools/tools.schema.json (sha256 cef76f12c6264508, cmdop 0.1.16) by exports/sdk/gen/gen.ts. Do not edit.

/** Arguments of `docs_read`. */
export type DocsReadArgs = {
  /**
   * The page: `guides/connect`, `/guides/connect`, its docs.cmdop.ai address or the `.md`
   * link a page carries. Absent: the contents, every page with its path and title.
   */
  path?: string | null;
};

/** What `docs_read` returns. */
export type DocsReadOut = string;

/** Arguments of `history_search`. */
export type HistorySearchArgs = {
  /** Author or its start: `owner`, `agent:` (every agent), `agent:<name>`. */
  author?: string | null;
  /** What to return. Default: tasks, sessions and calls. */
  kind?: HistoryKind[] | null;
  /** At most this many of each kind, newest first (default 50, at most 200). */
  limit?: number | null;
  /** Only this machine (name or id). */
  machine?: string | null;
  /** Started (sessions: last changed) at or after this time, unix seconds. */
  since?: number | null;
  /** Only this task (its row and the calls that started or named it; no sessions). */
  task?: number | null;
  /**
   * Text, any case. Tasks: the command, the folder or the error (another author's only for an
   * agent granted exec). Sessions: path, id, folder. Calls: the tool name.
   */
  text?: string | null;
  /** Started (sessions: last changed) before this time, unix seconds. */
  until?: number | null;
};

/** What `history_search` returns. */
export type HistorySearchOut = {
  /**
   * Only calls the server could read: calls from a paired client, encrypted end to end, are
   * left out.
   */
  calls?: CallView[] | null;
  /** Absent when `task` was given: a task has no sessions. */
  sessions?: SessionView[] | null;
  tasks?: ShownTask[] | null;
};

/** Arguments of `machines_list`. No arguments. */
export type MachinesListArgs = Record<string, never>;

/** What `machines_list` returns. */
export type MachinesListOut = MachineRow[];

/** Arguments of `showtime_guide`. */
export type ShowtimeGuideArgs = {
  /** The language to speak to the user in, e.g. "Russian" or "de". Default: the user's. */
  language?: string | null;
  /** The stage machine's OS (`sys_info` `os`). Default: the notes for every OS. */
  os?: Os | null;
};

/** What `showtime_guide` returns. */
export type ShowtimeGuideOut = string;

/** Arguments of `tasks_list`. */
export type TasksListArgs = {
  /** Only this machine (name or id). Default: all machines. */
  machine?: string | null;
};

/** What `tasks_list` returns. */
export type TasksListOut = {
  /** Other processes on each online machine (`proc_list` there), by who started them. */
  outside: Picture[];
  /** Tasks started through cmdop that still run. */
  tasks: ShownTask[];
};

export type CallView = {
  author: string;
  id: number;
  machine: string;
  machine_name: string;
  ms?: number | null;
  /**
   * `ok`, an error code, `cancelled` (the caller went away first) or `interrupted` (the
   * server stopped first); none while it runs.
   */
  outcome?: string | null;
  /**
   * The caller was refused (the grant, an OS permission or the app list said no), as opposed
   * to the tool failing.
   */
  refused: boolean;
  /**
   * Sealed end to end: the server never saw its arguments or answer. False for MCP
   * and the page, whose calls pass through the server in clear.
   */
  sealed: boolean;
  started: number;
  /**
   * The task the call started (`task_start`) or named (a plain `task_output` / `task_stop`);
   * none for other tools and for a sealed call that names a task.
   */
  task?: number | null;
  /** The token that made the call: an agent's id on `/api/agents`, or the owner's token. */
  token: number;
  tool: string;
};

/** What `history_search` returns. */
export type HistoryKind = "tasks" | "sessions" | "calls";

/** One row of `machines_list`: the machine as `/api/v1/machines` shows it, and its activity. */
export type MachineRow = {
  /** The last 7 days' counts; absent when the server's store could not count them. */
  activity?: Activity | null;
  arch: string;
  /**
   * Whether a newer CMDOP release than `program` is published. Null when this server cannot
   * say (it does not follow releases, as a self-hosted server may not) or `program` is not a
   * release version.
   */
  behind?: boolean | null;
  /**
   * The machine's key for sealed calls. A client trusts it only with `box_sig`, checked
   * against the machine id it pinned.
   */
  box_key?: string | null;
  box_sig?: string | null;
  /**
   * The commit its program was built from (12 hex digits), as it said on its current or last
   * link since the server started; null from an older program or before it dialled in.
   */
  commit?: string | null;
  /**
   * Its program had changes not in `commit` (a developer's build). Not required in the
   * document, so a client also reads a row from an older server, which sends none.
   */
  dirty: boolean;
  epoch: number;
  id: string;
  /** The name its owner gave it on the page; null when none, and `name` is `own_name`. */
  label?: string | null;
  /** Unix seconds of the last message from the machine. */
  last_seen: number;
  /** What to call it: the name its owner gave it on the page, else the machine's own. */
  name: string;
  /**
   * The newest published CMDOP release this server knows, `0.1.10`; null when it knows none.
   * The same on every row.
   */
  newest_release?: string | null;
  /**
   * It has a live link (it may still be `stale` or `paused`; `state` says whether it can
   * take a call).
   */
  online: boolean;
  os: string;
  /** The name the machine gives itself (`machine.json` `name`), from its last `Hello`. */
  own_name: string;
  /**
   * Whether its owner paused it (no tool runs there), as the machine reported on its live
   * link; null while it is offline, or when its program is too old to report.
   */
  paused?: boolean | null;
  program: string;
  /** Unix seconds: when the current link came up, or when the machine was last seen. */
  since: number;
  /**
   * Whether it can take a call now: `online`, `stale`, `offline` or `paused`. Only `online`
   * takes calls; for any other, tell the user instead of retrying.
   */
  state: Presence;
  /** Tools the machine runs, as it announced them on its current or last link. */
  tools: string[];
  /**
   * Risk classes a call from the page or MCP may use on this machine: what its own ceiling
   * allows, which no agent's grant can exceed. As the machine reported on its live link; null
   * while it is offline, or when its program is too old to report.
   */
  unpaired_risks?: string[] | null;
};

/** The operating systems with notes. Windows has none until it has a machine program (V4). */
export type Os = "macos" | "linux";

/** One machine's picture, or why there is none. */
export type Picture = {
  error?: string | null;
  machine: string;
  machine_name: string;
  /** Processes of "the machine itself" (apps, daemons), only counted. */
  others: number;
  procs: ProcView[];
};

/** A kept vendor session file, or a run of the agent dock (`dock` set), as history shows it. */
export type SessionView = {
  author: string;
  cwd?: string | null;
  /** Set when this row is a dock run, not a vendor file. */
  dock?: DockRunView | null;
  gone: boolean;
  kept: boolean;
  machine: string;
  machine_name: string;
  modified: number;
  path: string;
  session: string;
  size: number;
  vendor: string;
};

/** A task as the caller may see it. */
export type ShownTask = {
  argv?: string[];
  author: string;
  code?: number | null;
  created: number;
  cwd?: string | null;
  ended?: number | null;
  error?: string | null;
  hidden?: string | null;
  id: number;
  machine: string;
  machine_name: string;
  pid?: number | null;
  /**
   * Started by a call from a paired client, encrypted end to end: the server never saw the
   * command, so `argv` is empty.
   */
  sealed: boolean;
  signal?: number | null;
  state: TaskState;
};

export type Activity = {
  /**
   * Tool calls the server could read made to it since `since`; calls from a paired client,
   * encrypted end to end, are not counted.
   */
  calls: number;
  /** Unix seconds. */
  since: number;
  /** Tasks started on the machine since `since`. */
  tasks: number;
};

/**
 * A run of the owner's agent dock on that machine (persistent context S4), from the app's
 * `dock.log`: start, stop and exit only, never keystrokes or output.
 */
export type DockRunView = {
  /** Unix milliseconds; absent while it runs, or when the app quit first (`exit` is `lost`). */
  ended?: number | null;
  /** The exit code, `signal`, or `lost`. */
  exit?: string | null;
  /** Unix milliseconds. */
  started: number;
};

/**
 * Whether a machine can take a call now, the one answer the page, the app, MCP, the SDK and the
 * refusals give (machine-presence V1). It is derived from the time of the machine's last
 * envelope, never from WebSocket control frames, so a proxy that pings cannot keep a gone
 * machine looking alive.
 */
export type Presence = "online" | "stale" | "offline" | "paused";

/** A process cmdop did not start, with who did. */
export type ProcView = {
  argv: string[];
  author: string;
  cwd?: string | null;
  machine: string;
  machine_name: string;
  pid: number;
  started: number;
};

/** Where a task is in its life. The store keeps it as text (`cmdop-store` writes only these five). */
export type TaskState = "running" | "starting" | "ended" | "failed" | "lost";

/** Every tool the server answers itself: its arguments and its result. */
export interface ServerToolMap {
  docs_read: { args: DocsReadArgs; out: DocsReadOut };
  history_search: { args: HistorySearchArgs; out: HistorySearchOut };
  machines_list: { args: MachinesListArgs; out: MachinesListOut };
  showtime_guide: { args: ShowtimeGuideArgs; out: ShowtimeGuideOut };
  tasks_list: { args: TasksListArgs; out: TasksListOut };
}

export type ServerToolName = keyof ServerToolMap;

/** Title and description of every server tool, as the server lists them. */
export const SERVER_TOOLS = {
  docs_read: { title: "Read the docs", description: "Call before answering how CMDOP works, is set up or is priced: no `path` lists every page of docs.cmdop.ai (path and title); a `path` returns that page as Markdown." },
  history_search: { title: "Search history", description: "Past tasks, tool calls and agent sessions by machine, author, task, time and text, newest first. Calls carry no arguments; journal_search on the machine has them." },
  machines_list: { title: "List machines", description: "The owner's machines: name, id, `state` (online; stale = not answering; paused; offline), `last_seen`, `activity`, `tools` (screen and control are here), build, `behind`. Only online ones take calls." },
  showtime_guide: { title: "Showtime guide", description: "Call when the user asks to see what CMDOP can do (a demo or a show), or offer it to a user new to CMDOP: returns a guide for a short live demonstration on their machines." },
  tasks_list: { title: "List running work", description: "Everything running now, by author. `tasks`: started through cmdop. `outside`: other processes per machine, by agent:claude-code, agent:codex or user. Ended ones: history_search." },
} as const satisfies Record<ServerToolName, { title: string; description: string }>;

export const SERVER_TOOL_NAMES = ["docs_read","history_search","machines_list","showtime_guide","tasks_list"] as const satisfies readonly ServerToolName[];

/** The server tools as client methods (`cmdop.showtime_guide()`): no machine, never sealed. */
export interface ServerMethods<O> {
  /** Call before answering how CMDOP works, is set up or is priced: no `path` lists every page of docs.cmdop.ai (path and title); a `path` returns that page as Markdown. */
  docs_read(args?: DocsReadArgs, opts?: O): Promise<DocsReadOut>;
  /** Past tasks, tool calls and agent sessions by machine, author, task, time and text, newest first. Calls carry no arguments; journal_search on the machine has them. */
  history_search(args?: HistorySearchArgs, opts?: O): Promise<HistorySearchOut>;
  /** The owner's machines: name, id, `state` (online; stale = not answering; paused; offline), `last_seen`, `activity`, `tools` (screen and control are here), build, `behind`. Only online ones take calls. */
  machines_list(args?: MachinesListArgs, opts?: O): Promise<MachinesListOut>;
  /** Call when the user asks to see what CMDOP can do (a demo or a show), or offer it to a user new to CMDOP: returns a guide for a short live demonstration on their machines. */
  showtime_guide(args?: ShowtimeGuideArgs, opts?: O): Promise<ShowtimeGuideOut>;
  /** Everything running now, by author. `tasks`: started through cmdop. `outside`: other processes per machine, by agent:claude-code, agent:codex or user. Ended ones: history_search. */
  tasks_list(args?: TasksListArgs, opts?: O): Promise<TasksListOut>;
}
