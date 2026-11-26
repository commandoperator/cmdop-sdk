import { CarrierError, CmdopError, connect, type Client } from "@cmdop/sdk";

export type Profile = Readonly<{ agent: string; prompt: string; expected: string }>;
export const question = {
  prompt: "Reply with exactly CMDOP_AGENT_OK and no other text. Do not use tools.",
  expected: "CMDOP_AGENT_OK",
} as const;

export class ExampleError extends Error {}

export function settings(env: Readonly<Record<string, string | undefined>>): string {
  if (env.AGENT_PROMPT !== "1") throw new ExampleError("opt_in_required: set AGENT_PROMPT=1");
  if (![env.CMDOP_URL, env.CMDOP_TOKEN, env.CMDOP_MACHINE].every((value) => value?.trim())) {
    throw new ExampleError("setup_required: CMDOP_URL, CMDOP_TOKEN, CMDOP_MACHINE");
  }
  return env.CMDOP_MACHINE?.trim() ?? "";
}

export async function prompt(client: Client, machineId: string, profile: Profile) {
  const rows = (await client.machines_list({}, { deadline: 15_000 })).filter((row) => row.id === machineId);
  const target = rows[0];
  if (rows.length !== 1 || target?.state !== "online") throw new ExampleError("target_unavailable");
  if (!["agent_list", "agent_prompt"].every((tool) => target.tools.includes(tool))) {
    throw new ExampleError("agent_tools_unavailable");
  }
  const box = client.machine(machineId);
  const agents = (await box.agent.list({}, { deadline: 15_000 })).agents.filter((row) => row.id === profile.agent);
  const agent = agents[0];
  if (agents.length !== 1 || !agent?.installed) throw new ExampleError("requested_agent_unavailable");
  if (agent.busy) throw new ExampleError("requested_agent_busy");
  if (!["text_only", "read_only"].includes(agent.tier)) throw new ExampleError("unsupported_tier");
  const answer = await box.agent.prompt({
    agent: profile.agent, tier: "text_only", prompt: profile.prompt, wait_secs: 30,
  }, { deadline: 45_000 });
  if (answer.agent !== profile.agent || answer.tier !== "text_only") throw new ExampleError("unexpected_agent_or_tier");
  if (answer.state === "running") {
    return { agent: profile.agent, state: "running", task: answer.task, session: answer.session ?? null };
  }
  if (answer.state !== "done") throw new ExampleError("agent_did_not_finish");
  if ((answer.text ?? "").trim() !== profile.expected) throw new ExampleError("unexpected_answer");
  return { agent: profile.agent, state: "done", answer: profile.expected };
}

export async function main(profile: Profile): Promise<void> {
  try {
    const machineId = settings(process.env);
    const client = connect();
    let result;
    try {
      result = await prompt(client, machineId, profile);
    } finally {
      await client.close();
    }
    console.log(JSON.stringify(result));
    if (result.state === "running") process.exitCode = 3;
  } catch (error) {
    const reason = error instanceof ExampleError ? error.message
      : error instanceof CmdopError ? "CmdopError"
      : error instanceof CarrierError ? "CarrierError" : "unexpected_error";
    console.error(JSON.stringify({ state: "failed", reason }));
    process.exitCode = 1;
  }
}
