# cmdop 2.0 (Python)

Async Python SDK for the current Cmdop machine roster, agent stream, and
durable messages.

## Install

```bash
pip install cmdop
```

The package includes `cmdop-core` for supported macOS, Linux, and Windows
hosts. It does not download a runtime on first use.

## Quick start

`Client()` is the canonical local configuration. The core discovers the active
Cmdop server and credentials from the local Cmdop configuration.

```python
import asyncio

from cmdop import Client


async def main() -> None:
    async with Client() as client:
        bootstrap = await client.system.bootstrap()
        print(bootstrap.version, bootstrap.capabilities)

        snapshot = await client.machines.list()
        for machine in snapshot.machines:
            print(machine.machine_id, machine.display_name, machine.presence)


asyncio.run(main())
```

For an explicit remote relay, provide both its URL and bearer token. Constructor
arguments take precedence over environment variables.

```python
async with Client(base_url="https://relay.example.com", token="...") as client:
    snapshot = await client.machines.list()
```

The equivalent environment variables are `CMDOP_BASE_URL` and `CMDOP_TOKEN`.
A remote URL without a token fails closed. An explicit loopback URL can mint a
local loopback token.

## Public API

| Namespace | Method | Result |
|---|---|---|
| `system` | `await client.system.bootstrap()` | version, bundle, contract range, capabilities, update state |
| `machines` | `await client.machines.list()` | authoritative `MachineRosterSnapshot` |
| `machines` | `client.machines.ask(machine_id, prompt, ...)` | `AskStream` |
| `machines` | `await client.machines.messages(machine_id, ...)` | durable `MachineMessageList` |

## Ask streaming and PIN

Pass a connection PIN up front, before consuming the headless stream.

```python
async with Client() as client:
    stream = client.machines.ask(
        machine_id,
        "Summarize the current system load.",
        pin="1234",
        session="2",
    )

    async for frame in stream:
        if frame.type == "event":
            print(frame.payload)
        elif frame.type == "error":
            print(frame.code, frame.message)
        elif frame.type == "done":
            print(frame.success, frame.text)
```

For the common one-shot case, `collect()` drains the stream and returns final
text. An unsuccessful `done` raises `AgentStreamError`.

```python
text = await client.machines.ask(machine_id, "Reply with: pong", pin="1234").collect()
```

`ask()` also accepts `attachment_ids`, `engine`, `working_dir`,
`project_root_id`, and `model`. A stream is single-consumer and yields only
typed `event`, `error`, and `done` frames.

## Durable messages

```python
history = await client.machines.messages(machine_id, session="2", limit=100)
for message in history.messages:
    print(message.seq, message.role, message.content)
```

`limit` must be between 1 and 500.

## Configuration

| Setting | Constructor | Environment | Default |
|---|---|---|---|
| Relay URL | `base_url` | `CMDOP_BASE_URL` | local Cmdop config |
| Bearer token | `token` | `CMDOP_TOKEN` | local Cmdop credentials |
| Timeout | `timeout_ms` | `CMDOP_TIMEOUT_MS` | `30000` |
| Development binary override | `binary_path` | `CMDOP_CORE_BINARY` | packaged host binary |

Use `async with Client()` or call `await client.aclose()` when finished.

## Typed errors

Every protocol failure is a `CmdopError` with stable `code`, optional HTTP
`status`, `retryable`, and redacted `details` fields. Common subclasses include
`AuthError`, `PermissionError`, `ValidationError`, `NotFoundError`,
`UnavailableError`, `TimeoutError`, `ConnectionError`, and `AgentStreamError`.

```python
from cmdop import CmdopError

try:
    await client.machines.messages("missing")
except CmdopError as error:
    print(error.code, error.status, error.retryable)
```

Documentation: [docs.cmdop.com](https://docs.cmdop.com) · Source:
[commandoperator/cmdop-sdk](https://github.com/commandoperator/cmdop-sdk)
