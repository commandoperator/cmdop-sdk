"""Every machine of the contour, and what each online one is: the first thing a program does."""

import cmdop

with cmdop.connect() as c:  # CMDOP_TOKEN, CMDOP_URL
    machines = c.machines()
    online = [m for m in machines if m["online"]]
    print(f"{len(machines)} machines, {len(online)} online")
    for m in online:
        info = c.machine(m["name"]).sys.info()
        gb = lambda b: f"{b / 2**30:.1f} GB"  # noqa: E731
        print(f"  {m['name']}: {info.os} {info.os_version or ''} {info.arch}, {info.cpus} cpus, "
              f"{gb(info.memory_available)} of {gb(info.memory_total)} free")
