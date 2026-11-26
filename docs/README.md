# SDK

The machine tools as a library for your own program: the same tools an agent calls through MCP, under
the same grant and ceiling, each call recorded under the agent whose token the program holds.

**In short:** `npm install @cmdop/sdk` or `pip install cmdop`; set `CMDOP_TOKEN` (an agent token) and `CMDOP_URL`
(your page's address); `connect().machine("box").run("uptime")`.

| Language | Package | Page |
|---|---|---|
| TypeScript, Node 20+ | npm [`@cmdop/sdk`](https://www.npmjs.com/package/@cmdop/sdk) | [TypeScript](typescript.md) |
| Python 3.10+ | PyPI [`cmdop`](https://pypi.org/project/cmdop/) | [Python](python.md) |

The current version is the one npm and PyPI show; what changed in each: [changelog](https://docs.cmdop.ai/help/changelog).

Source: [github.com/commandoperator/cmdop-sdk](https://github.com/commandoperator/cmdop-sdk). License: MIT.

## Start here

- [Quickstart](quickstart.md): install, connect and read a machine in either language.
- [Authentication](authentication.md): settings, agent grants and revocation.
- [TypeScript](typescript.md) and [Python](python.md): language API and lifecycle.
- [Machines and tools](machines-and-tools.md): selection, method groups and client tools.
- [Commands and tasks](commands-and-tasks.md): results, streaming and work you revisit.
- [Files and screenshots](files-and-screen.md): encoding, truncation and screen permissions.
- [Installed AI agents](agents.md): prompts, sessions and longer runs.
- [Errors and cancellation](errors-and-cancellation.md): deadlines, codes and safe recovery.
- [Examples](examples.md): choose a workflow by required access.
- [Versions and support](versions-and-support.md): compatibility and reproducible issues.
- [Docker](docker.md): run the local MCP report example and check machine image availability.

## Shared capabilities

- **A typed method per tool** on a machine, with the arguments and result of its
  [tool page](https://docs.cmdop.ai/reference/tools), also under its group (`box.fs.read`). A tool added to CMDOP comes with
  the next SDK version.
- **`run` and `stream`** for commands: `run` waits for the result; `stream` gives the output as it
  comes, then the same result. Leaving the loop early stops the command.
- **`call(tool, args)`** reaches any tool by name.
- **The contour's own tools** as methods of the client, with no machine: `machines_list`, `tasks_list`,
  `history_search`, `docs_read` (this documentation, the contents first, then a page by path) and `showtime_guide`,
  the guide an agent follows for a short live demo on your machines.
  They are the same tools an agent sees over MCP.
- **A deadline per call.** The call keeps the shorter of yours and the tool's own time; past it the
  answer is `timed_out`.
- **It names itself.** Each request says which SDK and version sent it (`x-cmdop-client: python/<version>` or
  `node/<version>`), so a machine on `cmdop` 0.1.16 or later shows "Python SDK" or "Node SDK" as the caller in its
  Activity. Nothing else about your program is sent.
- **One error type** with the [error code](https://docs.cmdop.ai/reference/errors) as `code`. Decide by the code, never by
  the message. A connection that breaks is a separate error, not a result.

## Before you start

A machine online on your page and an agent token for your program from the Agents tab, in the
environment as `CMDOP_TOKEN`; your page's address (`https://<address>.cmdop.dev`) as `CMDOP_URL`.
The token is held to the agent's grant. Never put it in code you commit, in a URL or in a log.

The SDK uses the [HTTP API](https://docs.cmdop.ai/reference/http): `/api/v1/machines`, `/api/v1/call` and
`/api/v1/call/stream`. Calls from a paired client, encrypted end to end, are not in the published
packages yet: [sealed calls](https://docs.cmdop.ai/concepts/sealed-calls).

## The same tools over MCP

CMDOP is also an MCP server. An agent reaches the same tools at `https://<address>.cmdop.dev/mcp`
(streamable HTTP) with an agent token as `Authorization: Bearer`: the kind of token the SDK takes,
held to the same grant, each call recorded the same way. Give each program and each agent its own
token, so the record says which one acted. The command or settings for each client:
[Connect an agent](https://docs.cmdop.ai/guides/connect).

## Versions

One version for both languages. Within a major version, tools, arguments, result fields and error
codes are only added; a program written against 3.x keeps working. A machine with an older `cmdop`
program answers a tool it does not have yet with `unknown_tool`.

---

Documentation snapshot from the [CMDOP documentation](https://docs.cmdop.ai/reference/sdk).
Source revision: 0aefbf8b3e28f71a7b74f82c557ef6d0b99493d5. The live site may contain newer changes.
