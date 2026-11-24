/**
 * The cmdop client (developer SDK plan, section 4): your machines' tools from a program.
 *
 * ```ts
 * const cmdop = connect();                       // CMDOP_TOKEN and CMDOP_URL
 * const box = cmdop.machine("box");
 * const { exit_code, stdout } = await box.run("uptime");
 * const run = box.stream("make test");
 * for await (const piece of run) process.stdout.write(piece.data);
 * const done = await run.result;
 * ```
 *
 * Every tool, its arguments and result, the error codes and the call shapes are generated from the Rust workspace
 * (`generated/`). This file speaks only the call contract; which channel carries it is the carrier's business
 * (`carriers/`), and nothing here knows it.
 *
 * End-to-end calls come through a `Sealer` (`connect({ e2e })`): this file holds no key and reads no sealed text.
 */

import type { Answer, CallRequest, ErrorCode, OutputChunk, StreamLine } from "./generated/call.gen.ts";
import { FORMS, GROUPS, type Forms, type Groups } from "./generated/surface.gen.ts";
import { TOOL_NAMES, type ExecRunOut, type ToolMap, type ToolName } from "./generated/tools.gen.ts";
import { CarrierError, type Carrier, type MachineRow } from "./carriers/carrier.ts";
import { httpCarrier } from "./carriers/http.ts";
import { toScreenshot } from "./screen.ts";

/**
 * End-to-end calls: `connect({ e2e })` takes a sealer. It turns each call into the request to send and opens what
 * comes back for it; the client sends what it is given and never reads the sealed text itself.
 */
export interface Sealer {
  /** The request to send for one call, and how to open what comes back for it. `machines` lists the contour's machines. */
  seal(call: CallRequest, machines: () => Promise<MachineRow[]>): Promise<{ req: CallRequest; open: Opener }>;
  /** This client's public key, for `cmdop pair <key>` on each machine. */
  publicKey(): Promise<string>;
}

/** Opens what comes back for one sealed call. Anything not sealed for it throws `CmdopError` (`not_sealed`). */
export interface Opener {
  answer(sealed: string): Promise<Answer>;
  piece(seq: number, sealed: string): Promise<OutputChunk>;
}

export interface ConnectOptions {
  /** An agent token (held to its grant) or an owner token. Default: `CMDOP_TOKEN`. Keep it out of source and logs. */
  token?: string;
  /** The contour's address in full, `https://<address>.cmdop.dev` or a local server. Default: `CMDOP_URL`. */
  url?: string;
  /** The contour's address alone, for example `m7xg5cgy`, instead of `url`. */
  contour?: string;
  /** `"auto"` (default, or `CMDOP_CARRIER`), `"http"`, or a carrier of your own (tests: `memoryCarrier`). */
  carrier?: "auto" | "http" | Carrier;
  /** Seal every call end to end with this sealer. */
  e2e?: Sealer;
  /** For the HTTP carrier in tests and other runtimes; the global `fetch` by default. */
  fetch?: typeof fetch;
}

export interface CallOpts {
  /** Machine id or unique name; left out when exactly one machine is online. */
  machine?: string;
  /** How long to wait, in milliseconds. The call keeps the shorter of this and the tool's own time. */
  deadline?: number;
  /** Aborting it cancels the call; the answer is then `cancelled`. */
  signal?: AbortSignal;
}

/** Why a call returned no result. Decide by `code`, never by `message`. */
export class CmdopError extends Error {
  readonly code: ErrorCode | "not_sealable" | "not_sealed" | "key_changed";
  /**
   * Machine-readable facts that come with some codes. `permission_missing` carries
   * `{ permission, state, requires_human, machine, human_action, retry }`: a person must act on that machine, do not
   * retry until they have.
   */
  readonly details?: Record<string, unknown>;
  constructor(code: CmdopError["code"], message: string, details?: Record<string, unknown>) {
    super(message);
    this.name = "CmdopError";
    this.code = code;
    if (details !== undefined) this.details = details;
  }
}

/** One piece of a running command's output, with its place in the call. */
export type Piece = OutputChunk & { seq: number };

/** A call running with its output followed: iterate for the pieces, then `await run.result`. */
export interface Run<T = ExecRunOut> extends AsyncIterable<Piece> {
  /** The call's result, the same as the one-shot call returns. Awaiting it without iterating skips the pieces. */
  readonly result: Promise<T>;
}

type ToolMethods = {
  [N in ToolName]: (args: ToolMap[N]["args"], opts?: Omit<CallOpts, "machine">) => Promise<ToolMap[N]["out"]>;
};

/**
 * One machine: every tool as a method (`box.fs_read({ path })`), under its group (`box.fs.read({ path })`), and the
 * short forms (`run`, `stream`, `screenshot`), all generated (`generated/surface.gen.ts`).
 */
export type Machine = ToolMethods & Groups<Omit<CallOpts, "machine">> & Forms<Omit<CallOpts, "machine">>;

/** What a short form's result becomes: the decoders, the one hand-written part of the forms. */
const DECODE: Record<(typeof FORMS)[number]["result"], (out: never) => unknown> = { raw: (out) => out, screenshot: toScreenshot };

export interface Client {
  /** Which carrier is in use (`"http"`, …): what `auto` picked. */
  readonly carrier: string;
  /** The machines of the contour: name, id, online, os, tools. */
  machines(opts?: Pick<CallOpts, "signal">): Promise<MachineRow[]>;
  /** One machine; no name: the one online machine (the server decides). */
  machine(name?: string): Machine;
  /** Runs any tool by name. */
  call<N extends ToolName>(tool: N, args: ToolMap[N]["args"], opts?: CallOpts): Promise<ToolMap[N]["out"]>;
  /** Runs any tool by name as a streamed call: its pieces as they come (only `exec_run` sends any), then its result. */
  stream<N extends ToolName>(tool: N, args: ToolMap[N]["args"], opts?: CallOpts): Run<ToolMap[N]["out"]>;
  /** With `e2e`: this client's public key, for `cmdop pair <key>` on each machine. */
  publicKey(): Promise<string>;
  close(): Promise<void>;
}

const env = (name: string): string | undefined => (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env?.[name];

/** `url` as given, else `https://<contour>.cmdop.dev`; `CMDOP_URL` when neither is given. */
export function urlOf(opts: Pick<ConnectOptions, "url" | "contour">): string {
  if (opts.url && opts.contour) throw new Error("connect: give url or contour, not both");
  if (opts.contour) {
    if (!/^[a-z0-9-]+$/.test(opts.contour)) throw new Error(`connect: ${JSON.stringify(opts.contour)} is not a contour address`);
    return `https://${opts.contour}.cmdop.dev`;
  }
  const url = opts.url ?? env("CMDOP_URL");
  if (!url) throw new Error("connect: no address; set CMDOP_URL (your page's address, https://<address>.cmdop.dev) or pass url");
  return url.replace(/\/+$/, "");
}

function carrierOf(opts: ConnectOptions): Carrier {
  const want = opts.carrier ?? (env("CMDOP_CARRIER") as ConnectOptions["carrier"]) ?? "auto";
  if (typeof want === "object") return want;
  const token = opts.token ?? env("CMDOP_TOKEN");
  if (!token) throw new Error("connect: no token; set CMDOP_TOKEN or pass token");
  // One door exists today, so `auto` is HTTP. A second carrier adds its probe here, never a branch in the client.
  if (want === "auto" || want === "http") return httpCarrier({ url: urlOf(opts), token, ...(opts.fetch ? { fetch: opts.fetch } : {}) });
  throw new Error(`connect: unknown carrier ${JSON.stringify(want)} (auto, http)`);
}

function errorOf(e: { code: string; message: string; details?: unknown }): CmdopError {
  const d = e.details;
  const details = typeof d === "object" && d !== null && !Array.isArray(d) ? (d as Record<string, unknown>) : undefined;
  return new CmdopError(e.code as ErrorCode, e.message, details);
}

/** The tool's result, or the refusal as a `CmdopError`. */
function settle<T>(a: Answer): T {
  if ("ok" in a) return a.ok as T;
  if ("error" in a) throw errorOf(a.error);
  throw new CmdopError("not_sealed", "a sealed answer reached a call that was not sealed");
}

const isAnswer = (l: StreamLine): l is Answer => "ok" in l || "error" in l || "sealed" in l;

/** A call on its way: the request, and for a sealed one how to open what comes back. */
interface Prepared {
  req: CallRequest;
  open?: Opener;
}

export function connect(opts: ConnectOptions = {}): Client {
  const carrier = carrierOf(opts);

  async function machines(o: Pick<CallOpts, "signal"> = {}): Promise<MachineRow[]> {
    return settle<MachineRow[]>(await carrier.machines(o));
  }

  async function prepare(tool: string, args: unknown, o: CallOpts): Promise<Prepared> {
    const deadline = o.deadline === undefined ? {} : { deadline_ms: Math.max(0, Math.round(o.deadline)) };
    const req: CallRequest = { tool, args: args ?? {}, ...(o.machine === undefined ? {} : { machine: o.machine }), ...deadline };
    return opts.e2e ? opts.e2e.seal(req, () => machines()) : { req };
  }

  /** The tool's result from an answer, opened when the call was sealed. */
  async function result<T>(p: Prepared, a: Answer): Promise<T> {
    if (!p.open) return settle<T>(a);
    if ("sealed" in a) return settle<T>(await p.open.answer(a.sealed));
    // Refusals come in clear (they hold nothing secret); a result never does.
    if ("ok" in a) throw new CmdopError("not_sealed", "a sealed call came back in clear; refusing it");
    return settle<T>(a);
  }

  /** A carrier failure the caller caused (abort) is the contract's `cancelled`. */
  function cancelledOr(e: unknown, signal: AbortSignal | undefined): unknown {
    return signal?.aborted ? new CmdopError("cancelled", "the call was stopped by its caller") : e;
  }

  async function call<N extends ToolName>(tool: N, args: ToolMap[N]["args"], o: CallOpts = {}): Promise<ToolMap[N]["out"]> {
    const p = await prepare(tool, args, o);
    let a: Answer;
    try {
      a = await carrier.call(p.req, o.signal ? { signal: o.signal } : {});
    } catch (e) {
      throw cancelledOr(e, o.signal);
    }
    return result(p, a);
  }

  /** Pieces of one streamed call in order, opened when sealed; the answer last. */
  async function* lines(p: Prepared, o: CallOpts): AsyncGenerator<Piece, Answer> {
    try {
      for await (const l of carrier.stream(p.req, o.signal ? { signal: o.signal } : {})) {
        if (isAnswer(l)) return l;
        if ("chunk" in l && !p.open) yield { ...l.chunk, seq: l.seq };
        else if ("sealed_chunk" in l && p.open) yield { ...(await p.open.piece(l.seq, l.sealed_chunk)), seq: l.seq };
        else throw new CmdopError("not_sealed", "a piece came back in a form this call did not ask for");
      }
    } catch (e) {
      throw cancelledOr(e, o.signal);
    }
    throw new CarrierError(carrier.name, "the stream ended without an answer");
  }

  function stream<N extends ToolName>(tool: N, args: ToolMap[N]["args"], o: CallOpts = {}): Run<ToolMap[N]["out"]> {
    type Out = ToolMap[N]["out"];
    // Breaking out of the loop aborts the request, which cancels the call on the machine.
    const stop = new AbortController();
    const signal = o.signal ? AbortSignal.any([o.signal, stop.signal]) : stop.signal;
    const opts: CallOpts = { ...o, signal };
    let gen: AsyncGenerator<Piece, Answer> | undefined;
    let iterated = false;
    let resolveDone!: (a: Promise<Out>) => void;
    let settled = false;
    const done = new Promise<Out>((resolve) => (resolveDone = resolve));
    // Nobody may await the result of a run they stopped; its rejection is still theirs to read.
    done.catch(() => {});
    // A thunk, so a rejection is only made when it settles the result (an unread one would be reported).
    const settleResult = (a: () => Promise<Out>) => {
      if (settled) return;
      settled = true;
      resolveDone(a());
    };
    const prepared = prepare(tool, args, opts);
    const start = async () => (gen ??= lines(await prepared, opts));
    const finish = async (a: Answer) => settleResult(() => result$(a));
    const result$ = async (a: Answer) => result<Out>(await prepared, a);
    return {
      async *[Symbol.asyncIterator]() {
        iterated = true;
        const g = await start();
        try {
          for (;;) {
            const n = await g.next();
            if (n.done) {
              await finish(n.value);
              return;
            }
            yield n.value;
          }
        } catch (e) {
          settleResult(() => Promise.reject(e));
          throw e;
        } finally {
          // Left the loop before the answer: the call is stopped, and its result says so.
          settleResult(() => Promise.reject(new CmdopError("cancelled", "the call was stopped by its caller")));
          stop.abort();
        }
      },
      get result() {
        if (!iterated) {
          iterated = true;
          void (async () => {
            try {
              const g = await start();
              for (;;) {
                const n = await g.next();
                if (n.done) return finish(n.value);
              }
            } catch (e) {
              settleResult(() => Promise.reject(e));
            }
          })();
        }
        return done;
      },
    };
  }

  function machine(name?: string): Machine {
    const at = (o?: Omit<CallOpts, "machine">): CallOpts => ({ ...o, ...(name === undefined ? {} : { machine: name }) });
    const out: Record<string, unknown> = {};
    for (const tool of TOOL_NAMES) out[tool] = (args: never, o?: Omit<CallOpts, "machine">) => call(tool, args, at(o));
    for (const [group, methods] of Object.entries(GROUPS)) {
      out[group] = Object.fromEntries(Object.entries(methods).map(([method, tool]) => [method, out[tool]]));
    }
    for (const f of FORMS) {
      out[f.name] = (...given: unknown[]) => {
        const n = f.positional.length;
        const rest = (given[n] ?? {}) as Record<string, unknown>;
        const args = { ...rest, ...Object.fromEntries(f.positional.map((p, i) => [p, given[i]])) } as never;
        const o = at(given[n + 1] as Omit<CallOpts, "machine"> | undefined);
        return f.stream ? stream(f.tool, args, o) : call(f.tool, args, o).then((r) => DECODE[f.result](r as never));
      };
    }
    return out as Machine;
  }

  async function publicKey(): Promise<string> {
    if (!opts.e2e) throw new CmdopError("bad_args", "this client was made without e2e");
    return opts.e2e.publicKey();
  }

  return { carrier: carrier.name, machines, machine, call, stream, publicKey, close: () => carrier.close() };
}
