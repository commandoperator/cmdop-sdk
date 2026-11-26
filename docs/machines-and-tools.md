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

## Ask the person at a machine to choose

When someone requests an on-screen demo, select their online machine and check its
advertised tools for `stage_show`. This control operation plays the CMDOP opening and
displays two to four buttons. Give each option a stable ID so changing its label preserves
the meaning of the response. Here `box` is the selected machine from the quickstart.

```python
reply = box.stage.show(
    question="Which demo would you like?",
    options=[{"id": "files", "label": "Files"}, {"id": "apps", "label": "Apps"}],
)
print(reply.answer if reply.outcome == "answered" else reply.outcome)
```

```typescript
const reply = await box.stage.show({
  question: "Which demo would you like?",
  options: [{ id: "files", label: "Files" }, { id: "apps", label: "Apps" }],
});
console.log(reply.outcome === "answered" ? reply.answer : reply.outcome);
```

A connected MCP caller supplies the same question and options in `tools/call`,
using `params.name = "stage_show"` and the selected `machine` in `params.arguments`.
The stage waits up to 45 seconds. Handle `closed`, `timeout` and `paused` as outcomes
without a selection. An answer records the button ID. The identity of the person at
the screen is unknown.

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
