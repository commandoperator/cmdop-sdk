// The carrier conformance suite (developer SDK S3b): every vector of `exports/sdk/vectors/carrier.json`, written from
// Rust, against every carrier of this package. A carrier that behaves differently on one vector is a defect in it.

import { describe, expect, it } from "vitest";
import { type Carrier } from "../src/carriers/carrier.ts";
import { httpCarrier } from "../src/carriers/http.ts";
import { memoryCarrier } from "../src/carriers/memory.ts";
import { connect } from "../src/client.ts";
import type { StreamLine } from "../src/generated/call.gen.ts";
import { differences, runVector, vectors, type Vector } from "./vectors.ts";

const isAnswer = (l: StreamLine) => "ok" in l || "error" in l || "sealed" in l;
const ended = (v: Vector) => v.door.some(isAnswer);

/** Waits until the caller aborts, then fails as a cut channel does. */
const untilAborted = (signal: AbortSignal | undefined) =>
  new Promise<never>((_, reject) => {
    if (signal?.aborted) reject(signal.reason);
    signal?.addEventListener("abort", () => reject(signal.reason), { once: true });
  });

/** The vector's door in memory. A door that gives no answer either hangs until cancelled or drops the channel. */
function memory(v: Vector): Carrier {
  return memoryCarrier({
    async *serve(_req, signal) {
      for (const l of v.door) yield l;
      if (ended(v)) return;
      if (v.cancel_after_pieces !== undefined) await untilAborted(signal);
      throw new Error("connection dropped");
    },
  });
}

/** The vector's door over HTTP: a one-shot call gets its answer as JSON, a streamed one as NDJSON lines. */
function http(v: Vector): Carrier {
  const f: typeof fetch = async (input, init) => {
    const request = input instanceof Request ? input : new Request(input, init);
    const signal = init?.signal ?? undefined;
    const answer = v.door.find(isAnswer);
    if (!request.url.endsWith("/call/stream")) {
      if (!answer) return new Response("", { status: 502 });
      return Response.json(answer, { status: "ok" in answer ? 200 : 400 });
    }
    const enc = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      start(c) {
        for (const l of v.door) c.enqueue(enc.encode(JSON.stringify(l) + "\n"));
        if (ended(v)) c.close();
        else if (v.cancel_after_pieces !== undefined) untilAborted(signal).catch((e: unknown) => c.error(e));
        // After what was sent has arrived: `error()` at once would discard the queued lines too.
        else setTimeout(() => c.error(new TypeError("connection dropped")), 5);
      },
    });
    return new Response(body, { status: 200, headers: { "content-type": "application/x-ndjson" } });
  };
  return httpCarrier({ url: "https://door.test", token: "cmdop_test", fetch: f });
}

describe.each([
  ["memory", memory],
  ["http", http],
] as const)("carrier %s", (_name, make) => {
  it.each(vectors.map((v) => [v.name, v] as const))("%s", async (_n, v) => {
    expect(differences(v, await runVector(v, connect({ carrier: make(v) })))).toEqual([]);
  });
});
