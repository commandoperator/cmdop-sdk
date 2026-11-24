/**
 * HTTP + NDJSON, the first carrier: `POST /api/v1/call`, `POST /api/v1/call/stream` (one JSON value per line, the
 * answer last) and `GET /api/v1/machines` on the contour's address. Every answer of these routes is shaped like the
 * contract's `Answer`, refusals included, so the HTTP status is never needed to read one. Cancel is closing the
 * request: the server sends the machine the contract's cancel. `gen.ts` checks these paths against `openapi.json`.
 */

import type { Answer, StreamLine } from "../generated/call.gen.ts";
import { CarrierError, type CallOptions, type Carrier, type MachineRow } from "./carrier.ts";
import { readNdjson } from "./ndjson.ts";

export interface HttpOptions {
  /** The contour's base URL, `https://<address>.cmdop.dev`, or a local server's. */
  url: string;
  token: string;
  /** For tests and other runtimes; the global `fetch` by default. */
  fetch?: typeof fetch;
}

function isAnswer(v: unknown): v is Answer {
  return typeof v === "object" && v !== null && !Array.isArray(v) && ("ok" in v || "error" in v || "sealed" in v);
}

function isRow(v: unknown): v is MachineRow {
  const r = v as Partial<MachineRow> | null;
  return typeof r === "object" && r !== null && typeof r.id === "string" && typeof r.name === "string" && typeof r.online === "boolean";
}

export function httpCarrier(opts: HttpOptions): Carrier {
  const base = opts.url.replace(/\/+$/, "");
  const doFetch = opts.fetch ?? fetch;
  const headers = {
    authorization: `Bearer ${opts.token}`,
    "content-type": "application/json",
    // The server takes writes under /api only with this header (a browser form cannot send it).
    "x-cmdop": "1",
  };
  const fail = (m: string) => new CarrierError("http", m);

  async function request(method: string, path: string, body: unknown, o: CallOptions): Promise<Response> {
    try {
      return await doFetch(`${base}${path}`, {
        method,
        headers,
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
        ...(o.signal ? { signal: o.signal } : {}),
      });
    } catch (e) {
      if (o.signal?.aborted) throw o.signal.reason ?? e;
      throw fail(`could not reach ${base}: ${String(e)}`);
    }
  }

  async function answerOf(res: Response): Promise<Answer> {
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      throw fail(`server answered ${res.status} without JSON`);
    }
    if (!isAnswer(body)) throw fail(`server answered ${res.status} without a call answer`);
    return body;
  }

  return {
    name: "http",
    async call(req, o) {
      return answerOf(await request("POST", "/api/v1/call", req, o));
    },
    async *stream(req, o) {
      const res = await request("POST", "/api/v1/call/stream", req, o);
      // A refusal before the call was sent comes as one JSON answer, not a stream.
      if (!res.ok || !res.body) {
        yield await answerOf(res);
        return;
      }
      const lines: StreamLine[] = [];
      let wake: (() => void) | undefined;
      let done = false;
      let failed: unknown;
      void readNdjson<StreamLine>(res.body, (l) => {
        lines.push(l);
        wake?.();
      })
        .catch((e: unknown) => {
          failed = e;
        })
        .finally(() => {
          done = true;
          wake?.();
        });
      for (;;) {
        const next = lines.shift();
        if (next !== undefined) {
          yield next;
          continue;
        }
        if (done) break;
        await new Promise<void>((r) => (wake = r));
        wake = undefined;
      }
      if (failed !== undefined) {
        if (o.signal?.aborted) throw o.signal.reason ?? failed;
        throw fail(`the stream broke: ${String(failed)}`);
      }
    },
    async machines(o) {
      const res = await request("GET", "/api/v1/machines", undefined, o);
      let body: unknown;
      try {
        body = await res.json();
      } catch {
        throw fail(`server answered ${res.status} without JSON for the machine list`);
      }
      if (isAnswer(body)) return body;
      if (!res.ok || !Array.isArray(body) || !body.every(isRow)) throw fail(`server answered ${res.status} without a machine list`);
      return { ok: body as MachineRow[] };
    },
    async close() {},
  };
}
