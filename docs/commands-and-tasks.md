# Commands and tasks

Use `run` for a result, `stream` for output as it arrives, and task tools for work you will revisit.

**In short:** `run` waits; `stream` follows a call; `task.start` returns a task id for later `task.output` or `task.stop`.

## Commands

Command execution requires the `exec` risk class in the agent's grant and machine ceiling.
After connecting and selecting a machine as in the [quickstart](quickstart.md):

```ts
const result = await box.run("printf 'hello from my computer\\n'");
console.log(result.stdout);
console.log(result.exit_code);
```

```python
result = box.run("printf 'hello from my computer\\n'")
print(result.stdout, end="")
print(result.exit_code)
```

Expected output:

```text
hello from my computer
0
```

Check the exit code; a nonzero program exit is different from a refused tool call.

## Call a local MCP tool

Suppose your application needs an airport code from Fli, an MCP server installed on a Mac.
Select that Mac by its machine ID. Through either SDK, call `exec_run` with the argument list
for a small MCP client on the selected machine. You can also send a fixed Python helper through
`stdin` with `python -`. The machine needs the interpreter and the MCP server's dependencies.

For a stdio server, the helper starts its own server process, initializes the session, lists
the tools and calls the selected tool. For example, a caller using CMDOP SDK 3.6.0 in Python
or TypeScript reached Fli 0.11.1 and called `find_airports` with query `DPS`. The same call
through CMDOP's MCP endpoint returned the same airport. The helper checked that one airport
record contained both the exact IATA code and the name “Ngurah Rai (Bali) International Airport”.

This pattern requires command execution permission on the target. Give the helper a timeout,
check the command's exit status and truncation flag, then validate the MCP tool's success
and structured result before using it. The permission applies to the outer command. Launching
a fresh stdio server creates a separate session from the one an agent may already be using.

## Streaming

```ts
const run = box.stream("printf 'first\\n'; printf 'second\\n'");
for await (const piece of run) process.stdout.write(piece.data);
console.log((await run.result).exit_code);
```

```python
run = box.stream("printf 'first\\n'; printf 'second\\n'")
for piece in run:
    print(piece.data, end="")
print(run.result.exit_code)
```

Output pieces include a stream name and sequence number. Chunk boundaries are not line boundaries.
Leaving the stream early cancels the command; see [cancellation](errors-and-cancellation.md).

## Tasks that outlive the call

These examples require `exec` to start and `read` to inspect.
The task id is an integer; save it with the selected machine id if another program will read it later.

```ts
const task = await box.task.start({ command: "printf 'task finished\\n'" });
const screen = await box.task.output({ task: task.task });
console.log(task.task, screen.running, screen.text);
```

```python
task = box.task.start(command="printf 'task finished\\n'")
screen = box.task.output(task=task.task)
print(task.task, screen.running, screen.text)
```

A task may still be running at the first read. Re-read `task.output` later; `task.stop` stops it.
Tasks continue when the call or chat closes. Output retention is bounded and ends when the machine
program restarts; see [task_output](https://docs.cmdop.ai/reference/tools/task_output). Use `run` when you need an exit code.
Do not assume closing a client stops a task created with `task.start`.

[SDK](README.md) · [Task concepts](https://docs.cmdop.ai/concepts/tasks)
