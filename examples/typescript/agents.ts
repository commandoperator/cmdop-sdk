// The AI agent programs on each online machine (Claude Code, Codex), and with AGENT_PROMPT=1 one question to the
// default one. Listing needs a `read` grant; asking needs the `agent` class on the token and in the machine's ceiling.
import { connect } from "@cmdop/sdk";

const cmdop = connect(); // CMDOP_TOKEN, CMDOP_URL
for (const m of (await cmdop.machines()).filter((m) => m.online)) {
  let list;
  try {
    list = await cmdop.machine(m.name).agent.list({});
  } catch (e) {
    console.log(`  ${m.name}: no agent tools (${(e as { code?: string }).code ?? e})`);
    continue;
  }
  const names = list.agents.map((a) => `${a.id} (${a.tier}${a.busy ? ", busy" : ""})`).join(", ");
  console.log(`  ${m.name}: ${names || "no agent allowed"}; default ${list.default ?? "none"}`);
  if (process.env.AGENT_PROMPT === "1" && list.default) {
    const answer = await cmdop.machine(m.name).agent.prompt({ prompt: "In one sentence: what is this machine?" });
    console.log(`    ${answer.agent} ${answer.state}: ${answer.text ?? ""}`);
  }
}
