# Installed AI agents

Ask supported AI agent programs installed on a computer through one set of machine methods.

**In short:** Call `box.agent.list`, then `box.agent.prompt`; preserve its `session` for follow-up prompts and its `task` for longer runs.

## Prerequisites

The token needs the `agent` risk class and the machine needs its agent configuration.
These calls use the installed program's authentication and available tier.
The public tiers are `text_only` and `read_only`: do not expect these prompts to edit files
or execute commands. See [Ask an agent](https://docs.cmdop.ai/guides/ask-an-agent) for setup.

## TypeScript

```ts
console.log((await box.agent.list({})).agents.map((agent) => agent.id));
const answer = await box.agent.prompt({
  prompt: "Explain the difference between a command and a persistent task.",
});
console.log(answer.state, answer.text);
if (answer.state === "done" && answer.session) {
  const follow = await box.agent.prompt({
    prompt: "Give one example of each.",
    session: answer.session,
  });
  console.log(follow.text);
}
```

## Python

```python
print([agent.id for agent in box.agent.list().agents])
answer = box.agent.prompt(
    prompt="Explain the difference between a command and a persistent task."
)
print(answer.state, answer.text)
if answer.state == "done" and answer.session:
    follow = box.agent.prompt(prompt="Give one example of each.", session=answer.session)
    print(follow.text)
```

The answer contains a state, task id and, when available, text and a session.
A `running` state means the answer is not finished: use `task.output` to follow it and
`agent.cancel` to stop it. Do not print an absent `text` as a successful final answer.

## Errors

[tool_refused](https://docs.cmdop.ai/reference/errors/tool_refused) means the requested action was refused.
[sandbox_unavailable](https://docs.cmdop.ai/reference/errors/sandbox_unavailable) means the required confinement is
unavailable; follow the tool's guidance rather than attempting a different tier automatically.

[SDK](README.md) · [Agent prompt reference](https://docs.cmdop.ai/reference/tools/agent_prompt)
