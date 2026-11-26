import { readFile } from "node:fs/promises";
import { connect } from "@cmdop/sdk";

function setting(key: string): string {
  const value = process.env[key]?.trim();
  if (!value) throw new Error("Set " + key);
  return value;
}

if (setting("EXAMPLES_EXEC") !== "1" || setting("EXAMPLES_NETWORK") !== "1") {
  throw new Error("Enable exec and network for the flight search");
}
const date = setting("FLIGHT_DATE");
const target = setting("CMDOP_MACHINE");
const argv = [setting("FLI_UVX"), "--offline", "--from", "flights[mcp]==0.11.1", "python", "-", date];
const helper = await readFile(new URL("../python/local_mcp/search_flights.py", import.meta.url), "utf8");
const client = connect();
try {
  const result = await client.machine(target).exec_run({ argv, stdin: helper, timeout_secs: 40 }, { deadline: 45000 });
  if (result.exit_code !== 0 || result.signal || result.cancelled || result.truncated || result.timed_out) {
    throw new Error("Flight search failed on the target machine");
  }
  const report = JSON.parse(result.stdout);
  if (report?.date !== date || !Array.isArray(report.flights)) throw new Error("Unexpected flight report");
  console.log(JSON.stringify(report, null, 2));
} finally {
  await client.close();
}
