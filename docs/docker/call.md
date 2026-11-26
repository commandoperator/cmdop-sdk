# Read a report from a connected container

Start with an [enrolled container](connect.md) that is online.

## Read the report with the Python SDK

For an application that only needs the report, give its agent token the
`read` grant. Set `CMDOP_URL` to your contour URL, `CMDOP_TOKEN` to that token.
From the same `reference/` directory, read the registered container's public
machine ID and pass it directly to the caller:

```sh
CMDOP_MACHINE=$(docker compose exec -T report-app cmdop key) && export CMDOP_MACHINE
docker compose exec -T -e CMDOP_URL -e CMDOP_TOKEN -e CMDOP_MACHINE report-app \
  python /opt/report/read_via_sdk.py
```

The bundled SDK sends `fs_read` to that machine for `/opt/report/build.json`.
It prints the packaged report for `demo-build` after checking that the response is complete.
If you configured filesystem roots on the machine, include `/opt/report` in the
allowed directories. The next example exercises the application's MCP server.

## Read the container's report from your agent

Use a container running the full reference application, enrolled and online in your
contour. Its machine name in the following prompt is `my-product-demo`. The caller
needs the CMDOP command execution grant on that machine.

> Using CMDOP, find the online machine named my-product-demo. If the name is
> ambiguous, ask me to select its machine ID. On that machine, run
> `/usr/local/bin/python /opt/report/read_report.py` with a 60-second timeout.
> Tell me the job name and how many tests passed and failed.

The helper calls the container's local MCP tool. A successful call returns
`demo-build`, three passed tests and zero failures. These values come from the
packaged report. If CMDOP reports a timeout or denies execution, report that
outcome to the caller.

To run the same check from the Python and TypeScript SDKs, open the public
SDK repository's `examples/` directory on the calling computer. Configure
`CMDOP_URL`, `CMDOP_TOKEN` and `CMDOP_MACHINE` for the enrolled container.
The following paths refer to files inside that container:

```sh
export LOCAL_MCP_PYTHON=/usr/local/bin/python
export LOCAL_MCP_HELPER=/opt/report/read_report.py
EXAMPLES_EXEC=1 ONLY=local-mcp ./run.sh
```

[How the local MCP call works](../commands-and-tasks.md#call-a-local-mcp-tool)
