import cmdop

with cmdop.connect() as client:
    online = next((machine for machine in client.machines() if machine["online"]), None)
    if online is None:
        raise RuntimeError("Bring a machine online on your CMDOP page.")
    info = client.machine(online["id"]).sys.info()
    print(info.os, info.arch, info.cpus)
