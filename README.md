# cmdop — the official SDK for CMDOP

![cmdop SDK — Python + Node](https://raw.githubusercontent.com/commandoperator/cmdop-sdk/main/assets/hero-cmdop-sdk.webp)

Programmatic access to your CMDOP fleet from **Python** and **Node** — manage
machines, fleets, tunnels, and schedules, stream a machine's AI agent live, and
drive the skills marketplace, all behind one typed client.

| | Install | Import |
|---|---|---|
| **Python** | `pip install cmdop` | [`cmdop`](https://pypi.org/project/cmdop/) |
| **Node** | `npm i @cmdop/sdk` | [`@cmdop/sdk`](https://www.npmjs.com/package/@cmdop/sdk) |

Both clients ship in lockstep at the **same version** and expose the **same
surface** — snake_case in Python, camelCase in Node.

📚 **Full documentation: [docs.cmdop.com](https://docs.cmdop.com)** — guides, the
complete API reference, and streaming details. Product pages:
[SDK](https://cmdop.com/sdk) · [Bots](https://cmdop.com/bots) ·
[Connect](https://cmdop.com/connect).

## Why it's easy to adopt

- **One install, zero dependencies.** `pip install cmdop` / `npm i @cmdop/sdk` is
  everything — no native build step, no extra runtime, nothing fetched on first
  run.
- **Works anywhere, offline-ready.** A single self-contained package runs the
  same on macOS, Linux, and Windows, including air-gapped hosts.
- **Typed end to end.** Every resource and response is fully typed, with one clean
  async streaming API for live agent output.

## Quick start

```python
# pip install cmdop
from cmdop import Client

async with Client(token="...") as c:                 # or Client.from_env()
    page = await c.machines.list(presence="online")
    text = await c.machines.ask(machine_id, "uptime").collect()
```

```ts
// npm i @cmdop/sdk
import { Client } from "@cmdop/sdk";

const c = new Client({ token: "..." });              // or Client.fromEnv()
const page = await c.machines.list({ presence: "online" });
const text = await c.machines.ask(machineId, "uptime").collect();
await c.close();
```

## What you can do

| Namespace | What |
|---|---|
| `machines` | list / inspect machines, stream their AI agent (`ask`), read & manage conversations |
| `fleets` | create and manage fleets, members, and machine membership |
| `tunnels` | open / close / inspect tunnels |
| `schedules` | create, trigger, and review scheduled jobs |
| `keys` | issue and revoke access keys |
| `skills` | browse, install, publish, and review skills from the marketplace |

The headline feature is **`machines.ask()`** — stream a machine's AI agent as a
clean async iterator of typed events, with mid-stream PIN and confirmation
prompts surfaced as first-class steps.

> **Two planes, one client.** `machines / fleets / tunnels / schedules / keys` use
> your relay token (`CMDOP_TOKEN`); the **`skills`** marketplace uses your platform
> API key (`CMDOP_API_KEY`). Set whichever you need — the client routes each call
> to the right plane.

## Per-package docs

Full method reference, streaming details, environment variables, and error
handling live in each package's README:

- **Python** → [`python/README.md`](python/README.md)
- **Node** → [`node/README.md`](node/README.md)

## Links

- **Docs** → [docs.cmdop.com](https://docs.cmdop.com)
- **SDK** → [cmdop.com/sdk](https://cmdop.com/sdk) · **Bots** →
  [cmdop.com/bots](https://cmdop.com/bots) · **Connect** →
  [cmdop.com/connect](https://cmdop.com/connect)
- [`cmdop` on PyPI](https://pypi.org/project/cmdop/) ·
  [`@cmdop/sdk` on npm](https://www.npmjs.com/package/@cmdop/sdk)
- [CMDOP](https://cmdop.com)

## License

MIT — see [LICENSE](LICENSE).
