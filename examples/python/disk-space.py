"""Check whether the selected mount has less than 10% available."""
import json
import os

import cmdop

machine_id = os.environ.get("CMDOP_MACHINE", "").strip()
if not machine_id:
    raise SystemExit("Set CMDOP_MACHINE to the selected machine ID")
mount = os.environ.get("CMDOP_MOUNT", "/")
with cmdop.connect() as client:
    info = client.machine(machine_id).sys.info(deadline=15)

matches = [disk for disk in info.disks if disk.mount == mount]
if len(matches) != 1 or matches[0].total <= 0:
    raise SystemExit(f"Disk measurement unavailable for {mount}")
disk = matches[0]
print(json.dumps({
    "mount": mount,
    "available_gib": round(disk.available / 2**30, 2),
    "below_10_percent": disk.available * 100 < disk.total * 10,
}))
