# SDK authentication

Give each program its own agent token so its calls have a distinct name in your record.

**In short:** Set `CMDOP_TOKEN` to an agent token and `CMDOP_URL` to your page's address. Create and revoke agent access on your page.

## Settings

```bash
export CMDOP_URL="https://<address>.cmdop.dev"
# Supply CMDOP_TOKEN through your shell environment or secret manager.
```

TypeScript `connect({ url, token })` and Python `connect(url=..., token=...)` can receive settings
explicitly. Read secrets from the environment; do not hardcode them. Use `contour` instead of `url`
when supplying the address label alone. Giving both is an error.

## Choose access for the work

Start with `read` for machine information and file reads. Commands and task creation need `exec`;
file changes need `write`; screenshots need `screen`; installed AI agent prompts need `agent`.
Check each [tool's risk class](https://docs.cmdop.ai/reference/tools) before granting access.

A grant does not override the machine's [ceiling](https://docs.cmdop.ai/concepts/grants-and-ceiling) or operating
system permissions. A refused call is an error, not a reason to broaden access automatically.

## Revoke

Revoke the agent on your page to prevent its next call. Use separate tokens for separate programs
and AI clients so you can revoke one without replacing every integration's settings.

## Failures

For [unauthorized](https://docs.cmdop.ai/reference/errors/unauthorized), check that the token is present and belongs to
the page you configured. For [denied](https://docs.cmdop.ai/reference/errors/denied), check the required risk class with
the owner. Do not print token values in an issue, URL, screenshot or log.

[Quickstart](quickstart.md) · [Errors and cancellation](errors-and-cancellation.md)
