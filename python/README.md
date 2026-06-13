# cmdop (Python)

![cmdop — Go-first Python SDK](https://raw.githubusercontent.com/commandoperator/cmdop-sdk/main/assets/hero-cmdop-python.webp)

Async-first Python SDK for CMDOP. A **thin** client: it spawns the baked-in
`cmdop-core` Go binary and speaks a protobuf-length-delimited `Envelope` protocol
over its stdio. All relay logic (REST, the `/ask` SSE stream, pin/confirm
side-channels, retries, error mapping) lives in the Go core.

- **No Go toolchain, no `cmdop_go` install** — every platform's `cmdop-core`
  binary is baked into one wheel; the right one is selected at runtime.
  `pip install cmdop` is everything.
- **Pure stdio** — no local port, no socket. Token via `CMDOP_TOKEN` env at spawn.
- **No macOS notarization** — pip-extracted binaries are unquarantined (ad-hoc
  signed only).

## Install

```bash
pip install cmdop        # or: uv add cmdop
```

## Quick start

```python
from cmdop import Client

async with Client(token="...") as c:        # or Client.from_env()
    page = await c.machines.list(presence="online")
    for m in page.items:
        print(m.hostname, m.presence)

    text = await c.machines.ask(machine_id, "uptime").collect()
    print(text)
```

`Client` is an async context manager — use `async with` so the core subprocess is
reaped on exit (or call `await c.aclose()`).

## Namespaces

The same surface as the relay, mirrored exactly by the Node SDK (snake_case here,
camelCase there):

| Namespace | Methods |
|---|---|
| `machines` | `list · get · update · disable · info · spend · ask · messages · clear_messages · active_session` |
| `fleets` | `list · get · create · update · disable` |
| `fleets.members` | `list · add · set_role · remove` |
| `fleets.machines` | `list · attach · detach` |
| `tunnels` | `open · close · list · get · sessions` |
| `schedules` | `list · get · create · update · delete · trigger · runs` |
| `keys` | `list · issue · revoke` |
| `skills` | `list · get · my · install · star · versions · reviews · create · update · delete · publish · publish_status · categories · tags` |

List endpoints also expose `iter(...)` (yield every item, following cursors) and
`pages(...)` (yield each page).

> **Two planes, one client.** `machines / fleets / tunnels / schedules / keys`
> talk to the relay with `CMDOP_TOKEN`; the **`skills`** marketplace lives on the
> platform (Django) and uses the `UserAPIKey` (`CMDOP_API_KEY`). Both are passed
> to the core at spawn; you only set whichever you use.

## Streaming: `machines.ask()`

`ask()` returns a `FrameStream` (aliased `AskStream`) — an async iterator of
typed frames with `pin()` / `confirm()` / `collect()`:

```python
stream = c.machines.ask(machine_id, "df -h", session_id="s1")
async for frame in stream:
    if frame.type == "event":
        print(frame.payload.get("delta", ""), end="")
    elif frame.type == "pin_required":          # machine asked for its connect PIN
        await stream.pin(frame.challenge_id, "1234")
    elif frame.type == "confirm_required":       # a dangerous plan awaits approval
        await stream.confirm(frame.token, accept=True)
    elif frame.type == "pin_denied":
        print("PIN rejected:", frame.reason)
    elif frame.type == "done":
        print("\n->", frame.text)

# one-shot: drain to the final text
text = await c.machines.ask(machine_id, "uptime").collect()
```

Frame types: `event · done · error · confirm_required · pin_required ·
pin_denied`. An `error` outcome raises `AgentStreamError`.

## Environment variables

| Var | Meaning | Default |
|---|---|---|
| `CMDOP_TOKEN` | relay Bearer token (machines/fleets/…) | — (required for relay ops) |
| `CMDOP_BASE_URL` | relay REST root | `https://cloud.cmdop.com` |
| `CMDOP_API_KEY` | platform `UserAPIKey` (for `skills`) | — (required for skills) |
| `CMDOP_API_BASE_URL` | platform REST root | `https://api.cmdop.com` |
| `CMDOP_FLEET_ID` | default fleet for fleet-scoped ops | none |
| `CMDOP_TIMEOUT_MS` | per-call timeout | `30000` |
| `CMDOP_CORE_BINARY` | override the baked binary (dev / offline) | baked wheel binary |

Precedence is always explicit arg > env var > default.

## Error handling

The core emits a terminal `ERROR` frame; the client maps its `code` to a typed
exception (all subclass `CmdopError`):

```python
from cmdop import (
    AuthError, PermissionError, NotFoundError, ConflictError,
    ValidationError, RateLimitError, ServerError, ConnectionError,
    AgentStreamError, CmdopError,
)

try:
    await c.machines.get("missing-id")
except NotFoundError:
    ...
except CmdopError as e:
    print(e.code, e.message)
```

`ConnectionError` also covers the core process dying mid-call (pending calls
reject). `AgentStreamError` is the streaming-`ask` error outcome.

## Local development

Released wheels bake in every platform's binary. For local work, build the core
and point the client at it with `CMDOP_CORE_BINARY` (also the offline escape
hatch in production):

```bash
cd ../../cmdop_go/go && go build -o /tmp/cmdop-core ./cmd/cmdop-core
CMDOP_CORE_BINARY=/tmp/cmdop-core CMDOP_TOKEN=... uv run python -c "..."
```

Tests: `uv run pytest`. The cross-language parity gate:
`python ../../core/parity/check.py`.
