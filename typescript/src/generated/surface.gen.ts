// Generated from cmdop/crates/tools/tools.schema.json (sha256 53ac9daa3bb73c83, cmdop 0.1.11) by exports/sdk/gen/gen.ts. Do not edit.

/** Every tool under its group (`box.fs.read` is `fs_read`), and the short forms of `gen/forms.json`. */

import type { Run } from "../client.ts";
import type { Screenshot } from "../screen.ts";
import type { ToolMap, ToolName } from "./tools.gen.ts";

/** Group, then method, then the tool it calls. */
export const GROUPS = {
  app: { open: "app_open" },
  control: { release: "control_release" },
  exec: { run: "exec_run" },
  fs: { delete: "fs_delete", edit: "fs_edit", list: "fs_list", read: "fs_read", search: "fs_search", stat: "fs_stat", write: "fs_write" },
  journal: { search: "journal_search" },
  key: { press: "key_press" },
  pointer: { click: "pointer_click", drag: "pointer_drag", move: "pointer_move", scroll: "pointer_scroll" },
  proc: { kill: "proc_kill", list: "proc_list" },
  screen: { capture: "screen_capture", info: "screen_info" },
  sys: { info: "sys_info" },
  task: { output: "task_output", start: "task_start", stop: "task_stop" },
  text: { type: "text_type" },
  ui: { act: "ui_act", snapshot: "ui_snapshot", wait: "ui_wait" },
  window: { list: "window_list" },
} as const satisfies Record<string, Record<string, ToolName>>;

export type GroupName = keyof typeof GROUPS;

type ToolOf<G extends GroupName, M extends keyof (typeof GROUPS)[G]> = (typeof GROUPS)[G][M] & ToolName;

/** The methods of every group; `O` is the per-call options type. */
export type Groups<O> = {
  readonly [G in GroupName]: {
    readonly [M in keyof (typeof GROUPS)[G]]: (args: ToolMap[ToolOf<G, M>]["args"], opts?: O) => Promise<ToolMap[ToolOf<G, M>]["out"]>;
  };
};

/** How a short form is called: its tool, the positional arguments in order, whether it streams, its decoder. */
export interface FormSpec {
  readonly name: string;
  readonly tool: ToolName;
  readonly positional: readonly string[];
  readonly stream: boolean;
  readonly result: "raw" | "screenshot";
}

export const FORMS = [
  { name: "run", tool: "exec_run", positional: ["command"], stream: false, result: "raw" },
  { name: "stream", tool: "exec_run", positional: ["command"], stream: true, result: "raw" },
  { name: "screenshot", tool: "screen_capture", positional: [], stream: false, result: "screenshot" },
] as const satisfies readonly FormSpec[];

/** The short forms as methods; `O` is the per-call options type. */
export type Forms<O> = {
  /** `exec_run` with a shell command line. */
  run(command: string, args?: Omit<ToolMap["exec_run"]["args"], "command" | "argv">, opts?: O): Promise<ToolMap["exec_run"]["out"]>;
  /** `exec_run` with its output as it comes. Breaking out of the loop or cancelling stops the command. */
  stream(command: string, args?: Omit<ToolMap["exec_run"]["args"], "command" | "argv">, opts?: O): Run<ToolMap["exec_run"]["out"]>;
  /** `screen_capture` with the picture decoded. Needs the `screen` grant and `screen` in the machine's ceiling. */
  screenshot(args?: ToolMap["screen_capture"]["args"], opts?: O): Promise<Screenshot>;
};
