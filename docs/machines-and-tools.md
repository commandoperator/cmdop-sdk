# Machines and tools

Choose a target once, then call its typed tool methods.

**In short:** `client.machines()` lists machines; `client.machine(nameOrId)` selects one. Grouped and flat methods call the same tool.

## Select a machine

`machines()` returns rows with an id, name and online state. Select by id if names may change.
`machine()` without a name asks the server to choose the one online machine; when the choice
is ambiguous, specify a name or id. An offline machine cannot answer a call.

## Machine methods

In TypeScript, `box.fs.read({ path: "/tmp/notes.txt" })` and
`box.fs_read({ path: "/tmp/notes.txt" })` call the same tool.
In Python, `box.fs.read(path="/tmp/notes.txt")` and `box.fs_read(path="/tmp/notes.txt")` do the same.

Arguments and typed results follow the [tool reference](https://docs.cmdop.ai/reference/tools).
The short forms `run`, `stream` and `screenshot` provide convenient command and image handling.
Use `client.call("sys_info", {}, { machine: "<machine>" })` in TypeScript or
`client.call("sys_info", {}, machine="<machine>")` in Python for a call by tool name.

## Client methods

These tools have no machine argument: `machines_list`, `tasks_list`, `history_search`,
`docs_read` and `showtime_guide`. Call them on the client, not on `box`.
For example, `await client.docs_read()` in TypeScript or `client.docs_read()` in Python
returns the documentation index as text. Supply `path` to read a page.

## Discover before using

Read a row's advertised tools and the current reference before using a capability on an older machine.
An older machine may answer [unknown_tool](https://docs.cmdop.ai/reference/errors/unknown_tool). Update that machine
or choose an available tool; changing a method's spelling does not add a missing capability.

[SDK](README.md) · [Versions and support](versions-and-support.md)
