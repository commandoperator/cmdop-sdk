// The home folder of the first online machine: a read, nothing changes.
import { connect } from "@cmdop/sdk";

const cmdop = connect();
const box = (await cmdop.machines()).find((m) => m.online);
if (!box) throw new Error("no machine is online");
const home = await cmdop.machine(box.name).fs.list({ path: "~", limit: 10 });
console.log(`${box.name}:${home.path}${home.truncated ? " (first 10)" : ""}`);
for (const e of home.entries) console.log(`  ${e.kind === "dir" ? "d" : "-"} ${e.name}`);
