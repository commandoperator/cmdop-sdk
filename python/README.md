# cmdop

Your computers' tools from Python, sync and async. Use the same tools AI agents call through MCP,
with typed results, your agent's grant and a record of each call.

```bash
pip install cmdop
```

Requires Python 3.10+. [Install CMDOP](https://cmdop.ai/download) on a computer, bring it online on
your page and create an agent token in the Agents tab. Set `CMDOP_URL` to your page's address
(`https://<address>.cmdop.dev`) and `CMDOP_TOKEN` through your environment.
The SDK does not install the machine program. Start with the `read` risk class.

```python
import cmdop

with cmdop.connect() as client:
    online = next((machine for machine in client.machines() if machine["online"]), None)
    if online is None:
        raise RuntimeError("Bring a machine online on your CMDOP page.")
    info = client.machine(online["id"]).sys.info()
    print(info.os, info.arch, info.cpus)
```

The program prints the selected computer's OS, architecture and CPU count.

## Async

```python
import asyncio
import cmdop

async def main():
    async with cmdop.connect_async() as client:
        for machine in await client.machines():
            if machine["online"]:
                info = await client.machine(machine["id"]).sys.info()
                print(info.os, info.arch, info.cpus)

asyncio.run(main())
```

## Commands and streaming

Inside the connected client's `with` block, with `exec` allowed for the agent and machine:

```python
box = client.machine("<machine>")
print(box.run("uptime").stdout)
run = box.stream("printf 'hello\\n'")
for piece in run:
    print(piece.data, end="")
print(run.result.exit_code)
```

`box.fs.read(path=...)` and `box.fs_read(path=...)` call the same typed tool.
`box.screenshot()` decodes the image. `client.tasks_list()` and `client.docs_read()` need no
machine. Installed agents use `box.agent.*` and the `agent` risk class.

## Deadlines and errors

`box.run("uptime", deadline=5)` limits the call to five seconds.
Branch on `cmdop.CmdopError.code`; `cmdop.CarrierError` means the connection broke before an
answer arrived. Do not blindly repeat writes after a connection failure.
Call `run.cancel()` explicitly when leaving a synchronous stream early. Async streams use
`async for`, `await run.result()` and `await run.cancel()`.

[Quickstart](https://docs.cmdop.ai/reference/sdk/quickstart) ·
[Python API](https://docs.cmdop.ai/reference/sdk/python) ·
[MCP client setup](https://docs.cmdop.ai/guides/connect) ·
[Source and issues](https://github.com/commandoperator/cmdop-sdk)

License: MIT.
