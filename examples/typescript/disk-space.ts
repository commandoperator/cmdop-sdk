// Check whether the selected mount has less than 10% available.
import { connect } from "@cmdop/sdk";

const machineId = process.env.CMDOP_MACHINE?.trim();
if (!machineId) throw new Error("Set CMDOP_MACHINE to the selected machine ID");
const mount = process.env.CMDOP_MOUNT ?? "/";
const client = connect();
try {
  const info = await client.machine(machineId).sys.info({}, { deadline: 15_000 });
  const matches = info.disks.filter((disk) => disk.mount === mount);
  const disk = matches[0];
  if (matches.length !== 1 || !disk || disk.total <= 0) {
    throw new Error(`Disk measurement unavailable for ${mount}`);
  }
  console.log(JSON.stringify({
    mount,
    available_gib: Number((disk.available / 2 ** 30).toFixed(2)),
    below_10_percent: disk.available * 100 < disk.total * 10,
  }));
} finally {
  await client.close();
}
