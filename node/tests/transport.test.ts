/**
 * Transport demux tests: drive the transport off an in-process stdin/stdout
 * pair (no real cmdop-core), asserting unary + streamed-ask (all frame types) +
 * pin/confirm round-trip. Mirror of the Python `test_transport.py`.
 */

import { PassThrough } from "node:stream";
import { create } from "@bufbuild/protobuf";
import {
  sizeDelimitedDecodeStream,
  sizeDelimitedEncode,
} from "@bufbuild/protobuf/wire";
import { describe, expect, it } from "vitest";
import { resolveConfig } from "../src/config";
import {
  AgentStreamError,
  AuthError,
  ConflictError,
  ConnectionError,
  NotFoundError,
  PermissionError,
  RateLimitError,
  ServerError,
  ValidationError,
} from "../src/errors";
import { Transport } from "../src/transport";
import {
  type Envelope,
  Envelope_Kind,
  EnvelopeSchema,
} from "../src/_proto/cmdop/core/v1/envelope_pb";

function makeTransport(): {
  t: Transport;
  feed: (env: Envelope) => void;
  reqs: AsyncGenerator<Envelope>;
  crash: () => void;
} {
  const toCore = new PassThrough(); // client -> core (transport writes here)
  const fromCore = new PassThrough(); // core -> client (transport reads here)
  const t = new Transport(resolveConfig({ token: "t", baseUrl: "https://x" }), "/nope");
  t.attachStreamsForTest(toCore, fromCore);
  // Expose the raw core->client stream for chunk-boundary tests.
  (t as unknown as { __fromCore: PassThrough }).__fromCore = fromCore;

  const feed = (env: Envelope) => {
    fromCore.write(sizeDelimitedEncode(EnvelopeSchema, env));
  };
  // crash: EOF the core->client stream → the read loop ends → all pending fail.
  const crash = () => {
    fromCore.end();
  };
  const reqs = sizeDelimitedDecodeStream(EnvelopeSchema, toCore);
  return { t, feed, reqs, crash };
}

async function nextReq(reqs: AsyncGenerator<Envelope>): Promise<Envelope> {
  const { value, done } = await reqs.next();
  if (done) throw new Error("no request");
  return value;
}

describe("transport demux", () => {
  it("unary response round-trip", async () => {
    const { t, feed, reqs } = makeTransport();
    const p = t.callUnary(
      create(EnvelopeSchema, {
        payload: { case: "listMachinesReq", value: { presence: "any" } },
      }),
    );
    const req = await nextReq(reqs);
    expect(req.kind).toBe(Envelope_Kind.REQUEST);
    expect(req.payload.case).toBe("listMachinesReq");
    feed(
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.RESPONSE,
        payload: {
          case: "machineList",
          value: { items: [{ id: "m1", hostname: "work" }] },
        },
      }),
    );
    const env = await p;
    expect(env.payload.case).toBe("machineList");
    await t.close();
  });

  it("unary error maps to typed exception", async () => {
    const { t, feed, reqs } = makeTransport();
    const p = t.callUnary(
      create(EnvelopeSchema, { payload: { case: "getMachineReq", value: { machineId: "x" } } }),
    );
    const req = await nextReq(reqs);
    feed(
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.ERROR,
        payload: { case: "error", value: { code: "auth", message: "missing token" } },
      }),
    );
    await expect(p).rejects.toThrowError(AuthError);
    await expect(p).rejects.toThrow(/missing token/);
    await t.close();
  });

  it("ask stream: all frame types with pin + confirm", async () => {
    const { t, feed, reqs } = makeTransport();
    const stream = t.callStream(
      create(EnvelopeSchema, { payload: { case: "askReq", value: { machineId: "m1", prompt: "x" } } }),
    );

    const kinds: string[] = [];
    const consume = (async () => {
      for await (const frame of stream) {
        kinds.push(frame.type);
        if (frame.type === "pin_required") await stream.pin(frame.challengeId, "1234");
        else if (frame.type === "confirm_required") await stream.confirm(frame.token, true);
        else if (frame.type === "done") {
          expect(frame.text).toBe("hi done");
          expect(frame.durationMs).toBe(42);
        }
      }
    })();

    const req = await nextReq(reqs);
    expect(req.payload.case).toBe("askReq");
    const id = req.id;
    const ev = (json: string) =>
      feed(
        create(EnvelopeSchema, {
          id,
          kind: Envelope_Kind.EVENT,
          payload: {
            case: "askFrame",
            value: { frame: { case: "event", value: { eventType: 1, payloadJson: json } } },
          },
        }),
      );

    ev('{"delta":"hi "}');
    feed(
      create(EnvelopeSchema, {
        id,
        kind: Envelope_Kind.CALLBACK,
        payload: { case: "pinRequired", value: { challengeId: "c9", label: "Connect PIN" } },
      }),
    );
    const pinAns = await nextReq(reqs);
    expect(pinAns.kind).toBe(Envelope_Kind.ANSWER);
    expect(pinAns.payload.case === "pinAnswer" && pinAns.payload.value.pin).toBe("1234");

    feed(
      create(EnvelopeSchema, {
        id,
        kind: Envelope_Kind.EVENT,
        payload: {
          case: "askFrame",
          value: { frame: { case: "pinDenied", value: { challengeId: "c9", reason: "bad" } } },
        },
      }),
    );
    feed(
      create(EnvelopeSchema, {
        id,
        kind: Envelope_Kind.CALLBACK,
        payload: { case: "confirmRequired", value: { token: "tok", plan: "rm -rf", dangerLevel: "high" } },
      }),
    );
    const confAns = await nextReq(reqs);
    expect(confAns.kind).toBe(Envelope_Kind.ANSWER);
    expect(confAns.payload.case === "confirmAnswer" && confAns.payload.value.accept).toBe(true);

    ev('{"delta":"done"}');
    feed(
      create(EnvelopeSchema, {
        id,
        kind: Envelope_Kind.DONE,
        payload: { case: "done", value: { success: true, text: "hi done", durationMs: 42 } },
      }),
    );

    await consume;
    expect(kinds).toEqual([
      "event",
      "pin_required",
      "pin_denied",
      "confirm_required",
      "event",
      "done",
    ]);
    await t.close();
  });

  it("ask stream: error frame raises AgentStreamError", async () => {
    const { t, feed, reqs } = makeTransport();
    const stream = t.callStream(
      create(EnvelopeSchema, { payload: { case: "askReq", value: { machineId: "m1", prompt: "x" } } }),
    );
    const consume = (async () => {
      for await (const _ of stream) {
        /* drain */
      }
    })();
    const req = await nextReq(reqs);
    feed(
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.ERROR,
        payload: { case: "error", value: { code: "connection", message: "machine offline" } },
      }),
    );
    await expect(consume).rejects.toThrowError(AgentStreamError);
    await t.close();
  });

  it("collect accumulates event deltas", async () => {
    const { t, feed, reqs } = makeTransport();
    const stream = t.callStream(
      create(EnvelopeSchema, { payload: { case: "askReq", value: { machineId: "m1", prompt: "x" } } }),
    );
    const collected = stream.collect();
    const req = await nextReq(reqs);
    const id = req.id;
    const ev = (json: string) =>
      feed(
        create(EnvelopeSchema, {
          id,
          kind: Envelope_Kind.EVENT,
          payload: {
            case: "askFrame",
            value: { frame: { case: "event", value: { eventType: 1, payloadJson: json } } },
          },
        }),
      );
    ev('{"delta":"foo"}');
    ev('{"delta":"bar"}');
    feed(
      create(EnvelopeSchema, {
        id,
        kind: Envelope_Kind.DONE,
        payload: { case: "done", value: { success: true } },
      }),
    );
    expect(await collected).toBe("foobar");
    await t.close();
  });

  it("large frame (>64KB) round-trips whole", async () => {
    // The report-11 §2.2 regression guard: sizeDelimitedDecodeStream has no
    // readline cap, so a single oversized frame reassembles whole.
    const { t, feed, reqs } = makeTransport();
    const big = "z".repeat(256 * 1024); // 256 KB
    const stream = t.callStream(
      create(EnvelopeSchema, { payload: { case: "askReq", value: { machineId: "m1", prompt: big } } }),
    );
    let deltas = "";
    const consume = (async () => {
      for await (const frame of stream) {
        if (frame.type === "event") deltas += (frame.payload as { delta?: string })?.delta ?? "";
      }
    })();

    const req = await nextReq(reqs);
    // The big prompt round-tripped in too.
    expect(req.payload.case === "askReq" && req.payload.value.prompt.length).toBe(big.length);
    const id = req.id;
    feed(
      create(EnvelopeSchema, {
        id,
        kind: Envelope_Kind.EVENT,
        payload: {
          case: "askFrame",
          value: { frame: { case: "event", value: { eventType: 1, payloadJson: JSON.stringify({ delta: big }) } } },
        },
      }),
    );
    feed(
      create(EnvelopeSchema, {
        id,
        kind: Envelope_Kind.DONE,
        payload: { case: "done", value: { success: true } },
      }),
    );
    await consume;
    expect(deltas.length).toBe(big.length);
    await t.close();
  });

  it("split frame across chunk boundaries reassembles", async () => {
    // Write a single encoded frame in two raw chunks: sizeDelimitedDecodeStream
    // must reassemble it. Proves the decoder is chunk-boundary safe.
    const { t, reqs } = makeTransport();
    const p = t.callUnary(
      create(EnvelopeSchema, { payload: { case: "getMachineReq", value: { machineId: "x" } } }),
    );
    const req = await nextReq(reqs);

    const full = sizeDelimitedEncode(
      EnvelopeSchema,
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.RESPONSE,
        payload: { case: "machineDetail", value: { id: "m1", hostname: "split-host" } },
      }),
    );
    // Split the bytes mid-frame and write the halves separately.
    const mid = Math.floor(full.length / 2);
    // Access the same fromCore PassThrough used by `feed`: re-create a feeder.
    // makeTransport's `feed` writes whole frames; here we need raw chunked writes,
    // so reach the underlying stream via a fresh transport wired the same way.
    // Simplest: write both halves through the public feed by re-encoding — but to
    // truly test chunking we write raw halves on the fromCore stream.
    (t as unknown as { __fromCore?: { write: (b: Uint8Array) => void } }).__fromCore?.write(
      full.subarray(0, mid),
    );
    (t as unknown as { __fromCore?: { write: (b: Uint8Array) => void } }).__fromCore?.write(
      full.subarray(mid),
    );

    const env = await p;
    expect(env.payload.case).toBe("machineDetail");
    await t.close();
  });

  it("core crash rejects pending unary call", async () => {
    const { t, reqs, crash } = makeTransport();
    const p = t.callUnary(
      create(EnvelopeSchema, { payload: { case: "listMachinesReq", value: {} } }),
    );
    await nextReq(reqs); // received, then the core dies
    crash();
    await expect(p).rejects.toThrowError(ConnectionError);
    await t.close();
  });

  it("core crash raises on an open stream", async () => {
    const { t, feed, reqs, crash } = makeTransport();
    const stream = t.callStream(
      create(EnvelopeSchema, { payload: { case: "askReq", value: { machineId: "m1", prompt: "x" } } }),
    );
    const consume = (async () => {
      for await (const _ of stream) {
        /* drain */
      }
    })();
    const req = await nextReq(reqs);
    feed(
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.EVENT,
        payload: {
          case: "askFrame",
          value: { frame: { case: "event", value: { eventType: 1, payloadJson: '{"delta":"hi"}' } } },
        },
      }),
    );
    crash();
    await expect(consume).rejects.toThrowError(ConnectionError);
    await t.close();
  });

  it.each([
    ["auth", AuthError],
    ["permission", PermissionError],
    ["not_found", NotFoundError],
    ["conflict", ConflictError],
    ["validation", ValidationError],
    ["rate_limit", RateLimitError],
    ["server", ServerError],
    ["connection", ConnectionError],
  ] as const)("unary error code %s maps to its typed exception", async (code, Ctor) => {
    const { t, feed, reqs } = makeTransport();
    const p = t.callUnary(
      create(EnvelopeSchema, { payload: { case: "getMachineReq", value: { machineId: "x" } } }),
    );
    const req = await nextReq(reqs);
    feed(
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.ERROR,
        payload: { case: "error", value: { code, message: "boom" } },
      }),
    );
    await expect(p).rejects.toThrowError(Ctor);
    await expect(p).rejects.toThrow(/boom/);
    await t.close();
  });
});
