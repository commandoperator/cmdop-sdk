# SDK examples

Start with a read, then add the access each workflow requires.

**In short:** Use [quickstart](quickstart.md) for the first complete program; choose a workflow below for the next step.

## Choose an example

| Workflow | Required risk classes | Example |
|---|---|---|
| Find an online machine and inspect its OS | `read` | [Quickstart](quickstart.md) |
| Read a file and check truncation | `read` | [Files and screenshots](files-and-screen.md) |
| Run a command and print its exit code | `exec` | [Commands](commands-and-tasks.md#commands) |
| Follow output as it arrives | `exec` | [Streaming](commands-and-tasks.md#streaming) |
| Start work and read it after reconnecting | `exec`, `read` | [Tasks](commands-and-tasks.md#tasks-that-outlive-the-call) |
| Ask an installed AI program | `agent` | [Installed agents](agents.md) |
| Capture the computer's screen | `screen`, OS permission | [Screenshots](files-and-screen.md#capture-a-screen) |

The language references cover [TypeScript](typescript.md) and
[Python](python.md), including resource cleanup. Workflow snippets use the connected
client and selected `box` from the quickstart; run them inside its `try` or context-manager block.

## Run the executable examples

The public repository includes [TypeScript and Python programs](https://github.com/commandoperator/cmdop-sdk/tree/main/examples).
Start with `examples/typescript/hello.ts` or `examples/python/hello.py` from a local checkout.
Follow [quickstart](quickstart.md) to bring a computer online and set `CMDOP_URL`
and `CMDOP_TOKEN`. The first-read programs need an agent token with `read` access.
Keep tokens out of source files and logs. The SDK package does not install the machine program.

### Node.js

Requires Node.js 20+. Install the package in your project:

```bash
npm install @cmdop/sdk
```

The first-read TypeScript program contains no TypeScript-only syntax. Copy its contents to
`hello.mjs` in that project, then run:

```bash
node hello.mjs
```

For a TypeScript project, use your existing TypeScript runner.

### Python

From the repository root, using your project's Python 3.10+ environment:

```bash
python -m pip install cmdop
python examples/python/hello.py
```

### Expected result

Both programs print the selected computer's OS, architecture and CPU count. A verified run
on a connected Linux computer returned:

```text
linux x86_64 32
```

Your values depend on your computer. These programs choose the first online computer;
select an explicit machine id when the target matters. Read other example programs before
running them and enable only the access their workflow requires.

## Build an integration

Use a dedicated token for each application. Discover machines, select an explicit id and call the
tool you need. Keep tool arguments typed; handle refusal codes and uncertain connection outcomes.
For a custom AI integration, have the model propose a supported tool call, validate it against
the tool contract, and execute it under that application's grant.

The public SDK source and executable example files are in
[commandoperator/cmdop-sdk](https://github.com/commandoperator/cmdop-sdk).
Review commands before running them on your own machines.

[SDK](README.md) · [Authentication](authentication.md)
