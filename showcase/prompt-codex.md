# Ask the Codex installed on your Mac

A chat connected to CMDOP can ask the Codex program on your Mac a question.
Try a short request with a recognizable answer so you can tell which agent
responded. Choose a connected Mac where Codex is installed and signed in.
The caller needs permission to discover and prompt agents on that machine.

> On my Mac, list the installed agents. Ask Codex in text-only mode to reply
> with exactly CMDOP_AGENT_OK. If it is still working, follow that task on the
> same Mac and show me the final answer.

In a live run through CMDOP MCP, the Mac offered both Codex and Claude Code.
The caller selected Codex explicitly. After 30 seconds the first call returned
a task number. Reading that task initially returned an empty screen, then the
answer appeared. The final read showed the task had finished with
`CMDOP_AGENT_OK`. Only one prompt was sent.

## Try it from your application

The [Python example](../examples/python/agents/codex.py) and
[TypeScript example](../examples/typescript/agents/codex.ts) select the same
agent by ID. Both check whether Codex is available and preserve the task number
when the prompt outlasts the initial wait. Use that number with the same machine
ID to read the output. [SDK checkout instructions](../docs/examples/run.md) ·
[Installed agent reference](../docs/agents.md)
