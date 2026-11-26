# Prompt Codex with the SDK

**In short:** Check that Codex on a particular computer can receive a prompt from your application and return a known answer.

Use the machine ID for the computer where you normally run Codex. Its local Codex installation must already be authenticated. Configure the caller with `CMDOP_URL`, `CMDOP_TOKEN` and `CMDOP_MACHINE`
as described in the [checkout instructions](run.md).
The token needs the `read` and `agent` grants.

From the root of the public SDK checkout, run:

```bash
ONLY=prompt-codex AGENT_PROMPT=1 bash examples/run.sh
```

The runner selects the Python and TypeScript examples for Codex. Each caller
checks that the named agent is available and sends a text-only prompt asking
for `CMDOP_AGENT_OK`. A completed response must identify `codex` and contain
the expected text. If the task is still running, use the returned task handle
to follow its output. If Codex is busy, wait for it to become available.

[Python source](https://github.com/commandoperator/cmdop-sdk/blob/b1e820e9df3c202da3723172c96a3dc4d6e518c9/examples/python/agents/codex.py) · [TypeScript source](https://github.com/commandoperator/cmdop-sdk/blob/b1e820e9df3c202da3723172c96a3dc4d6e518c9/examples/typescript/agents/codex.ts) · [Agent sessions and tasks](../agents.md)
