import { connect } from "@cmdop/sdk";

function required(key: string): string {
  const value = process.env[key]?.trim();
  if (!value) throw new Error("Missing " + key);
  return value;
}

if (required("EXAMPLES_EXEC") !== "1") throw new Error("Set EXAMPLES_EXEC=1");
const target = required("CMDOP_MACHINE");
const argv = [required("LOCAL_MCP_PYTHON"), required("LOCAL_MCP_HELPER")];
const client = connect();
try {
  const result = await client.machine(target).exec_run({ argv, timeout_secs: 60 }, { deadline: 70000 });
  if (result.exit_code !== 0 || result.signal || result.cancelled || result.truncated || result.timed_out) {
    throw new Error("build report unavailable");
  }
  const report = JSON.parse(result.stdout);
  if (report?.job !== "demo-build" || report.tests_passed !== 3 || report.tests_failed !== 0) {
    throw new Error("unexpected build report");
  }
  console.log("demo-build: 3 tests passed");
} finally {
  await client.close();
}
