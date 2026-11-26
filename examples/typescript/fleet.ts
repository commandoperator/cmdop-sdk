// Every machine of the contour, and what each online one is: the first thing a program does.
import { connect } from "@cmdop/sdk";

const cmdop = connect(); // CMDOP_TOKEN, CMDOP_URL
const machines = await cmdop.machines();
console.log(`${machines.length} machines, ${machines.filter((m) => m.online).length} online`);
for (const m of machines.filter((m) => m.online)) {
  const info = await cmdop.machine(m.name).sys.info({});
  const gb = (b: number) => `${(b / 2 ** 30).toFixed(1)} GB`;
  console.log(`  ${m.name}: ${info.os} ${info.os_version ?? ""} ${info.arch}, ${info.cpus} cpus, ${gb(info.memory_available)} of ${gb(info.memory_total)} free`);
}
