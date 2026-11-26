// The carrier vectors (`exports/sdk/vectors/carrier.json`, written from Rust) and how a client runs one: shared by
// the conformance suite (each carrier, a door played from the vector) and `make sdk-live` (a real server and machine).

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { isDeepStrictEqual } from "node:util";
import { CarrierError } from "../src/carriers/carrier.ts";
import { CmdopError, type Client } from "../src/client.ts";
import type { CallRequest, StreamLine } from "../src/generated/call.gen.ts";
import type { ToolName } from "../src/generated/tools.gen.ts";

export interface Vector {
  name: string;
  call: CallRequest;
  pad_command_to?: number;
  stream: boolean;
  door: StreamLine[];
  cancel_after_pieces?: number;
  expect: { outcome: string; pieces?: { stream: string; data: string }[]; result?: Record<string, unknown> };
  live: boolean;
}

export interface Seen {
  outcome: string;
  pieces: { stream: string; data: string }[];
  result: Record<string, unknown> | undefined;
}

const file = fileURLToPath(new URL("../../vectors/carrier.json", import.meta.url));
export const vectors = (JSON.parse(readFileSync(file, "utf8")) as { vectors: Vector[] }).vectors;

/** Sends the vector's call through `c` (to `machine` when given) and says what the caller saw. */
export async function runVector(v: Vector, c: Client, machine?: string): Promise<Seen> {
  const args = { ...(v.call.args as Record<string, unknown>) };
  if (v.pad_command_to !== undefined) args.command = `${String(args.command)} #`.padEnd(v.pad_command_to, "x");
  const tool = v.call.tool as ToolName;
  const opts = { ...(v.call.deadline_ms == null ? {} : { deadline: v.call.deadline_ms }), ...(machine === undefined ? {} : { machine }) };
  const pieces: Seen["pieces"] = [];
  const outcomeOf = (e: unknown) => (e instanceof CmdopError ? e.code : e instanceof CarrierError ? "carrier_error" : `threw ${String(e)}`);
  try {
    if (!v.stream) return { outcome: "ok", pieces, result: (await c.call(tool, args as never, opts)) as Record<string, unknown> };
    const r = c.stream(tool, args as never, opts);
    for await (const p of r) {
      pieces.push({ stream: p.stream, data: p.data });
      if (v.cancel_after_pieces !== undefined && pieces.length >= v.cancel_after_pieces) break;
    }
    return { outcome: "ok", pieces, result: (await r.result) as Record<string, unknown> };
  } catch (e) {
    return { outcome: outcomeOf(e), pieces, result: undefined };
  }
}

/** How what the caller saw differs from the vector's `expect`; empty when it matches. */
export function differences(v: Vector, got: Seen): string[] {
  const out: string[] = [];
  if (got.outcome !== v.expect.outcome) out.push(`outcome ${got.outcome}, want ${v.expect.outcome}`);
  // Compared as values: the key order of a piece is not part of the contract.
  const want = v.expect.pieces ?? [];
  if (!isDeepStrictEqual(got.pieces, want)) out.push(`pieces ${JSON.stringify(got.pieces)}, want ${JSON.stringify(want)}`);
  for (const [k, val] of Object.entries(v.expect.result ?? {})) {
    if (!isDeepStrictEqual(got.result?.[k], val)) out.push(`result.${k} ${JSON.stringify(got.result?.[k])}, want ${JSON.stringify(val)}`);
  }
  return out;
}
