"""The home folder of the first online machine: a read, nothing changes."""

import cmdop

with cmdop.connect() as c:
    box = next((m for m in c.machines() if m["online"]), None)
    if box is None:
        raise SystemExit("no machine is online")
    home = c.machine(box["name"]).fs.list(path="~", limit=10)
    print(f"{box['name']}:{home.path}{' (first 10)' if home.truncated else ''}")
    for e in home.entries:
        print(f"  {'d' if e.kind == 'dir' else '-'} {e.name}")
