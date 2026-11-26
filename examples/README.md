# SDK examples

Generated from `examples/catalog.json`; edit the inventory, not this index.

[Setup and execution guide](../docs/examples.md#run-the-executable-examples).
Source availability does not establish live integration verification.

| Example | Python | TypeScript | Access | Local check |
|---|---|---|---|---|
| [Read a machine's OS and CPU](../docs/quickstart.md) | [hello.py](python/hello.py) | [hello.ts](typescript/hello.ts) | `read` | smoke |
| [Inspect online computers](../docs/examples.md) | [fleet.py](python/fleet.py) | [fleet.ts](typescript/fleet.ts) | `read` | smoke |
| [List a machine's files](../docs/files-and-screen.md) | [files.py](python/files.py) | [files.ts](typescript/files.ts) | `read` | smoke |
| [Read the demo guide and task summary](../docs/examples.md) | [showtime.py](python/showtime.py) | [showtime.ts](typescript/showtime.ts) | `read` | smoke |
| [Discover installed agents without prompting](../docs/agents.md) | [agents.py](python/agents.py) | [agents.ts](typescript/agents.ts) | `read` | smoke |
| [Read a build report from a machine-local MCP server](../docs/commands-and-tasks.md) | [local-mcp.py](python/local-mcp.py) | [local-mcp.ts](typescript/local-mcp.ts) | `exec` | outcome |
| [Find nonstop Bali to Bangkok flights through local Fli MCP](../docs/examples.md) | [google-flights.py](python/google-flights.py) | [google-flights.ts](typescript/google-flights.ts) | `exec`, `network` | outcome |
| [Run and verify a bounded command](../docs/commands-and-tasks.md) | [command.py](python/command.py) | [command.ts](typescript/command.ts) | `exec` | outcome |
| [Ask Codex explicitly](../docs/agents.md) | [prompt-codex.py](python/agents/codex.py) | [prompt-codex.ts](typescript/agents/codex.ts) | `read`, `agent` | outcome |
| [Ask Claude Code explicitly](../docs/agents.md) | [prompt-claude-code.py](python/agents/claude-code.py) | [prompt-claude-code.ts](typescript/agents/claude-code.ts) | `read`, `agent` | outcome |
