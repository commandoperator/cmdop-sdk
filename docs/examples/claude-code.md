# Prompt Claude Code with the SDK

**In short:** Check that Claude Code on a particular computer can receive a prompt from your application and return a known answer.

Choose the machine where Claude Code is installed and signed in. The SDK profile selects the installed program by its ID, `claude-code`. Configure the caller with `CMDOP_URL`, `CMDOP_TOKEN` and `CMDOP_MACHINE`
as described in the [checkout instructions](run.md).
The token needs the `read` and `agent` grants.

From the root of the public SDK checkout, run:

```bash
ONLY=prompt-claude-code AGENT_PROMPT=1 bash examples/run.sh
```

The runner selects the Python and TypeScript examples for Claude Code. Each caller
checks that the named agent is available and sends a text-only prompt asking
for `CMDOP_AGENT_OK`. A completed response must identify `claude-code` and contain
the expected text. If the task is still running, [read its output using the returned task number](run.md#follow-a-running-agent-prompt). If Claude Code is busy, wait for it to become available.

[Python source](https://github.com/commandoperator/cmdop-sdk/blob/b1e820e9df3c202da3723172c96a3dc4d6e518c9/examples/python/agents/claude-code.py) · [TypeScript source](https://github.com/commandoperator/cmdop-sdk/blob/b1e820e9df3c202da3723172c96a3dc4d6e518c9/examples/typescript/agents/claude-code.ts) · [Agent sessions and tasks](../agents.md)
