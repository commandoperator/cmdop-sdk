# Give an assistant read access to a computer

You want an assistant to tell you about a build machine. Start it with a
dedicated agent token that has the `read` grant. It can inspect the computer
while you keep control of who can run commands.

## Try it on a test machine

Choose an online Mac or Linux machine you own. Connect the agent using its
read-only token and give it the machine ID. Ask:

> On this machine, use CMDOP’s sys_info to tell me how many CPUs it has.
> Then try exec_run once with the command true and tell me the outcome.

The first call should report a CPU count. The second requests permission to
run a harmless command. With this token, the expected response from the SDK
endpoint is HTTP 403 with the code `denied`. An agent interface may omit tools
outside its grant. In that case the command is unavailable in the interface,
and there is no attempted execution to look up.

## What the owner can see

In a local integration test, the same agent token received the following results
through the SDK endpoint. The owner changed the grant only for the last call.

| Agent grant | Request | Response to caller | Owner’s activity record |
|---|---|---|---|
| Read | Read system information | CPU count | `sys_info` · `ok` |
| Read | Run `true` | HTTP 403 | `exec_run` · `denied` |
| Read and execute | Run `echo from-sdk` | stdout contained `from-sdk` | `exec_run` · `ok` |

The owner could look up all three outcomes under the same agent name. You can
leave your reporting assistant read-only. If another workflow needs execution,
use a separate token so the activity records identify which caller ran it.

[Agent tokens and permissions](../docs/authentication.md) ·
[Inspect a machine from the SDK](first-read.md)
