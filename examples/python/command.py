"""A command, waited for and then streamed. It runs on a machine, so `run.sh` runs it only with EXAMPLES_EXEC=1."""

import cmdop

with cmdop.connect() as c:
    box = next((m for m in c.machines() if m["online"]), None)
    if box is None:
        raise SystemExit("no machine is online")
    machine = c.machine(box["name"])
    print(machine.run("uname -a").stdout.strip())
    run = machine.stream("for i in 1 2 3; do echo line $i; done")
    for piece in run:
        print(piece.data, end="")
    print(f"exit {run.result.exit_code}")
