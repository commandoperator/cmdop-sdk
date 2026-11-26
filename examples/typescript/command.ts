// A command, waited for and then streamed. It runs on a machine, so `run.sh` runs it only with EXAMPLES_EXEC=1.
import { connect } from "@cmdop/sdk";

const cmdop = connect();
const box = (await cmdop.machines()).find((m) => m.online);
if (!box) throw new Error("no machine is online");
const machine = cmdop.machine(box.name);
console.log((await machine.run("uname -a")).stdout.trim());
const run = machine.stream("for i in 1 2 3; do echo line $i; done");
for await (const piece of run) process.stdout.write(piece.data);
console.log(`exit ${(await run.result).exit_code}`);
