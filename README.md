# CMDOP SDK

Your machines' tools from a program, in TypeScript and Python: the same tools AI agents use through MCP, with the
same rules and the same record of every call.

| Language | Install | Source |
|---|---|---|
| TypeScript / Node | `npm install @cmdop/sdk` | [`typescript/`](typescript/) |
| Python | `pip install cmdop` | [`python/`](python/) |

```ts
import { connect } from "@cmdop/sdk";

const box = connect().machine("box");        // CMDOP_TOKEN, CMDOP_URL
console.log((await box.run("uptime")).stdout);
```

```python
import cmdop

with cmdop.connect() as c:                   # CMDOP_TOKEN, CMDOP_URL
    print(c.machine("box").run("uptime").stdout)
```

Every tool is a typed method on a machine (`box.fs_read`), also under its group (`box.fs.read`); the tools about the
whole contour are methods of the client, with no machine: `machines_list`, `tasks_list`, `history_search`,
`docs_read` (the documentation, contents first) and `showtime_guide`, the guide for a short live demo on your machines.
Each machine also lets you ask the AI agent programs installed on it (Claude Code, Codex) the same way:
`box.agent.list`, `box.agent.prompt` (an answer and a `session` to continue), `box.agent.sessions`, `box.agent.cancel`.

Both packages are generated from one tool contract, so a tool, its arguments and its result are the same in each.
[`vectors/carrier.json`](vectors/carrier.json) holds the cases every client must pass.

## The same tools over MCP

CMDOP is an MCP server too: an agent reaches these tools at `$CMDOP_URL/mcp` (streamable HTTP) with an agent token
as `Authorization: Bearer`, the same kind of token this package takes, under the same grant and record. The
command or settings for each client: https://docs.cmdop.ai/guides/connect

This repository is the published source of each release (`v<version>` tags); issues are welcome here.

Website: https://cmdop.ai · Docs: https://docs.cmdop.ai/reference/sdk · License: [MIT](LICENSE)
