# cmdop (Python)

![cmdop — Python SDK for CMDOP](https://raw.githubusercontent.com/commandoperator/cmdop-sdk/main/assets/hero-cmdop-python.webp)

Async-first Python SDK for CMDOP — manage your machines, fleets, tunnels, and
schedules, stream a machine's AI agent, and drive the skills marketplace, all
from typed Python.

📚 **Docs: [docs.cmdop.com](https://docs.cmdop.com)** · [SDK](https://cmdop.com/sdk) ·
[Bots](https://cmdop.com/bots) · [Connect](https://cmdop.com/connect)

- **One install, zero dependencies** — `pip install cmdop` is everything. No
  native build step, no extra runtime, nothing fetched on first run.
- **Works anywhere, offline-ready** — a single self-contained package runs the
  same on macOS, Linux, and Windows, including air-gapped hosts.
- **Typed end to end** — every resource and response is fully typed, with one
  clean async streaming API for live agent output.

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

`Client` is an async context manager — use `async with` so resources are released
on exit (or call `await c.aclose()`).

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
> use your relay token (`CMDOP_TOKEN`); the **`skills`** marketplace uses your
> platform API key (`CMDOP_API_KEY`). Set whichever you need — the client routes
> each call to the right plane for you.

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

Precedence is always explicit arg > env var > default.

## Error handling

Every failure surfaces as a typed exception carrying a stable `code` (all
subclass `CmdopError`):

```python
from cmdop import (
    AuthError, PermissionError, NotFoundError, ConflictError,
    ValidationError, RateLimitError, ServerError, ConnectionError,
    TimeoutError, UnavailableError, AgentStreamError, CmdopError,
)

try:
    await c.machines.get("missing-id")
except NotFoundError:
    ...
except CmdopError as e:
    if e.retryable:           # True on TimeoutError — safe to retry
        ...
    print(e.code, e.message)
```

`ConnectionError` covers a lost connection mid-call (pending calls reject);
`TimeoutError` (a retryable subclass) is a deadline/handshake timeout;
`UnavailableError` means the relay is up but the target agent/machine is offline.
`AgentStreamError` is the streaming-`ask` error outcome.

## Links

- **Docs** → [docs.cmdop.com](https://docs.cmdop.com)
- **SDK** → [cmdop.com/sdk](https://cmdop.com/sdk) · **Bots** →
  [cmdop.com/bots](https://cmdop.com/bots) · **Connect** →
  [cmdop.com/connect](https://cmdop.com/connect)
- [`cmdop` on PyPI](https://pypi.org/project/cmdop/) ·
  [source](https://github.com/commandoperator/cmdop-sdk)
