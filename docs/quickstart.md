# SDK quickstart

List your computers and read system information before enabling command execution.

**In short:** Install `@cmdop/sdk` or `cmdop`, set `CMDOP_URL` and `CMDOP_TOKEN`, then call `machines()` and `sys.info`.

## Before you start

[Install CMDOP](https://cmdop.ai/download) on a macOS or Linux computer and bring it online on your page.
Create a dedicated agent token in the Agents tab with the `read` risk class.
The language package connects to the machine program; it does not install that program.

Set `CMDOP_URL` to `https://<address>.cmdop.dev` and supply `CMDOP_TOKEN` through your
shell environment or secret manager. See [authentication](authentication.md).

## TypeScript: first read

Requires Node.js 20+ and the `read` risk class.

```bash
npm install @cmdop/sdk
```

```ts
import { connect } from "@cmdop/sdk";

const client = connect();
try {
  const machines = await client.machines();
  const online = machines.find((machine) => machine.online);
  if (!online) throw new Error("Bring a machine online on your CMDOP page.");
  const info = await client.machine(online.id).sys.info({});
  console.log(info.os, info.arch, info.cpus);
} finally {
  await client.close();
}
```

## Python: first read

Requires Python 3.10+ and the `read` risk class.

```bash
pip install cmdop
```

```python
import cmdop

with cmdop.connect() as client:
    online = next((machine for machine in client.machines() if machine["online"]), None)
    if online is None:
        raise RuntimeError("Bring a machine online on your CMDOP page.")
    info = client.machine(online["id"]).sys.info()
    print(info.os, info.arch, info.cpus)
```

Both programs print the selected computer's OS, architecture and CPU count.
An illustrative output on an Apple Silicon Mac is:

```text
macos aarch64 8
```

Your values depend on the selected machine. If more than one machine is online, these examples
choose the first; use an explicit name or id when the target matters.

## Next

[TypeScript](typescript.md) · [Python](python.md) ·
[Machines and tools](machines-and-tools.md) ·
[Commands and tasks](commands-and-tasks.md)
