// Bounded POSIX fixture, explicit target and opt-in; a remote nonzero result cannot pass.
import { connect, type ExecRunOut } from "@cmdop/sdk";

function successful(result: ExecRunOut): void {
  if (result.exit_code !== 0 || result.signal != null || result.timed_out || result.cancelled || result.truncated) {
    throw new Error("command_not_successful");
  }
}

if (process.env.EXAMPLES_EXEC !== "1") throw new Error("opt_in_required: EXAMPLES_EXEC=1");
const target = process.env.CMDOP_MACHINE?.trim();
if (!target) throw new Error("explicit_machine_id_required");
const client = connect();
try {
  const rows = (await client.machines_list({})).filter((row) => row.id === target && row.state === "online");
  const row = rows[0];
  if (rows.length !== 1 || !row?.tools.includes("exec_run") || !["macos", "linux"].includes(row.os)) {
    throw new Error("target_unavailable_or_unsupported");
  }
  const machine = client.machine(target);
  const result = await machine.exec_run({ argv: ["uname", "-s"], timeout_secs: 10 }, { deadline: 15_000 });
  successful(result);
  if (!result.stdout.trim()) throw new Error("missing_system_name");
  const run = machine.stream("for i in 1 2 3; do echo line $i; done", { timeout_secs: 10 }, { deadline: 15_000 });
  const chunks: string[] = [];
  for await (const piece of run) if (piece.stream === "stdout") chunks.push(piece.data);
  successful(await run.result);
  if (chunks.join("").replaceAll("\r\n", "\n") !== "line 1\nline 2\nline 3\n") {
    throw new Error("unexpected_stream_output");
  }
  console.log("command result and streamed fixture verified");
} finally {
  await client.close();
}
