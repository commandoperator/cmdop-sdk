// Generated from cmdop/crates/tools/tools.schema.json (sha256 459e32fe9bbff178, cmdop 0.1.9) by exports/sdk/gen/gen.ts. Do not edit.

export type ErrorCode = "other" | "denied" | "unknown_tool" | "bad_args" | "not_found" | "busy" | "permission_missing" | "screen_locked" | "stale_capture" | "element_gone" | "app_not_allowed" | "lease_paused" | "paused" | "offline" | "rate_limited" | "quota_exceeded" | "not_dispatched" | "display_gone" | "timed_out" | "cancelled" | "too_large" | "hash_required" | "failed" | "needs_presence" | "unauthorized";

/**
 * One piece of a running command's output, as a streaming `exec_run` sends it (the payload of
 * a `CallChunk`). The machine writes it and every client reads it, so it is defined here once.
 * Fields are in the order the text has always had them; `dropped` is absent when nothing was.
 */
export type OutputChunk = {
  /** The output, as text (invalid UTF-8 replaced). */
  data: string;
  /**
   * Bytes left out just before this piece because the reader fell behind; the call's final
   * result still has the whole tail.
   */
  dropped?: number | null;
  stream: OutputStream;
};

/** One call, as a caller sends it. */
export type CallRequest = {
  /** The arguments, as the tool's input schema says. Absent means `{}`. */
  args?: unknown;
  /**
   * How long the caller waits, in milliseconds. The call keeps the smaller of this and the
   * tool's own time; past it the answer is `timed_out`. Absent: the tool's time.
   */
  deadline_ms?: number | null;
  /** Machine id or unique name; optional when exactly one machine is online. */
  machine?: string | null;
  /** The arguments sealed for the machine, instead of `args`. */
  sealed?: string | null;
  /** The tool's name, in clear: the server routes and checks the grant by it. */
  tool: string;
};

/**
 * How a call ended: its result, why there is none, or a sealed answer with its outcome in
 * clear (`ok` or an error code).
 */
export type Answer = {
  ok: unknown;
} | {
  error: ToolError;
} | {
  outcome: string;
  sealed: string;
};

/**
 * One line of a streamed answer: a piece of output while the call runs, and the answer last.
 * `seq` counts the pieces of one call from 0, in the order they were made.
 */
export type StreamLine = {
  chunk: OutputChunk;
  seq: number;
} | {
  sealed_chunk: string;
  seq: number;
} | Answer;

/** Which output of the command a piece comes from. */
export type OutputStream = "stdout" | "stderr";

/**
 * Why a call did not return a result. The machine answers with this; the server and the SDK
 * decide by `code`, never by `message`.
 */
export type ToolError = {
  code: ErrorCode;
  /**
   * Machine-readable facts for the caller, per code (`permission_missing` carries the
   * permission, who must act and where). Absent for most errors; never required to read
   * `code`.
   */
  details?: unknown;
  message: string;
};

/** Every error code, in the order Rust declares them. */
export const ERROR_CODES = ["other","denied","unknown_tool","bad_args","not_found","busy","permission_missing","screen_locked","stale_capture","element_gone","app_not_allowed","lease_paused","paused","offline","rate_limited","quota_exceeded","not_dispatched","display_gone","timed_out","cancelled","too_large","hash_required","failed","needs_presence","unauthorized"] as const satisfies readonly ErrorCode[];

/** The size limits every carrier keeps. */
export const LIMITS = { envelopeMaxBytes: 16777216, pieceMaxBytes: 65536 } as const;
