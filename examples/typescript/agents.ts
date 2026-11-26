// Discovery only. Named prompt examples require separate explicit selection and opt-in.
import { connect } from "@cmdop/sdk";

const client = connect();
try {
  for (const row of await client.machines_list({})) {
    if (row.state !== "online" || !row.tools.includes("agent_list")) continue;
    const listing = await client.machine(row.id).agent.list({});
    console.log(row.name, listing.agents.map((agent) => [agent.id, agent.tier, agent.busy]));
  }
} finally {
  await client.close();
}
