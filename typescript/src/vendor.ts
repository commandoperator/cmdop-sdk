/**
 * Vendor computer-use actions as cmdop tool calls (@dev/completed/computer-use/10_computer_use.md, D13). The machine publishes one convention;
 * the formats of the vendors are converted here, in pure functions: an action in, a list of steps out.
 *
 * Supported: Anthropic `computer_20250124` / `computer_20251124` actions (`screenshot`, `left_click`, `right_click`,
 * `middle_click`, `double_click`, `triple_click`, `mouse_move`, `left_click_drag`, `type`, `key`, `hold_key`, `scroll`,
 * `wait`, `cursor_position`, `zoom`) and OpenAI computer-use actions (`screenshot`, `click`, `double_click`, `scroll`,
 * `type`, `keypress`, `move`, `drag`, `wait`).
 *
 * Not supported yet: models that point on a 0-999 grid (UI-TARS style) or in relative coordinates. Their numbers are not
 * pixels of our screenshot and converting them needs the screen size; such an action is not guessed at. Also refused:
 * `left_mouse_down` / `left_mouse_up` (no half-clicks: a button is never left held), and OpenAI `wheel`, `back` and
 * `forward` buttons.
 *
 * Coordinates are taken as pixels of the image the latest `screen_capture` returned, which is what both vendors expect
 * when the screenshot they were shown is the one we sent. Input steps ask for `observe: "image"` by default because a
 * vendor loop wants a screenshot after every action; pass `observe: "none"` to send them without.
 */

import type { Machine } from "./client.ts";
import type { Modifier, Observe, Point, ToolMap, ToolName } from "./generated/tools.gen.ts";

/** One thing to do: a tool call, or a pause the caller makes itself (the machine never sleeps on its own). */
export type Step = { [N in ToolName]: { tool: N; args: ToolMap[N]["args"] } }[ToolName] | { sleep_ms: number };

export interface VendorOptions {
  /** What input steps return afterwards. Default `"image"`. */
  observe?: Observe;
}

/** An action this adapter does not convert. The message says why; nothing was sent. */
export class UnsupportedAction extends Error {
  constructor(message: string) {
    super(message);
    this.name = "UnsupportedAction";
  }
}

const MAX_LINES = 10;
const clampLines = (n: number): number => Math.max(-MAX_LINES, Math.min(MAX_LINES, Math.round(n)));

function num(v: unknown, what: string): number {
  if (typeof v !== "number" || !Number.isFinite(v)) throw new UnsupportedAction(`${what} must be a number`);
  return Math.round(v);
}

/** Seconds as milliseconds, without rounding the seconds first. */
function millis(v: unknown, what: string): number {
  if (typeof v !== "number" || !Number.isFinite(v) || v < 0) throw new UnsupportedAction(`${what} must be a number of seconds`);
  return Math.round(v * 1000);
}

function pair(v: unknown, what: string): Point {
  if (!Array.isArray(v) || v.length !== 2) throw new UnsupportedAction(`${what} must be [x, y]`);
  return { x: num(v[0], `${what}[0]`), y: num(v[1], `${what}[1]`) };
}

function text(v: unknown, what: string): string {
  if (typeof v !== "string") throw new UnsupportedAction(`${what} must be a string`);
  return v;
}

const MODIFIERS: Record<string, Modifier> = {
  shift: "shift",
  ctrl: "ctrl",
  control: "ctrl",
  alt: "alt",
  option: "alt",
  opt: "alt",
  meta: "meta",
  cmd: "meta",
  command: "meta",
  super: "meta",
  win: "meta",
  windows: "meta",
};

/** Key names the vendors use (xdotool, DOM, OpenAI) to ours (`crates/tools` `key_press`). Anything else passes through. */
const KEYS: Record<string, string> = {
  return: "Enter",
  enter: "Enter",
  kp_enter: "Enter",
  tab: "Tab",
  escape: "Escape",
  esc: "Escape",
  space: "Space",
  backspace: "Backspace",
  delete: "Delete",
  home: "Home",
  end: "End",
  page_up: "PageUp",
  pageup: "PageUp",
  prior: "PageUp",
  page_down: "PageDown",
  pagedown: "PageDown",
  next: "PageDown",
  up: "ArrowUp",
  down: "ArrowDown",
  left: "ArrowLeft",
  right: "ArrowRight",
  arrowup: "ArrowUp",
  arrowdown: "ArrowDown",
  arrowleft: "ArrowLeft",
  arrowright: "ArrowRight",
};

const MODIFIER_KEYS: Record<Modifier, string> = { shift: "Shift", ctrl: "Control", alt: "Alt", meta: "Meta" };

function keyName(raw: string): string {
  const k = raw.trim();
  if (k === "" && raw.length > 0) return "Space";
  const mapped = KEYS[k.toLowerCase()];
  if (mapped) return mapped;
  // A single letter is lower case: the shift is a modifier, never implied by the case.
  if (k.length === 1) return k.toLowerCase();
  // `F5`, `f5` → `F5`.
  if (/^f\d{1,2}$/i.test(k)) return k.toUpperCase();
  return k;
}

/** `["CTRL", "A"]` or `"ctrl+shift+a"` → modifiers and the one key. */
function chord(parts: string[]): { key: string; modifiers: Modifier[] } {
  const modifiers: Modifier[] = [];
  const keys: string[] = [];
  for (const p of parts) {
    const m = MODIFIERS[p.trim().toLowerCase()];
    if (m) {
      if (!modifiers.includes(m)) modifiers.push(m);
    } else keys.push(p);
  }
  // A modifier pressed alone (`hold_key Shift`) is the key itself, named as the DOM does.
  if (keys.length === 0 && modifiers.length > 0) return { key: MODIFIER_KEYS[modifiers[modifiers.length - 1] as Modifier], modifiers: modifiers.slice(0, -1) };
  if (keys.length !== 1) throw new UnsupportedAction(`a key press needs exactly one key besides modifiers, got ${JSON.stringify(parts)}`);
  return { key: keyName(keys[0] as string), modifiers };
}

/** `"ctrl+s"`, `"alt+Tab"`, `"Return"`, a lone `"+"`. */
function splitChord(s: string): string[] {
  if (s === "+") return ["+"];
  return s.split("+").map((p) => (p === "" ? "+" : p));
}

/** The modifiers of an Anthropic click's `text` (`"ctrl"`, `"ctrl+shift"`). */
function modifiersOf(v: unknown): Modifier[] {
  if (v === undefined || v === null || v === "") return [];
  return chord([...splitChord(text(v, "text")), "x"]).modifiers;
}

const withMods = (modifiers: Modifier[]): { modifiers?: Modifier[] } => (modifiers.length ? { modifiers } : {});

/**
 * Anthropic computer-use tool actions. `action` is the tool input as the model wrote it (`{ action: "left_click",
 * coordinate: [640, 400] }`). Returns the steps to run in order.
 */
export function anthropicToCalls(action: unknown, opts: VendorOptions = {}): Step[] {
  if (typeof action !== "object" || action === null) throw new UnsupportedAction("an action must be an object");
  const a = action as Record<string, unknown>;
  const observe = opts.observe ?? "image";
  const at = (): Point => pair(a.coordinate, "coordinate");
  const click = (button: "left" | "right" | "middle", count: number): Step[] => [
    { tool: "pointer_click", args: { ...at(), button, count, ...withMods(modifiersOf(a.text)), observe } },
  ];
  switch (a.action) {
    case "screenshot":
      return [{ tool: "screen_capture", args: {} }];
    case "left_click":
      return click("left", 1);
    case "right_click":
      return click("right", 1);
    case "middle_click":
      return click("middle", 1);
    case "double_click":
      return click("left", 2);
    case "triple_click":
      return click("left", 3);
    case "mouse_move":
      return [{ tool: "pointer_move", args: { ...at(), observe } }];
    case "left_click_drag": {
      const path = [pair(a.start_coordinate, "start_coordinate"), pair(a.coordinate, "coordinate")];
      return [{ tool: "pointer_drag", args: { path, ...withMods(modifiersOf(a.text)), observe } }];
    }
    case "type":
      return [{ tool: "text_type", args: { text: text(a.text, "text"), observe } }];
    case "key": {
      const { key, modifiers } = chord(splitChord(text(a.text, "text")));
      return [{ tool: "key_press", args: { key, ...withMods(modifiers), observe } }];
    }
    case "hold_key": {
      const { key, modifiers } = chord(splitChord(text(a.text, "text")));
      const hold_ms = millis(a.duration, "duration");
      return [{ tool: "key_press", args: { key, hold_ms, ...withMods(modifiers), observe } }];
    }
    case "scroll": {
      const n = num(a.scroll_amount ?? 1, "scroll_amount");
      let dx = 0;
      let dy = 0;
      if (a.scroll_direction === "up") dy = -n;
      else if (a.scroll_direction === "down") dy = n;
      else if (a.scroll_direction === "left") dx = -n;
      else if (a.scroll_direction === "right") dx = n;
      else throw new UnsupportedAction("scroll_direction must be up, down, left or right");
      return [{ tool: "pointer_scroll", args: { ...at(), dx: clampLines(dx), dy: clampLines(dy), observe } }];
    }
    case "wait":
      return [{ sleep_ms: millis(a.duration, "duration") }, { tool: "screen_capture", args: {} }];
    case "cursor_position":
      return [{ tool: "screen_info", args: {} }];
    case "zoom": {
      const r = a.region;
      if (!Array.isArray(r) || r.length !== 4) throw new UnsupportedAction("region must be [x0, y0, x1, y1]");
      const [x0, y0, x1, y1] = r.map((v, i) => num(v, `region[${i}]`)) as [number, number, number, number];
      return [{ tool: "screen_capture", args: { region: { x: x0, y: y0, w: x1 - x0, h: y1 - y0 } } }];
    }
    case "left_mouse_down":
    case "left_mouse_up":
      throw new UnsupportedAction(`${String(a.action)}: half-clicks are not offered (a button is never left held); use left_click_drag`);
    default:
      throw new UnsupportedAction(`unknown Anthropic action ${JSON.stringify(a.action)}`);
  }
}

/** Pixels of an OpenAI wheel delta to lines: about a notch per 100 px, at least one line for any movement. */
function pixelsToLines(px: number): number {
  if (px === 0) return 0;
  return clampLines(Math.sign(px) * Math.max(1, Math.round(Math.abs(px) / 100)));
}

/**
 * OpenAI computer-use actions (`{ type: "click", x, y, button }`, the `action` of a `computer_call`). Returns the
 * steps to run in order.
 */
export function openaiToCalls(action: unknown, opts: VendorOptions = {}): Step[] {
  if (typeof action !== "object" || action === null) throw new UnsupportedAction("an action must be an object");
  const a = action as Record<string, unknown>;
  const observe = opts.observe ?? "image";
  const at = (): Point => ({ x: num(a.x, "x"), y: num(a.y, "y") });
  switch (a.type) {
    case "screenshot":
      return [{ tool: "screen_capture", args: {} }];
    case "click": {
      const button = a.button ?? "left";
      if (button !== "left" && button !== "right" && button !== "middle") {
        throw new UnsupportedAction(`click button ${JSON.stringify(button)} is not offered (left, right and middle are)`);
      }
      return [{ tool: "pointer_click", args: { ...at(), button, count: 1, observe } }];
    }
    case "double_click":
      return [{ tool: "pointer_click", args: { ...at(), button: "left", count: 2, observe } }];
    case "move":
      return [{ tool: "pointer_move", args: { ...at(), observe } }];
    case "scroll":
      return [
        {
          tool: "pointer_scroll",
          args: { ...at(), dx: pixelsToLines(num(a.scroll_x ?? 0, "scroll_x")), dy: pixelsToLines(num(a.scroll_y ?? 0, "scroll_y")), observe },
        },
      ];
    case "type":
      return [{ tool: "text_type", args: { text: text(a.text, "text"), observe } }];
    case "keypress": {
      if (!Array.isArray(a.keys) || a.keys.length === 0) throw new UnsupportedAction("keys must be a non-empty array");
      const { key, modifiers } = chord(a.keys.map((k) => text(k, "keys[]")));
      return [{ tool: "key_press", args: { key, ...withMods(modifiers), observe } }];
    }
    case "drag": {
      if (!Array.isArray(a.path) || a.path.length < 2) throw new UnsupportedAction("path must hold at least two points");
      const path = a.path.map((p, i): Point => {
        const o = (p ?? {}) as Record<string, unknown>;
        return { x: num(o.x, `path[${i}].x`), y: num(o.y, `path[${i}].y`) };
      });
      return [{ tool: "pointer_drag", args: { path, observe } }];
    }
    case "wait":
      // OpenAI's wait has no length; its examples wait about two seconds.
      return [{ sleep_ms: 2000 }, { tool: "screen_capture", args: {} }];
    default:
      throw new UnsupportedAction(`unknown OpenAI action ${JSON.stringify(a.type)}`);
  }
}

/**
 * Runs steps on one machine in order and returns the answer of the last tool call. A `sleep_ms` step waits here, on the
 * caller's side. The first failing call throws its `CmdopError`; later steps are not run.
 */
export async function performCalls(
  machine: Machine,
  steps: Step[],
  sleep: (ms: number) => Promise<void> = (ms) => new Promise((r) => setTimeout(r, ms)),
): Promise<unknown> {
  let last: unknown;
  for (const s of steps) {
    if ("sleep_ms" in s) await sleep(s.sleep_ms);
    else last = await (machine[s.tool] as (args: unknown) => Promise<unknown>)(s.args);
  }
  return last;
}
