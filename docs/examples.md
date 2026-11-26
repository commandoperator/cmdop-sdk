# SDK examples

Start with a read, then add the access each workflow requires.

**In short:** Use [quickstart](quickstart.md) for the first complete program; choose a workflow below for the next step.

## Choose an example

| Workflow | Required risk classes | Example |
|---|---|---|
| Find an online machine and inspect its OS | `read` | [Quickstart](quickstart.md) |
| Read a file and check truncation | `read` | [Files and screenshots](files-and-screen.md) |
| Run a command and print its exit code | `exec` | [Commands](commands-and-tasks.md#commands) |
| Follow output as it arrives | `exec` | [Streaming](commands-and-tasks.md#streaming) |
| Start work and read it after reconnecting | `exec`, `read` | [Tasks](commands-and-tasks.md#tasks-that-outlive-the-call) |
| Ask an installed AI program | `agent` | [Installed agents](agents.md) |
| Capture the computer's screen | `screen`, OS permission | [Screenshots](files-and-screen.md#capture-a-screen) |

The language references cover [TypeScript](typescript.md) and
[Python](python.md), including resource cleanup. Workflow snippets use the connected
client and selected `box` from the quickstart; run them inside its `try` or context-manager block.

## Published source programs

Each source pair links to the same published revision. Availability is not a claim that every workflow has been run on your machine.

| Program | Sources | Access | Prerequisites | Guide |
|---|---|---|---|---|
| Read a machine's OS and CPU | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/hello.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/hello.ts) | `read` | See guide | [Guide](quickstart.md) |
| Inspect online computers | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/fleet.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/fleet.ts) | `read` | See guide | [Guide](examples.md) |
| List a machine's files | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/files.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/files.ts) | `read` | See guide | [Guide](files-and-screen.md) |
| Read the demo guide and task summary | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/showtime.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/showtime.ts) | `read` | See guide | [Guide](examples.md) |
| Discover installed agents without prompting | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/agents.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/agents.ts) | `read` | See guide | [Guide](agents.md) |
| Read a build report from a machine-local MCP server | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/local-mcp.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/local-mcp.ts) | `exec` | Exact machine ID | [Guide](commands-and-tasks.md) |
| Find nonstop Bali to Bangkok flights through local Fli MCP | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/google-flights.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/google-flights.ts) | `exec`, `network` | Exact machine ID | [Guide](examples.md) |
| Run and verify a bounded command | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/command.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/command.ts) | `exec` | Exact machine ID | [Guide](commands-and-tasks.md) |
| Ask Codex explicitly | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/agents/codex.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/agents/codex.ts) | `read`, `agent` | Exact machine ID; named agent installed and authenticated | [Guide](agents.md) |
| Ask Claude Code explicitly | [Python](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/python/agents/claude-code.py) · [TypeScript](https://github.com/commandoperator/cmdop-sdk/blob/7c8e0bee944e9573dd0a31011b63e83025141ec5/examples/typescript/agents/claude-code.ts) | `read`, `agent` | Exact machine ID; named agent installed and authenticated | [Guide](agents.md) |

## Run the executable examples

The public repository includes [TypeScript and Python programs](https://github.com/commandoperator/cmdop-sdk/tree/main/examples).
Start with `examples/typescript/hello.ts` or `examples/python/hello.py` from a local checkout.
Follow [quickstart](quickstart.md) to bring a computer online and set `CMDOP_URL`
and `CMDOP_TOKEN`. The first-read programs need an agent token with `read` access.
Keep tokens out of source files and logs. The SDK package does not install the machine program.

### Node.js

Requires Node.js 20+. Install the package in your project:

```bash
npm install @cmdop/sdk
```

The first-read TypeScript program contains no TypeScript-only syntax. Copy its contents to
`hello.mjs` in that project, then run:

```bash
node hello.mjs
```

For a TypeScript project, use your existing TypeScript runner.

### Python

From the repository root, using your project's Python 3.10+ environment:

```bash
python -m pip install cmdop
python examples/python/hello.py
```

### Expected result

Both programs print the selected computer's OS, architecture and CPU count. A verified run
on a connected Linux computer returned:

```text
linux x86_64 32
```

Your values depend on your computer. These programs choose the first online computer;
select an explicit machine id when the target matters. Read other example programs before
running them and enable only the access their workflow requires.

## Catalog-based checkout runner

In a checkout containing `examples/catalog.json` and `examples/run.sh`, the catalog selects the
programs and records their language paths and required access. Older checkouts do not include
this runner; use the first-read instructions above until you have a revision containing it.
The combined runner requires Node.js 20+, Python 3.10+, npm and uv. It compiles TypeScript to
JavaScript rather than assuming Node can execute every `.ts` file directly.

From that checkout's root:

```bash
bash examples/run.sh --list
bash examples/run.sh --plan
```

`--list` validates the source inventory. `--plan` checks selection without installing packages
or connecting. For a live run, set `CMDOP_URL` and `CMDOP_TOKEN` explicitly; the runner does not
read an owner token from local configuration. Set `CMDOP_MACHINE` to the exact machine ID for
command and named-agent examples.

The default selection contains read/discovery programs. `agents` only lists installed agents;
it does not send a prompt. Choose `prompt-codex` or `prompt-claude-code` explicitly:

```bash
ONLY=prompt-codex AGENT_PROMPT=1 bash examples/run.sh
```

Command execution uses `ONLY=command` with `EXAMPLES_EXEC=1`. Choosing an ID does not grant its
required access; setting an effect flag does not select more programs automatically. The agent
examples request `text_only` and need both discovery access and the agent risk class, subject
to the machine's configuration. Installation does not establish valid vendor authentication.

The catalog pins the SDK package version; `VERSION` can select another explicit release.
`--build-only` installs compilation dependencies and compiles the selected TypeScript without
executing examples. It still checks selection and effect opt-ins.

| Runner result | Meaning |
|---|---|
| `SMOKE` | The legacy demonstration process completed; no workflow verification is inferred |
| `PASS` | The example's bounded result assertions passed |
| `RUNNING` | An agent answer is unfinished; keep its task handle |
| `UNKNOWN` | The local wait ended without establishing the remote outcome; do not blindly retry |
| `FAIL` or `SKIP` | The pair is incomplete; inspect prerequisites or the reported condition |

The runner omits raw process/model output. An unfinished or uncertain effectful run prevents
an automatic second-language attempt. Source availability, local checks, a real machine run
and public delivery are separate facts.

## Search Google Flights through a local MCP server

“Which nonstop flights leave Bali for Bangkok on my travel date?” The Google Flights example
asks Fli, an unofficial Google Flights interface running on your selected machine. It checks
both Bangkok airports for one adult, then returns up to three distinct flights ordered by USD
fare, with local departure times and booking links when available. Prices reflect the time
of the search. The example only searches.

On the target machine, install uv and prepare the Fli environment once:

```bash
uvx --from 'flights[mcp]==0.11.1' python -c "import fli.mcp.server"
command -v uvx
```

With the SDK connection and machine ID set as described above, set `FLI_UVX` to the absolute
path printed on the target and `FLIGHT_DATE` to your travel date in YYYY-MM-DD format.
From the checkout, run the example in both languages:

```bash
ONLY=google-flights EXAMPLES_EXEC=1 EXAMPLES_NETWORK=1 bash examples/run.sh
```

The runner reports whether each caller succeeded. To see fares directly, set the same two
effect flags and run the Python example:

```bash
EXAMPLES_EXEC=1 EXAMPLES_NETWORK=1 uv run --with cmdop==3.6.0 python examples/python/google-flights.py
```

An empty flight list means the search completed with no matching fares. A failed search
exits with an error. The pinned local package runs offline from the uv cache while Fli
uses the target machine's network to request current fares.

## Build an integration

Use a dedicated token for each application. Discover machines, select an explicit id and call the
tool you need. Keep tool arguments typed; handle refusal codes and uncertain connection outcomes.
For a custom AI integration, have the model propose a supported tool call, validate it against
the tool contract, and execute it under that application's grant.

The public SDK source and executable example files are in
[commandoperator/cmdop-sdk](https://github.com/commandoperator/cmdop-sdk).
Review commands before running them on your own machines.

[SDK](README.md) · [Authentication](authentication.md)
