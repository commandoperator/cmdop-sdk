# @cmdop/sdk

Your machines' tools from a program: the same tools agents use through MCP, typed.

```bash
npm install @cmdop/sdk
```

```ts
import { connect } from "@cmdop/sdk";

const cmdop = connect();                      // CMDOP_TOKEN, CMDOP_URL
const box = cmdop.machine("box");
console.log((await box.run("uptime")).stdout);

const run = box.stream("make test");
for await (const piece of run) process.stdout.write(piece.data);
console.log((await run.result).exit_code);
```

Every tool is a typed method on a machine (`box.fs_read({ path })`, `box.task_start({ command })`, …), also under
its group (`box.fs.read({ path })`, `box.task.start({ command })`); `box.screenshot()` decodes the picture; and
`cmdop.call(tool, args, { machine })` reaches any of them by name. A refused call throws `CmdopError` with its
`code`; `deadline` and `signal` bound and cancel any call.

## The same tools over MCP

CMDOP is an MCP server too: an agent reaches these tools at `$CMDOP_URL/mcp` (streamable HTTP) with an agent token
as `Authorization: Bearer`, the same kind of token this package takes, under the same grant and record. The
command or settings for each client: https://docs.cmdop.ai/guides/connect

Website: https://cmdop.ai · Docs: https://docs.cmdop.ai/reference/sdk/typescript · License: MIT
