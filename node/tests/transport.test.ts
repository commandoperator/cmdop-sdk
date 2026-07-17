import { PassThrough } from "node:stream";
import { create } from "@bufbuild/protobuf";
import { sizeDelimitedDecodeStream, sizeDelimitedEncode } from "@bufbuild/protobuf/wire";
import { describe, expect, it } from "vitest";
import { resolveConfig } from "../src/config";
import { AgentStreamError, AuthError, ConnectionError } from "../src/errors";
import { Transport } from "../src/transport";
import {
  AskStreamErrorCode,
  ErrorCode,
  type Envelope,
  Envelope_Kind,
  EnvelopeSchema,
} from "../src/_proto/cmdop/core/v2/contract_pb";

function setup() {
  const requests = new PassThrough();
  const responses = new PassThrough();
  const transport = new Transport(resolveConfig({ token: "t", baseUrl: "https://relay", timeoutMs: 1000 }), "/none");
  transport.attachStreamsForTest(requests, responses);
  return {
    transport,
    requests: sizeDelimitedDecodeStream(EnvelopeSchema, requests),
    feed: (envelope: Envelope) => responses.write(sizeDelimitedEncode(EnvelopeSchema, envelope)),
  };
}

async function request(requests: AsyncGenerator<Envelope>): Promise<Envelope> {
  const next = await requests.next();
  if (next.done) throw new Error("missing request");
  return next.value;
}

describe("v2 transport", () => {
  it("round-trips unary responses and maps typed errors", async () => {
    const fixture = setup();
    const call = fixture.transport.callUnary(
      create(EnvelopeSchema, { payload: { case: "systemBootstrapReq", value: {} } }),
    );
    let req = await request(fixture.requests);
    fixture.feed(
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.RESPONSE,
        payload: { case: "systemBootstrapResp", value: { bundleId: "bundle" } },
      }),
    );
    expect((await call).payload.value).toMatchObject({ bundleId: "bundle" });

    const failed = fixture.transport.callUnary(
      create(EnvelopeSchema, { payload: { case: "listMachinesReq", value: {} } }),
    );
    req = await request(fixture.requests);
    fixture.feed(
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.ERROR,
        payload: { case: "error", value: { code: ErrorCode.UNAUTHENTICATED, message: "missing token" } },
      }),
    );
    await expect(failed).rejects.toThrowError(AuthError);
    await fixture.transport.close();
  });

  it("collects event deltas and rejects a failed done", async () => {
    let fixture = setup();
    const collected = fixture.transport
      .callStream(create(EnvelopeSchema, { payload: { case: "askMachineReq", value: { machineId: "m1", prompt: "hello" } } }))
      .collect();
    let req = await request(fixture.requests);
    fixture.feed(create(EnvelopeSchema, {
      id: req.id,
      kind: Envelope_Kind.EVENT,
      payload: { case: "askEvent", value: { eventType: 1, payloadJson: '{"delta":"hi"}' } },
    }));
    fixture.feed(create(EnvelopeSchema, {
      id: req.id,
      kind: Envelope_Kind.DONE,
      payload: { case: "askDone", value: { success: true } },
    }));
    expect(await collected).toBe("hi");
    await fixture.transport.close();

    fixture = setup();
    const failed = fixture.transport
      .callStream(create(EnvelopeSchema, { payload: { case: "askMachineReq", value: { machineId: "m1", prompt: "x" } } }))
      .collect();
    req = await request(fixture.requests);
    fixture.feed(create(EnvelopeSchema, {
      id: req.id,
      kind: Envelope_Kind.EVENT,
      payload: { case: "askStreamError", value: { code: AskStreamErrorCode.MACHINE_OFFLINE, message: "offline" } },
    }));
    fixture.feed(create(EnvelopeSchema, {
      id: req.id,
      kind: Envelope_Kind.DONE,
      payload: { case: "askDone", value: { success: false, error: "offline" } },
    }));
    await expect(failed).rejects.toThrowError(AgentStreamError);
    await fixture.transport.close();
  });

  it("round-trips a frame larger than 64 KiB", async () => {
    const fixture = setup();
    const large = "x".repeat(256 * 1024);
    const call = fixture.transport.callUnary(
      create(EnvelopeSchema, { payload: { case: "systemBootstrapReq", value: {} } }),
    );
    const req = await request(fixture.requests);
    fixture.feed(create(EnvelopeSchema, {
      id: req.id,
      kind: Envelope_Kind.RESPONSE,
      payload: { case: "systemBootstrapResp", value: { bundleId: large } },
    }));
    const response = await call;
    expect(response.payload.case === "systemBootstrapResp" && response.payload.value.bundleId.length).toBe(large.length);
    await fixture.transport.close();
  });

  it("rejects requests larger than the core decoder limit locally", async () => {
    const fixture = setup();
    const oversized = fixture.transport.callUnary(
      create(EnvelopeSchema, {
        payload: {
          case: "askMachineReq",
          value: { machineId: "m1", prompt: "x".repeat(4 * 1024 * 1024) },
        },
      }),
    );
    await expect(oversized).rejects.toThrowError(ConnectionError);
    await expect(oversized).rejects.toThrow("request frame exceeds 4194304 bytes");

    const valid = fixture.transport.callUnary(
      create(EnvelopeSchema, { payload: { case: "systemBootstrapReq", value: {} } }),
    );
    const req = await request(fixture.requests);
    fixture.feed(create(EnvelopeSchema, {
      id: req.id,
      kind: Envelope_Kind.RESPONSE,
      payload: { case: "systemBootstrapResp", value: { bundleId: "still-alive" } },
    }));
    expect((await valid).payload.value).toMatchObject({ bundleId: "still-alive" });
    await fixture.transport.close();
  });
});
