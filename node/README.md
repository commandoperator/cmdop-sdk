# @cmdop/sdk (Node)

![@cmdop/sdk — Go-first Node SDK](https://raw.githubusercontent.com/commandoperator/cmdop-sdk/main/assets/hero-cmdop-node.webp)

Typed Node SDK for CMDOP. A **thin** client: it spawns the baked-in `cmdop-core`
Go binary and speaks a protobuf-length-delimited `Envelope` protocol over its
stdio. All relay logic (REST, the `/ask` SSE stream, pin/confirm side-channels,
retries, error mapping) lives in the Go core.

- **No Go toolchain, no `cmdop_go` install** — every platform's `cmdop-core`
  binary is baked into the one package; the right one is selected at runtime
  (no `optionalDependencies`). `npm i @cmdop/sdk` is everything.
- **Pure stdio** — no local port, no socket. Token via `CMDOP_TOKEN` env at spawn.
- **No macOS notarization** — npm-extracted binaries are unquarantined (ad-hoc
  signed only).

## Install

```bash
npm i @cmdop/sdk        # or: pnpm add @cmdop/sdk / yarn add @cmdop/sdk
```

ESM + CJS, Node ≥ 18.

## Quick start

```ts
import { Client } from "@cmdop/sdk";

const c = new Client({ token: "..." });        // or Client.fromEnv()

const page = await c.machines.list({ presence: "online" });
for (const m of page.items) console.log(m.hostname, m.presence);

const text = await c.machines.ask(machineId, "uptime").collect();
console.log(text);

await c.close();                                // reap the core subprocess
```

`await using c = new Client(...)` works too (`Symbol.asyncDispose`).

## Namespaces

The same surface as the relay, mirrored exactly by the Python SDK (camelCase
here, snake_case there):

| Namespace | Methods |
|---|---|
| `machines` | `list · get · update · disable · info · spend · ask · messages · clearMessages · activeSession` |
| `fleets` | `list · get · create · update · disable` |
| `fleets.members` | `list · add · setRole · remove` |
| `fleets.machines` | `list · attach · detach` |
| `tunnels` | `open · close · list · get · sessions` |
| `schedules` | `list · get · create · update · delete · trigger · runs` |
| `keys` | `list · issue · revoke` |
| `skills` | `list · get · my · install · star · versions · reviews · create · update · delete · publish · publishStatus · categories · tags` |

List endpoints also expose `iter(...)` (an async generator over every item,
following cursors) and `pages(...)` (an async generator over each page).

> **Two planes, one client.** `machines / fleets / tunnels / schedules / keys`
> talk to the relay with `CMDOP_TOKEN`; the **`skills`** marketplace lives on the
> platform (Django) and uses the `UserAPIKey` (`CMDOP_API_KEY`). Both are passed
> to the core at spawn; you only set whichever you use.

## Streaming: `machines.ask()`

`ask()` returns an `AskStream` — an async iterable of typed frames with `pin()` /
`confirm()` / `collect()`:

```ts
const stream = c.machines.ask(machineId, "df -h", { sessionId: "s1" });
for await (const frame of stream) {
  if (frame.type === "event") {
    process.stdout.write(String((frame.payload as { delta?: string })?.delta ?? ""));
  } else if (frame.type === "pin_required") {       // machine asked for its connect PIN
    await stream.pin(frame.challengeId, "1234");
  } else if (frame.type === "confirm_required") {    // a dangerous plan awaits approval
    await stream.confirm(frame.token, true);
  } else if (frame.type === "pin_denied") {
    console.log("PIN rejected:", frame.reason);
  } else if (frame.type === "done") {
    console.log("\n->", frame.text);
  }
}

// one-shot: drain to the final text
const text = await c.machines.ask(machineId, "uptime").collect();
```

Frame types: `event · done · error · confirm_required · pin_required ·
pin_denied`. An `error` outcome throws `AgentStreamError`.

## Environment variables

| Var | Meaning | Default |
|---|---|---|
| `CMDOP_TOKEN` | relay Bearer token (machines/fleets/…) | — (required for relay ops) |
| `CMDOP_BASE_URL` | relay REST root | `https://cloud.cmdop.com` |
| `CMDOP_API_KEY` | platform `UserAPIKey` (for `skills`) | — (required for skills) |
| `CMDOP_API_BASE_URL` | platform REST root | `https://api.cmdop.com` |
| `CMDOP_FLEET_ID` | default fleet for fleet-scoped ops | none |
| `CMDOP_TIMEOUT_MS` | per-call timeout | `30000` |
| `CMDOP_CORE_BINARY` | override the baked binary (dev / offline) | baked binary |

Precedence is always explicit option > env var > default. Pass a string to the
constructor (`new Client("token")`) as a shorthand for `{ token }`.

## Error handling

The core emits a terminal `ERROR` frame; the client maps its `code` to a typed
error (all extend `CmdopError`):

```ts
import {
  AuthError, PermissionError, NotFoundError, ConflictError,
  ValidationError, RateLimitError, ServerError, ConnectionError,
  AgentStreamError, CmdopError,
} from "@cmdop/sdk";

try {
  await c.machines.get("missing-id");
} catch (e) {
  if (e instanceof NotFoundError) { /* ... */ }
  else if (e instanceof CmdopError) console.log(e.code, e.message);
}
```

`ConnectionError` also covers the core process dying mid-call (pending
promises reject). `AgentStreamError` is the streaming-`ask` error outcome.

## Using your own core binary

Released packages bake in every platform's binary, picked automatically at spawn.
To point the client at a specific `cmdop-core` instead — an offline mirror, a
pinned build, an air-gapped host — set `CMDOP_CORE_BINARY` to its path:

```bash
CMDOP_CORE_BINARY=/opt/cmdop/cmdop-core CMDOP_TOKEN=... node your_app.js
```
