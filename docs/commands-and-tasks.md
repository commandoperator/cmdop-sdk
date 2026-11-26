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
