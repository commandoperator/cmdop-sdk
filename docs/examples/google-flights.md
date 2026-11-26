# Search Google Flights with Fli

**In short:** Run Fli on your selected machine through CMDOP and use the returned fares to write a local report.

“Which nonstop flights leave Bali for Bangkok on my travel date?” The Google Flights example
asks Fli, an unofficial Google Flights interface running on your selected machine. It checks
both Bangkok airports for one adult, then returns up to three distinct flights ordered by USD
fare, with local departure times and booking links when available. Prices reflect the time
of the search. The example only searches.

## From a connected chat

Ask your connected agent: “Use Fli on my Mac through CMDOP to find nonstop flights
from Bali to Bangkok on my travel date. Show the cheapest options in USD.” Include
your date and, if you have several Macs connected, the machine name.

For the agent: call `docs_read` with path `reference/mcp` and follow
[Call a local MCP tool from a connected chat](https://docs.cmdop.ai/reference/mcp#call-a-local-mcp-tool-from-a-connected-chat).
Select the requested online machine, resolve its `uvx` executable, and pass the
provided Python client to `exec_run` on stdin. The command runs against the prepared
Fli environment on that machine. Check the command result before reporting fares.

## From Python or TypeScript

On the target machine, install uv and prepare the Fli environment once:

```bash
uvx --from 'flights[mcp]==0.11.1' python -c "import fli.mcp.server"
command -v uvx
```

With the SDK connection and machine ID set as described in the [checkout instructions](run.md), set `FLI_UVX` to the absolute
path printed on the target and `FLIGHT_DATE` to your travel date in YYYY-MM-DD format.
From the checkout, run the example in both languages:

```bash
ONLY=google-flights EXAMPLES_EXEC=1 EXAMPLES_NETWORK=1 bash examples/run.sh
```

The runner reports whether each caller succeeded. To see fares directly, set the same two
effect flags and run the Python example:

```bash
EXAMPLES_EXEC=1 EXAMPLES_NETWORK=1 uv run --with cmdop==3.6.0 python examples/python/google-flights.py
```

An empty flight list means the search completed with no matching fares. A failed search
exits with an error. The pinned local package runs offline from the uv cache while Fli
uses the target machine's network to request current fares.

## Save the latest fare report on the selected machine

The Python example prints JSON on the computer running the SDK. To leave a report
on the traveler's Mac, use the same machine ID for a second call after a successful
search. Format the returned search time, travel date and fares as Markdown. Include
a booking link only when Fli supplies one.

Call [`fs_write`](https://docs.cmdop.ai/reference/tools/fs_write) with the traveler's chosen path as
`path` and the formatted report as `data`. For example, use
`Desktop/Bangkok flights.md` when the Mac's Desktop is in the user's home folder.
The caller needs write access on that machine.

- On the first run, pass `create_only: true` and save the returned `sha256`.
- On later runs, pass the previous successful write's hash as `expect_sha256`.
  If someone edited the report, inspect the change before replacing it.
- If the search fails, keep the last successful report. A successful empty result
  can replace it with the check time and “No matching flights.”
