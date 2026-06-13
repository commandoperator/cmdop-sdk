/**
 * skills resource: surface presence + a transport round-trip through a skills
 * op. The transport is driven off an in-process stdin/stdout pair (no real
 * cmdop-core), mirroring `transport.test.ts`. This proves the second-plane
 * (skills) op builds the right Envelope arm and reads the right response arm.
 */

import { PassThrough } from "node:stream";
import { create } from "@bufbuild/protobuf";
import {
  sizeDelimitedDecodeStream,
  sizeDelimitedEncode,
} from "@bufbuild/protobuf/wire";
import { describe, expect, it } from "vitest";
import type { Client } from "../src/client";
import { resolveConfig } from "../src/config";
import { AuthError } from "../src/errors";
import { SkillsResource } from "../src/resources/skills";
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
} {
  const toCore = new PassThrough();
  const fromCore = new PassThrough();
  const t = new Transport(
    resolveConfig({ token: "t", baseUrl: "https://x", apiKey: "cmd_fake" }),
    "/nope",
  );
  t.attachStreamsForTest(toCore, fromCore);
  const feed = (env: Envelope) => {
    fromCore.write(sizeDelimitedEncode(EnvelopeSchema, env));
  };
  const reqs = sizeDelimitedDecodeStream(EnvelopeSchema, toCore);
  return { t, feed, reqs };
}

async function nextReq(reqs: AsyncGenerator<Envelope>): Promise<Envelope> {
  const { value, done } = await reqs.next();
  if (done) throw new Error("no request");
  return value;
}

/** Minimal Client stand-in SkillsResource needs (transport + fleetId). */
function fakeClient(t: Transport): Client {
  return { _t: t, fleetId: undefined } as unknown as Client;
}

describe("skills resource", () => {
  it("apiKey + apiBaseUrl resolve onto the config", () => {
    const cfg = resolveConfig({
      token: "t",
      apiKey: "cmd_xyz",
      apiBaseUrl: "https://api.example",
    });
    expect(cfg.apiKey).toBe("cmd_xyz");
    expect(cfg.apiBaseUrl).toBe("https://api.example");
  });

  it("exposes the full skills method set", () => {
    for (const name of [
      "list",
      "get",
      "my",
      "install",
      "star",
      "versions",
      "reviews",
      "create",
      "update",
      "delete",
      "publish",
      "publishStatus",
      "categories",
      "tags",
    ]) {
      expect(typeof (SkillsResource.prototype as Record<string, unknown>)[name]).toBe(
        "function",
      );
    }
  });

  it("list round-trip builds skillsListReq and reads skillListPage", async () => {
    const { t, feed, reqs } = makeTransport();
    const skills = new SkillsResource(fakeClient(t));
    const p = skills.list({ category: "ai" });
    const req = await nextReq(reqs);
    expect(req.kind).toBe(Envelope_Kind.REQUEST);
    expect(req.payload.case).toBe("skillsListReq");
    if (req.payload.case === "skillsListReq") {
      expect(req.payload.value.category).toBe("ai");
    }
    feed(
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.RESPONSE,
        payload: {
          case: "skillListPage",
          value: { count: 1, page: 1, results: [{ slug: "browser", name: "Browser" }] },
        },
      }),
    );
    const page = await p;
    expect(page.count).toBe(1);
    expect(page.results[0].slug).toBe("browser");
    await t.close();
  });

  it("install 401 maps to a typed AuthError", async () => {
    const { t, feed, reqs } = makeTransport();
    const skills = new SkillsResource(fakeClient(t));
    const p = skills.install("browser");
    const req = await nextReq(reqs);
    expect(req.payload.case).toBe("skillsInstallReq");
    feed(
      create(EnvelopeSchema, {
        id: req.id,
        kind: Envelope_Kind.ERROR,
        payload: { case: "error", value: { code: "auth", message: "invalid api key" } },
      }),
    );
    await expect(p).rejects.toBeInstanceOf(AuthError);
    await t.close();
  });
});
