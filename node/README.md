# @cmdop/sdk (Node)

![@cmdop/sdk — Node SDK for CMDOP](https://raw.githubusercontent.com/commandoperator/cmdop-sdk/main/assets/hero-cmdop-node.webp)

Typed Node SDK for CMDOP — manage your machines, fleets, tunnels, and schedules,
stream a machine's AI agent, and drive the skills marketplace, all from typed
TypeScript.

📚 **Docs: [docs.cmdop.com](https://docs.cmdop.com)** · [SDK](https://cmdop.com/sdk) ·
[Bots](https://cmdop.com/bots) · [Connect](https://cmdop.com/connect)

![How the CMDOP SDK connects your app to your machines](https://raw.githubusercontent.com/commandoperator/cmdop-sdk/main/assets/diagram-cmdop-sdk.webp)

- **One install, zero dependencies** — `npm i @cmdop/sdk` is everything. No
  native build step, no `optionalDependencies`, nothing fetched on first run.
- **Works anywhere, offline-ready** — a single self-contained package runs the
  same on macOS, Linux, and Windows, including air-gapped hosts.
- **Typed end to end** — full TypeScript types for every resource and response,
  with one clean async streaming API for live agent output.

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

await c.close();                                // release resources
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
> use your relay token (`CMDOP_TOKEN`); the **`skills`** marketplace uses your
> platform API key (`CMDOP_API_KEY`). Set whichever you need — the client routes
> each call to the right plane for you.

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

**Connection PIN.** If a machine requires a PIN, pass it **upfront** — the SDK is
headless, so there's no prompt to answer:

```ts
const text = await c.machines.ask(machineId, "uptime", { pin: "1234" }).collect();
```

A wrong PIN throws `PinDeniedError`; an unverified one throws `PinTimeoutError`
(both extend `PermissionError`, non-retryable). The reactive `stream.pin(...)`
callback above is for interactive use (a human at a prompt). The relay never
stores the PIN — it forwards it once to the target, which verifies it locally.

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

Precedence is always explicit option > env var > default. Pass a string to the
constructor (`new Client("token")`) as a shorthand for `{ token }`.

## Error handling

Every failure surfaces as a typed error carrying a stable `code` (all extend
`CmdopError`):

```ts
import {
  AuthError, PermissionError, NotFoundError, ConflictError,
  ValidationError, RateLimitError, ServerError, ConnectionError,
  TimeoutError, UnavailableError, AgentStreamError, CmdopError,
} from "@cmdop/sdk";

try {
  await c.machines.get("missing-id");
} catch (e) {
  if (e instanceof NotFoundError) { /* ... */ }
  else if (e instanceof CmdopError) {
    if (e.retryable) { /* true on TimeoutError — safe to retry */ }
    console.log(e.code, e.message);
  }
}
```

`ConnectionError` covers a lost connection mid-call (pending promises reject);
`TimeoutError` (a retryable subclass) is a deadline/handshake timeout;
`UnavailableError` means the relay is up but the target agent/machine is offline.
`AgentStreamError` is the streaming-`ask` error outcome.

## Links

- **Docs** → [docs.cmdop.com](https://docs.cmdop.com)
- **SDK** → [cmdop.com/sdk](https://cmdop.com/sdk) · **Bots** →
  [cmdop.com/bots](https://cmdop.com/bots) · **Connect** →
  [cmdop.com/connect](https://cmdop.com/connect)
- [`@cmdop/sdk` on npm](https://www.npmjs.com/package/@cmdop/sdk) ·
  [source](https://github.com/commandoperator/cmdop-sdk)
