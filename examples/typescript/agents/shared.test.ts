import assert from "node:assert/strict";
import { test } from "node:test";
import { connect, memoryCarrier, type CallRequest } from "@cmdop/sdk";
import { prompt, question, settings } from "./shared.js";

async function runCase(options: {
  agent?: string; presence?: string; listed?: string; busy?: boolean;
  state?: string; text?: string; answered?: string;
} = {}) {
  const agent = options.agent ?? "codex";
  const seen: CallRequest[] = [];
  const carrier = memoryCarrier({
    async *serve(req) {
      seen.push(req);
      if (req.tool === "machines_list") yield { ok: [{
        id: "fixture", name: "fixture", online: true, os: "linux", arch: "x86_64", own_name: "fixture",
        dirty: false, epoch: 1, last_seen: 0, program: "0.1.16", since: 0,
        state: options.presence ?? "online", tools: ["agent_list", "agent_prompt"],
      }] };
      else if (req.tool === "agent_list") yield { ok: {
        agents: [{ id: options.listed ?? agent, name: "fixture", protocol: "headless_json",
          installed: true, tier: "text_only", resume: true, busy: options.busy ?? false }],
        default: options.listed ?? agent,
      } };
      else if (req.tool === "agent_prompt") yield { ok: {
        agent: options.answered ?? agent, state: options.state ?? "done", task: 7,
        tier: "text_only", text: options.text ?? "CMDOP_AGENT_OK", session: "fixture-session",
      } };
      else throw new Error("unexpected dispatch");
    },
  });
  const client = connect({ carrier });
  try {
    return { result: await prompt(client, "fixture", { agent, ...question }), seen };
  } catch (error) {
    return { error, seen };
  } finally {
    await client.close();
  }
}

test("explicit opt-in and setup are required", () => {
  assert.throws(() => settings({}), /opt_in_required/);
  assert.throws(() => settings({ AGENT_PROMPT: "1" }), /setup_required/);
});

test("each named agent is sent explicitly with bounded text-only access", async () => {
  for (const agent of ["codex", "claude-code"]) {
    const { result, seen } = await runCase({ agent });
    assert.equal(result?.state, "done");
    assert.deepEqual(seen[2]?.args, { agent, tier: "text_only", prompt: question.prompt, wait_secs: 30 });
    assert.equal(seen[2]?.machine, "fixture");
    assert.equal(seen[2]?.deadline_ms, 45_000);
  }
});

test("absent requested agent never falls back to the default", async () => {
  const { error, seen } = await runCase({ listed: "claude-code" });
  assert.match(String(error), /requested_agent_unavailable/);
  assert.deepEqual(seen.map((r) => r.tool), ["machines_list", "agent_list"]);
});

test("paused online machine stops before agent dispatch", async () => {
  const { error, seen } = await runCase({ presence: "paused" });
  assert.match(String(error), /target_unavailable/);
  assert.equal(seen.length, 1);
});

test("busy agent is not prompted", async () => {
  const { error, seen } = await runCase({ busy: true });
  assert.match(String(error), /requested_agent_busy/);
  assert.equal(seen.length, 2);
});

test("wrong answer, failed/stopped run and wrong responder cannot pass", async () => {
  for (const options of [{ text: "other" }, { state: "failed" }, { state: "stopped" }, { answered: "claude-code" }]) {
    assert.ok((await runCase(options)).error);
  }
});

test("running preserves the handle without a final-answer claim or retry", async () => {
  const { result, seen } = await runCase({ state: "running", text: "" });
  assert.deepEqual(result, { agent: "codex", state: "running", task: 7, session: "fixture-session" });
  assert.equal(seen.length, 3);
});
