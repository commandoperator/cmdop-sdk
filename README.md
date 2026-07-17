# Cmdop SDK 2.0

Official typed SDK for the current Cmdop machine roster, agent stream, and
durable messages. Python `cmdop` and Node `@cmdop/sdk` expose the same async v2
surface.

| Language | Install | Guide |
|---|---|---|
| Python | `pip install cmdop` | [`sdk/python/README.md`](sdk/python/README.md) |
| Node | `npm install @cmdop/sdk` | [`sdk/node/README.md`](sdk/node/README.md) |

Both packages include the `cmdop-core` process for supported macOS, Linux, and
Windows hosts. The language client and core communicate using a private,
length-delimited protobuf protocol over stdio.

## Local quick start

`Client()` is the canonical configuration. It uses the active local Cmdop
server and credentials, so application code does not need to collect setup
fields that Cmdop already owns.

```python
from cmdop import Client

async with Client() as client:
    bootstrap = await client.system.bootstrap()
    snapshot = await client.machines.list()
    for machine in snapshot.machines:
        print(machine.machine_id, machine.display_name)
```

```ts
import { Client } from "@cmdop/sdk";

const client = new Client();
try {
  const bootstrap = await client.system.bootstrap();
  const snapshot = await client.machines.list();
  for (const machine of snapshot.machines) {
    console.log(machine.machineId, machine.displayName);
  }
} finally {
  await client.close();
}
```

To select an explicit remote relay, provide `CMDOP_BASE_URL` and
`CMDOP_TOKEN`, or their matching constructor fields. A remote URL without a
token fails closed.

## Public surface

| Capability | Python and Node |
|---|---|
| Bootstrap discovery | `client.system.bootstrap()` |
| Authoritative machine snapshot | `client.machines.list()` |
| One-machine agent stream | `client.machines.ask(...)` |
| Durable machine history | `client.machines.messages(...)` |

Ask accepts typed session, attachment, engine, working-directory, project-root,
model, and connection-PIN options. Supply PIN before streaming begins. The
single-consumer stream yields `event`, `error`, and terminal `done` frames;
`collect()` returns final text or raises `AgentStreamError`.

## Development checks

```bash
buf lint core/proto
python3 core/parity/check.py --require-go
cd sdk/python && uv run pytest -q
cd ../node && pnpm exec vitest run
cd ../.. && python3 scripts/check_docs.py
```

The capability matrix at `core/parity/capabilities.v2.json` is the public API
authority. Generated proto outputs are never edited by hand.

Documentation: [docs.cmdop.com](https://docs.cmdop.com) · License:
[MIT](LICENSE)
