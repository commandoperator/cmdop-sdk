# Python SDK

`cmdop` for Python 3.10 and later: your machines' tools as typed methods, sync and async.

**In short:** `pip install cmdop`, then `with cmdop.connect() as c: print(c.machine("box").run("uptime").stdout)`.
`CMDOP_TOKEN` and `CMDOP_URL` come from the environment.

## Install

```bash
pip install cmdop
```

## Connect

```python
import cmdop

with cmdop.connect() as c:                   # CMDOP_TOKEN, CMDOP_URL
    print(c.machines())                      # name, id, online, os, tools
```

`connect(token=None, url=None, *, contour=None)`: the agent token, your page's address
(`https://<address>.cmdop.dev`), or the address alone as `contour`. `cmdop.connect_async()` takes the
same and is used with `async with` and `await`.

## Async client

The `read` risk class is enough for this complete example:

```python
import asyncio
import cmdop

async def main():
    async with cmdop.connect_async() as client:
        machines = await client.machines()
        online = next((machine for machine in machines if machine["online"]), None)
        if online is None:
            raise RuntimeError("Bring a machine online on your CMDOP page.")
        info = await client.machine(online["id"]).sys.info()
        print(info.os, info.arch, info.cpus)

asyncio.run(main())
```

For async commands, await `box.run(...)`. An async stream uses `async for piece in run`,
then `await run.result()`; synchronous streams expose `run.result` as a property.

## Run a command

```python
with cmdop.connect() as c:
    box = c.machine("box")                   # a name or id; no name: the one machine online
    print(box.run("uptime").stdout)

    run = box.stream("make test")
    for piece in run:
        print(piece.data, end="")
    print(run.result.exit_code)
```

Leaving the loop early, or `run.cancel()`, stops the command; `run.result` then raises `cancelled`.

When stopping early, call `run.cancel()` in a `finally` block so cancellation does not depend on
iterator cleanup. For async streams, use `await run.cancel()`.

## Any tool

Each tool on the [tools reference](https://docs.cmdop.ai/reference/tools) is a method with the same arguments, as keyword
arguments, and a typed result:

```python
text = box.fs_read(path="/tmp/notes.txt")
task = box.task_start(command="npm run dev")
c.call("sys_info", {}, machine="box")        # by name, the result as JSON
```

Every tool is also under its group, the part of its name before the first `_`:
`box.fs.read(path=...)` is `box.fs_read(path=...)`, `box.task.start(...)` is `box.task_start(...)`. Both spellings
stay. `box.screenshot()` returns the picture decoded (`image.data` as bytes, `image.mime`, `geometry`).

The tools about the whole contour, not one machine, are methods of the client:

```python
guide = c.showtime_guide(language="English")   # the demo guide, as text
running = c.tasks_list().tasks                 # everything running now
rows = c.machines_list()                       # machines with state and activity
past = c.history_search(text="make test")
pages = c.docs_read()                          # this documentation: every page, path and title
page = c.docs_read(path="guides/connect")      # one page as Markdown
```

Ask an AI agent program on a machine ([guide](https://docs.cmdop.ai/guides/ask-an-agent)):

```python
box = c.machine("laptop")
print([a.id for a in box.agent.list().agents])
answer = box.agent.prompt(prompt="Find the weakest point in this plan: ...")
follow = box.agent.prompt(prompt="And how would you fix it?", session=answer.session)
```

## Deadlines and errors

```python
try:
    box.run("long-job", deadline=30)         # seconds
except cmdop.CmdopError as e:
    if e.code != "timed_out":
        raise
```

`CmdopError.code` is one of the [error codes](https://docs.cmdop.ai/reference/errors) (`cmdop.ERROR_CODES`);
`CarrierError` means the connection broke and no answer came.

## Related

[SDK](README.md) · [TypeScript SDK](typescript.md) · [Use CMDOP from your product](https://docs.cmdop.ai/guides/embed)
