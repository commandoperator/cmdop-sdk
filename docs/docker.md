# Docker

**In short:** Build the SDK's sample application and read a build report over MCP inside a container. The example runs offline after the image is built.

## Try the report application

With Docker running, build the application from the
[SDK example source](https://github.com/commandoperator/cmdop-sdk/tree/b1e820e9df3c202da3723172c96a3dc4d6e518c9/examples/python/local_mcp):

```sh
docker build -t cmdop-report-fixture:local 'https://github.com/commandoperator/cmdop-sdk.git#b1e820e9df3c202da3723172c96a3dc4d6e518c9:examples/python/local_mcp'
docker run --rm --network none --cap-drop ALL cmdop-report-fixture:local python /opt/report/read_report.py
```

The client opens a stdio session, discovers the application's `latest_build` tool
and calls it. The expected output is the report packaged with the example:

```json
{"job": "demo-build", "tests_passed": 3, "tests_failed": 0}
```

To call the same tool from an MCP client on the host, configure its stdio server
command as `docker` with these arguments:

```json
["run", "--rm", "-i", "--network", "none", "--cap-drop", "ALL", "cmdop-report-fixture:local"]
```

Keep stdin open with `-i` and leave TTY allocation off so the client can exchange
protocol messages with the server. This example runs locally without a CMDOP account.

## Connect a container to your contour

An image that includes the CMDOP machine client is in development. A locally
built preview has run on Linux arm64. Public registry distribution and a hosted
end-to-end enrollment of the example are pending. The report fixture above runs
the application side only.

For a machine already connected to your contour, follow the
[local MCP example](commands-and-tasks.md#call-a-local-mcp-tool).
