# @cmdop/sdk

Your computers' tools from TypeScript. Use the same tools AI agents call through MCP, with typed
arguments and results, your agent's grant and a record of each call.

```bash
npm install @cmdop/sdk
```

Requires Node.js 20+. [Install CMDOP](https://cmdop.ai/download) on a computer, bring it online on
your page and create an agent token in the Agents tab. Set `CMDOP_URL` to your page's address
(`https://<address>.cmdop.dev`) and `CMDOP_TOKEN` to that token through your environment.
The SDK package does not install the machine program. Start with the `read` risk class.

```ts
import { connect } from "@cmdop/sdk";

const client = connect();
try {
  const online = (await client.machines()).find((machine) => machine.online);
  if (!online) throw new Error("Bring a machine online on your CMDOP page.");
  const info = await client.machine(online.id).sys.info({});
  console.log(info.os, info.arch, info.cpus);
} finally {
  await client.close();
}
```

The program prints the selected computer's OS, architecture and CPU count.
Use an explicit machine id when the target matters.

## Commands and streaming

Inside the connected client's `try` block, with `exec` allowed for the agent and machine:

```ts
const box = client.machine("<machine>");
console.log((await box.run("uptime")).stdout);
const run = box.stream("printf 'hello\\n'");
for await (const piece of run) process.stdout.write(piece.data);
console.log((await run.result).exit_code);
```

`box.fs.read({ path })` and `box.fs_read({ path })` call the same typed tool.
`box.screenshot()` decodes the image. `client.tasks_list()` and `client.docs_read()` need no
machine. Installed AI agents are available through `box.agent.*` with the `agent` risk class.

## Deadlines and errors

Pass `{ deadline: 5_000, signal: controller.signal }` as call options: deadlines use milliseconds
and `AbortSignal` cancels a call. For `run`, options are its third argument:
`box.run("uptime", {}, { deadline: 5_000 })`.
Branch on `CmdopError.code`; `CarrierError` means a connection failed before an answer arrived.
Python's deadline units differ; check the language reference.

[Quickstart](https://docs.cmdop.ai/reference/sdk/quickstart) ·
[TypeScript API](https://docs.cmdop.ai/reference/sdk/typescript) ·
[MCP client setup](https://docs.cmdop.ai/guides/connect) ·
[Source and issues](https://github.com/commandoperator/cmdop-sdk)

License: MIT.
