// Inspect available computers and show why others could not be inspected.
import { CarrierError, CmdopError, connect } from "@cmdop/sdk";

const client = connect();
try {
  const machines = await client.machines_list({}, { deadline: 15_000 });
  console.log(`${machines.length} machines`);
  for (const machine of machines) {
    const label = `${machine.name} (${machine.id})`;
    if (machine.state !== "online") {
      console.log(`  ${label}: ${machine.state}`);
      continue;
    }
    if (!machine.tools.includes("sys_info")) {
      console.log(`  ${label}: sys_info unavailable`);
      continue;
    }
    try {
      const info = await client.machine(machine.id).sys.info({}, { deadline: 15_000 });
      const gib = (bytes: number) => (bytes / 2 ** 30).toFixed(1);
      console.log(`  ${label}: ${info.os} ${info.arch}, ${info.cpus} CPUs, ${gib(info.memory_available)} of ${gib(info.memory_total)} GiB available`);
    } catch (error) {
      if (!(error instanceof CmdopError || error instanceof CarrierError)) throw error;
      console.log(`  ${label}: ${error instanceof CmdopError ? error.code : "connection error"}`);
      process.exitCode = 1;
    }
  }
} finally {
  await client.close();
}
