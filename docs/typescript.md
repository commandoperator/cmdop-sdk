# TypeScript SDK

`@cmdop/sdk` for Node 20 and later: your machines' tools as typed methods.

**In short:** `npm install @cmdop/sdk`, then `const box = connect().machine("box"); (await box.run("uptime")).stdout`.
`CMDOP_TOKEN` and `CMDOP_URL` come from the environment.

Start with the [read-only quickstart](quickstart.md). Commands below require the
`exec` risk class; file reads require `read`. Release the client with `await cmdop.close()` in
a `finally` block when your program is finished.

## Install

```bash
npm install @cmdop/sdk
```

## Connect

```ts
import { connect } from "@cmdop/sdk";

const cmdop = connect();                     // CMDOP_TOKEN, CMDOP_URL
const machines = await cmdop.machines();     // name, id, online, os, tools
```

| Option | Default | Meaning |
|---|---|---|
| `token` | `CMDOP_TOKEN` | the agent token; the program can do what the agent's grant allows |
| `url` | `CMDOP_URL` | your page's address, `https://<address>.cmdop.dev` |
| `contour` | — | the address alone (`m7xg5cgy`) instead of `url` |

## Run a command

```ts
const box = cmdop.machine("box");            // a name or id; no name: the one machine online
const { exit_code, stdout } = await box.run("uptime");

const run = box.stream("make test");
for await (const piece of run) process.stdout.write(piece.data);
console.log((await run.result).exit_code);
```

`piece.stream` is `stdout` or `stderr`. Breaking out of the loop stops the command; its result is
then `cancelled`.

## Any tool

Each tool on the [tools reference](https://docs.cmdop.ai/reference/tools) is a method with the same arguments and result:

```ts
const file = await box.fs_read({ path: "/tmp/notes.txt" });
const task = await box.task_start({ command: "npm run dev" });
const out = await box.task_output({ task: task.task });
await cmdop.call("sys_info", {}, { machine: "box" });   // by name
```

Every tool is also under its group, the part of its name before the first `_`:
`box.fs.read({ path })` is `box.fs_read({ path })`, `box.task.start(…)` is `box.task_start(…)`. Both spellings stay.
`box.screenshot()` returns the picture decoded (`image.bytes`, `image.mime`, `geometry`).

The tools about the whole contour, not one machine, are methods of the client:

```ts
const guide = await cmdop.showtime_guide({ language: "English" });   // the demo guide, as text
const { tasks } = await cmdop.tasks_list();                           // everything running now
const rows = await cmdop.machines_list();                             // machines with state and activity
const past = await cmdop.history_search({ text: "make test" });
const pages = await cmdop.docs_read();                                // this documentation: every page, path and title
const page = await cmdop.docs_read({ path: "guides/connect" });       // one page as Markdown
```

Ask an AI agent program on a machine ([guide](https://docs.cmdop.ai/guides/ask-an-agent)):

```ts
const box = cmdop.machine("laptop");
console.log((await box.agent.list({})).agents.map((a) => a.id));
const answer = await box.agent.prompt({ prompt: "Find the weakest point in this plan: ..." });
const follow = await box.agent.prompt({ prompt: "And how would you fix it?", session: answer.session });
```

## Deadlines, cancelling, errors

```ts
import { CmdopError } from "@cmdop/sdk";

const stop = new AbortController();
try {
  await box.run("long-job", {}, { deadline: 30_000, signal: stop.signal });
} catch (e) {
  if (e instanceof CmdopError && e.code === "timed_out") { /* retry later */ }
  else throw e;
}
```

`deadline` is in milliseconds; aborting `signal` cancels the call (`cancelled`). `CmdopError.code`
is one of the [error codes](https://docs.cmdop.ai/reference/errors); `CarrierError` means the connection broke and no
answer came.

## Related

[SDK](README.md) · [Python SDK](python.md) · [Use CMDOP from your product](https://docs.cmdop.ai/guides/embed)
