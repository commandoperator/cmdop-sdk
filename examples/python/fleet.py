"""Inspect available computers and show why others could not be inspected."""
import cmdop

failed = False
with cmdop.connect() as client:
    machines = client.machines_list(deadline=15)
    print(f"{len(machines)} machines")
    for machine in machines:
        label = f"{machine.name} ({machine.id})"
        if machine.state != "online":
            print(f"  {label}: {machine.state}")
            continue
        if "sys_info" not in machine.tools:
            print(f"  {label}: sys_info unavailable")
            continue
        try:
            info = client.machine(machine.id).sys.info(deadline=15)
        except (cmdop.CmdopError, cmdop.CarrierError) as error:
            reason = error.code if isinstance(error, cmdop.CmdopError) else "connection error"
            print(f"  {label}: {reason}")
            failed = True
            continue
        print(f"  {label}: {info.os} {info.arch}, {info.cpus} CPUs, "
              f"{info.memory_available / 2**30:.1f} of {info.memory_total / 2**30:.1f} GiB available")
if failed:
    raise SystemExit(1)
