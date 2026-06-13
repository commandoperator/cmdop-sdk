# cmdop_sdk — Go-first SDK for CMDOP

Two typed thin clients — **PyPI [`cmdop`](https://pypi.org/project/cmdop/)** and
**npm [`@cmdop/sdk`](https://www.npmjs.com/package/@cmdop/sdk)** — over one
shared **Go core** (`cmdop-core`). Write the hard relay logic once in Go; get
many typed language clients cheaply. Both ship in **semver lockstep** (current:
**1.0.0**).

## The three properties that matter (stated up front)

- **End users need NO `cmdop_go` install.** The per-platform `cmdop-core` binary
  is **baked into** the wheel / npm package. `pip install cmdop` or
  `npm i @cmdop/sdk` is everything — no Go toolchain, no separate agent download.
- **Pure stdio.** The client spawns `cmdop-core` and speaks
  protobuf-length-delimited frames over its stdin/stdout. **No local port, no
  socket, no token-on-a-port.** The Bearer token is passed via `CMDOP_TOKEN` env
  at spawn.
- **No macOS notarization.** `com.apple.quarantine` is set by browsers/Mail, not
  by npm/pip extracting a tarball, so Gatekeeper never engages. The binary is
  ad-hoc signed (free; `go build` + a CI `codesign --sign -`) — **no Developer-ID,
  no notarytool, no DMG**. (esbuild ships the same way to tens of millions of
  installs.)

## Architecture

```
   Python client (async)         Node client (async)         (future: Ruby, Go, …)
   thin: spawn + demux           thin: spawn + demux
        │  protobuf over stdio (length-delimited + id-mux Envelope)  │
        └───────────────────────────┬───────────────────────────────┘
                                     ▼
                       ┌──────────────────────────────────┐
                       │  cmdop-core  (Go binary)           │  baked into npm/pip pkg
                       │  • holds the Bearer token          │  (no notarization)
                       │  • REST via ogen client            │
                       │  • SSE /ask via tmaxmax/go-sse     │
                       │  • pin/confirm side-channel POSTs  │
                       │  • retries, error mapping          │
                       └──────────────────┬─────────────────┘
                                          ▼  HTTPS / SSE
                                   cmdop_server relay → machines
```

The Go core lives **inside the `cmdop_go` module** at
`cmdop_go/go/cmd/cmdop-core` (logic in `internal/sdk/core/`). The thin clients are
this repo's `sdk/python/` and `sdk/node/`. The stdio contract is defined once in
`core/proto/` (`buf generate` → typed Go + Python + Node message types in
`core/gen/`).

## Layout

```
cmdop_sdk/
  sdk/python/ · sdk/node/   thin clients (PyPI cmdop · npm @cmdop/sdk)
  core/                     orchestrator + contract + distribution pipeline
    proto/ · gen/             stdio contract + generated message types
    parity/                   cross-language surface gate (manifest.json)
    scripts/                  build_core · stage_packages · release (semver)
    Makefile                  proto · build · test · parity · core · dist
  devops/                   LOCAL release runbook (build → sign → stage → bump → publish)
  dist/                     build output (binaries, npm pkgs, wheels — gitignored)
  Makefile                  thin root delegator (-> core/ and devops/)
```

## Modules

| Path | Ships as | What |
|---|---|---|
| [`sdk/python/`](sdk/python/) | PyPI **`cmdop`** (import `cmdop`) | async-first Python thin client |
| [`sdk/node/`](sdk/node/) | npm **`@cmdop/sdk`** | async Node thin client (ESM + CJS) |
| [`core/proto/`](core/proto/) | — | the stdio contract (`buf generate` → `core/gen/`) |
| `cmdop_go/go/cmd/cmdop-core` + `internal/sdk/core/` | the baked binary | the Go core (in the `cmdop_go` submodule) |

Both clients expose the **same method set** with the **same `ask()` streaming
ergonomics** — camelCase in Node, snake_case in Python. That surface is locked by
[`core/parity/manifest.json`](core/parity/manifest.json) (see the parity table in
[`CLAUDE.md`](CLAUDE.md)).

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

Env: `CMDOP_TOKEN` (or `CMDOP_API_KEY`), `CMDOP_BASE_URL`, `CMDOP_FLEET_ID`,
`CMDOP_TIMEOUT_MS`, `CMDOP_CORE_BINARY` (dev override).

## Regen + build workflow

| Step | Run from | Tool | Produces |
|---|---|---|---|
| Contract codegen | `cmdop_sdk/` | `buf generate` (via `make proto`) | typed Go + py + node message types in `gen/` |
| Go core build | `cmdop_go/go` | `go build ./cmd/cmdop-core` (`make core`) | the per-platform `cmdop-core` binary (logic in `internal/sdk/core/`) |
| Bake + package | `cmdop_sdk/` | staging scripts | ONE fat npm package + ONE fat `py3-none-any` wheel, all 5 binaries baked in |
| Thin-client build | `cmdop_sdk/{python,node}` | `uv build` / `tsup` (`make build`) | publishable `cmdop` / `@cmdop/sdk` |

Codegen is **not** chained into `build` — regen explicitly when the proto
changes. The top-level [`Makefile`](Makefile) wraps these:
`make proto · core · build · test · parity · release`.

## Tests + drift guards

- `make test` — Go core (`go test ./internal/sdk/core/`) + Python (`pytest`) + Node
  (`vitest`).
- `make parity` — the cross-language surface gate
  ([`core/parity/check.py`](core/parity/check.py)): introspects both clients and
  asserts they equal `core/parity/manifest.json`. This + `buf breaking` (the wire
  gate) is the full drift guard.

## Release

`make release` delegates to [`devops/release.py`](devops/release.py), which wraps
[`core/scripts/release.py`](core/scripts/release.py) in **dry-run** by
default: it bumps the semver `X.Y.Z` in lockstep across the Go ldflags stamp, the
Python `pyproject` + `__version__`, and the Node `package.json` (the staged fat
`dist/npm/sdk/package.json` inherits it), then prints exactly what it *would*
publish — ONE fat `py3-none-any` wheel to PyPI `cmdop` + ONE fat `@cmdop/sdk` npm
package. The version is **explicit and stored** in `sdk/python/pyproject.toml`
(no date/network logic); bump with `bump --major/--minor/--patch` or
`--set X.Y.Z`. A real `release` prompts for a TTY confirmation before uploading.

> **First public release is `1.0.0`** — `0.1.0`/`0.1.1` filenames are permanently
> burned on PyPI (it never lets a deleted project re-use a wheel filename, even
> after the project is fully removed), so the line starts at `1.0.0`.
