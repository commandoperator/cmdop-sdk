# SDK examples

From an MCP connection, call `docs_read` with path `reference/sdk/examples` to open this index. Pass the path of a recipe to read its instructions.

**In short:** Use [quickstart](quickstart.md) for the first complete program; choose a workflow below for the next step.

## Choose an example

| Workflow | Required risk classes | Example |
|---|---|---|
| Find an online machine and inspect its OS | `read` | [Quickstart](quickstart.md) |
| Read a file and check truncation | `read` | [Files and screenshots](files-and-screen.md) |
| Run a command and print its exit code | `exec` | [Commands](commands-and-tasks.md#commands) |
| Follow output as it arrives | `exec` | [Streaming](commands-and-tasks.md#streaming) |
| Start work and read it after reconnecting | `exec`, `read` | [Tasks](commands-and-tasks.md#tasks-that-outlive-the-call) |
| Ask an installed AI program | `agent` | [Installed agents](agents.md) |
| Capture the computer's screen | `screen`, OS permission | [Screenshots](files-and-screen.md#capture-a-screen) |

The language references cover [TypeScript](typescript.md) and
[Python](python.md), including resource cleanup. Workflow snippets use the connected
client and selected `box` from the quickstart; run them inside its `try` or context-manager block.

## Published source programs

[Browse Python and TypeScript sources](examples/catalog.md).

## Run the executable examples

[Set up and run a first example](examples/run.md).

## Catalog-based checkout runner

[Select a workflow and interpret results](examples/run.md#catalog-based-checkout-runner).

## Search Google Flights through a local MCP server

[Search flights through Fli](examples/google-flights.md).

## Save the latest fare report on the selected machine

[Save the report on your Mac](examples/google-flights.md#save-the-latest-fare-report-on-the-selected-machine).

## Build an integration

Use a dedicated token for each application. Discover machines, select an explicit id and call the
tool you need. Keep tool arguments typed; handle refusal codes and uncertain connection outcomes.
For a custom AI integration, have the model propose a supported tool call, validate it against
the tool contract, and execute it under that application's grant.

The public SDK source and executable example files are in
[commandoperator/cmdop-sdk](https://github.com/commandoperator/cmdop-sdk).
Review commands before running them on your own machines.

[SDK](README.md) · [Authentication](authentication.md)
