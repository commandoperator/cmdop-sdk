# @cmdop/sdk 2.0 (Node)

Typed Node SDK for the current Cmdop machine roster, agent stream, and durable
messages. Requires Node 18 or newer.

## Install

```bash
npm install @cmdop/sdk
```

The package includes `cmdop-core` for supported macOS, Linux, and Windows
hosts. It does not download a runtime on first use.

## Quick start

`new Client()` is the canonical local configuration. The core discovers the
active Cmdop server and credentials from the local Cmdop configuration.

```ts
import { Client } from "@cmdop/sdk";

const client = new Client();
try {
  const bootstrap = await client.system.bootstrap();
  console.log(bootstrap.version, bootstrap.capabilities);

  const snapshot = await client.machines.list();
  for (const machine of snapshot.machines) {
    console.log(machine.machineId, machine.displayName, machine.presence);
  }
} finally {
  await client.close();
}
```

For an explicit remote relay, provide both its URL and bearer token. Constructor
options take precedence over environment variables.

```ts
const client = new Client({ baseUrl: "https://relay.example.com", token: "..." });
```

The equivalent environment variables are `CMDOP_BASE_URL` and `CMDOP_TOKEN`.
A remote URL without a token fails closed. An explicit loopback URL can mint a
local loopback token.

## Public API

| Namespace | Method | Result |
|---|---|---|
| `system` | `await client.system.bootstrap()` | version, bundle, contract range, capabilities, update state |
| `machines` | `await client.machines.list()` | authoritative `MachineRosterSnapshot` |
| `machines` | `client.machines.ask(machineId, prompt, options)` | `AskStream` |
| `machines` | `await client.machines.messages(machineId, options)` | durable `MachineMessageList` |

## Ask streaming and PIN

Pass a connection PIN up front, before consuming the headless stream.

```ts
const stream = client.machines.ask(
  machineId,
  "Summarize the current system load.",
  { pin: "1234", session: "2" },
);

for await (const frame of stream) {
  if (frame.type === "event") console.log(frame.payload);
  else if (frame.type === "error") console.log(frame.code, frame.message);
  else console.log(frame.success, frame.text);
}
```

For the common one-shot case, `collect()` drains the stream and returns final
text. An unsuccessful `done` throws `AgentStreamError`.

```ts
const text = await client.machines.ask(
  machineId,
  "Reply with: pong",
  { pin: "1234" },
).collect();
```

Ask options also include `attachmentIds`, `engine`, `workingDir`,
`projectRootId`, and `model`. A stream is single-consumer and yields only typed
`event`, `error`, and `done` frames.

## Durable messages

```ts
const history = await client.machines.messages(machineId, { session: "2", limit: 100 });
for (const message of history.messages) {
  console.log(message.seq, message.role, message.content);
}
```

`limit` must be between 1 and 500.

## Configuration

| Setting | Constructor | Environment | Default |
|---|---|---|---|
| Relay URL | `baseUrl` | `CMDOP_BASE_URL` | local Cmdop config |
| Bearer token | `token` | `CMDOP_TOKEN` | local Cmdop credentials |
| Timeout | `timeoutMs` | `CMDOP_TIMEOUT_MS` | `30000` |
| Development binary override | `binaryPath` | `CMDOP_CORE_BINARY` | packaged host binary |

Call `await client.close()` when finished. `await using` is also supported on
runtimes configured for explicit resource management.

## Typed errors

Every protocol failure is a `CmdopError` with stable `code`, optional HTTP
`status`, `retryable`, and redacted `details` fields. Common subclasses include
`AuthError`, `PermissionError`, `ValidationError`, `NotFoundError`,
`UnavailableError`, `TimeoutError`, `ConnectionError`, and `AgentStreamError`.

```ts
import { CmdopError } from "@cmdop/sdk";

try {
  await client.machines.messages("missing");
} catch (error) {
  if (error instanceof CmdopError) {
    console.log(error.code, error.status, error.retryable);
  }
}
```

Documentation: [docs.cmdop.com](https://docs.cmdop.com) · Source:
[commandoperator/cmdop-sdk](https://github.com/commandoperator/cmdop-sdk)
