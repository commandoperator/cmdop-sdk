# Errors and cancellation

A refused tool call and a broken connection need different handling.

**In short:** Branch on `CmdopError.code`. `CarrierError` means no answer arrived. Deadlines use milliseconds in TypeScript and seconds in Python.

## TypeScript

Requires a selected machine and `exec` access for this command.

```ts
import { CarrierError, CmdopError } from "@cmdop/sdk";

try {
  await box.run("printf 'hello\\n'", {}, { deadline: 5_000 });
} catch (error) {
  if (error instanceof CmdopError) console.error(error.code);
  else if (error instanceof CarrierError) console.error("Connection failed before an answer arrived.");
  else throw error;
}
```

Pass `signal: controller.signal` in call options to cancel with an `AbortController`.
Aborting the signal or leaving a streamed command ends that call as `cancelled`.
Read `run.result` to handle its final result or error.

## Python

```python
try:
    box.run("printf 'hello\\n'", deadline=5)
except cmdop.CmdopError as error:
    print(error.code)
except cmdop.CarrierError:
    print("Connection failed before an answer arrived.")
```

Call `run.cancel()` explicitly when stopping a synchronous stream early.
Use `connect_async()` and task cancellation for asynchronous callers; release clients with
their context managers.

## Decide what to do next

| Code or failure | Next action |
|---|---|
| `unauthorized` | Check token and page address without printing the token. |
| `denied` | Ask the owner to review the required risk class. |
| `permission_missing` | Follow the human action in the details before retrying. |
| `unknown_tool` | Check the selected machine's version and advertised tools. |
| `timed_out` | Check whether the work is still needed before issuing another call. |
| `cancelled` | Treat it as an intentional end; do not restart automatically. |
| `CarrierError` | The outcome can be uncertain; inspect state before repeating a write or command. |

The shorter of the caller's deadline and the tool's own timeout applies.
Do not blindly retry operations with side effects after losing the connection.
A task created through `task.start` has its own lifecycle; cancellation of a later output read
does not stop that task.

[SDK](README.md) · [Error reference](https://docs.cmdop.ai/reference/errors)
