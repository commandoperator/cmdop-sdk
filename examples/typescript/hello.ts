import { connect } from "@cmdop/sdk";

const client = connect();
try {
  const online = (await client.machines()).find((machine) => machine.online);
  if (!online) throw new Error("Bring a machine online on your CMDOP page.");
  const info = await client.machine(online.id).sys.info({});
  console.log(info.os, info.arch, info.cpus);
} finally {
  await client.close();
}
