# Run the SDK examples

**In short:** Start with machine discovery, then select a program and enable its required access.

## Run the executable examples

The public repository includes [TypeScript and Python programs](https://github.com/commandoperator/cmdop-sdk/tree/main/examples).
Start with `examples/typescript/hello.ts` or `examples/python/hello.py` from a local checkout.
Follow [quickstart](../quickstart.md) to bring a computer online and set `CMDOP_URL`
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

## Catalog-based checkout runner

In a checkout containing `examples/catalog.json` and `examples/run.sh`, the catalog selects the
programs and records their language paths and required access. Older checkouts do not include
this runner; use the first-read instructions above until you have a revision containing it.
The combined runner requires Node.js 20+, Python 3.10+, npm and uv. It compiles TypeScript to
JavaScript rather than assuming Node can execute every `.ts` file directly.

From that checkout's root:

```bash
bash examples/run.sh --list
bash examples/run.sh --plan
```

`--list` validates the source inventory. `--plan` checks selection without installing packages
or connecting. For a live run, set `CMDOP_URL` and `CMDOP_TOKEN` explicitly; the runner does not
read an owner token from local configuration. Set `CMDOP_MACHINE` to the exact machine ID for
command and named-agent examples.

The default selection contains read/discovery programs. `agents` only lists installed agents;
it does not send a prompt. Choose `prompt-codex` or `prompt-claude-code` explicitly:

```bash
ONLY=prompt-codex AGENT_PROMPT=1 bash examples/run.sh
```

Command execution uses `ONLY=command` with `EXAMPLES_EXEC=1`. Choosing an ID does not grant its
required access; setting an effect flag does not select more programs automatically. The agent
examples request `text_only` and need both discovery access and the agent risk class, subject
to the machine's configuration. Installation does not establish valid vendor authentication.

The catalog pins the SDK package version; `VERSION` can select another explicit release.
`--build-only` installs compilation dependencies and compiles the selected TypeScript without
executing examples. It still checks selection and effect opt-ins.

| Runner result | Meaning |
|---|---|
| `SMOKE` | The legacy demonstration process completed; no workflow verification is inferred |
| `PASS` | The example's bounded result assertions passed |
| `RUNNING` | An agent answer is unfinished; keep its task handle |
| `UNKNOWN` | The local wait ended without establishing the remote outcome; do not blindly retry |
| `FAIL` or `SKIP` | The pair is incomplete; inspect prerequisites or the reported condition |

The runner omits raw process/model output. An unfinished or uncertain effectful run prevents
an automatic second-language attempt. Source availability, local checks, a real machine run
and public delivery are separate facts.

## Follow a running agent prompt

If the runner prints `RUNNING typescript prompt-codex task=15`, the selected
machine has already accepted the prompt. The number is an example. Use the
number printed by your run and keep the same `CMDOP_MACHINE`. The next language
may show `SKIP` because the first prompt is still active.

From a connected MCP chat, ask: “On the same machine, call `task_output` for
task 15. Tell me whether it is still running and what text is available.”
In Python, use the same SDK connection as the original caller:

```python
import os
import cmdop

task_id = int(input("Task number from the runner: "))
with cmdop.connect() as client:
    machine = client.machine(os.environ["CMDOP_MACHINE"])
    output = machine.task.output(task=task_id)
    print("Running" if output.running else "Finished")
    print(output.text)
```

For TypeScript, save this as `follow.mts` in your SDK application and pass the
task number as the first argument when running it with your TypeScript runner:

```typescript
import { connect } from "@cmdop/sdk";

const machineId = process.env.CMDOP_MACHINE?.trim();
const task = Number(process.argv[2]);
if (!machineId || !Number.isSafeInteger(task) || task < 1) {
  throw new Error("Set CMDOP_MACHINE and supply a positive task number.");
}

const client = connect();
try {
  const output = await client.machine(machineId).task.output({ task });
  console.log(output.running ? "Running" : "Finished");
  console.log(output.text);
} finally {
  await client.close();
}
```

An empty first read is possible. While `running` is true, read the same task
again, even if answer text is already visible. For this example, check that
`running` is false and that the final text is exactly `CMDOP_AGENT_OK`.
