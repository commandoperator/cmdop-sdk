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

The [reference application preview](https://github.com/commandoperator/cmdop-docker/tree/0b9971aea6bc392acfbef945806c656d08b17945/reference)
packages the application, local MCP server, Python SDK and CMDOP machine client together.
To try this revision with Docker Compose, run:

```sh
git clone https://github.com/commandoperator/cmdop-docker.git
cd cmdop-docker
git checkout 0b9971aea6bc392acfbef945806c656d08b17945
cd reference
./connect --name my-product-demo
```

The command builds the image with the latest stable CMDOP client and prompts for
your existing account email and sign-in code. It waits for the registered machine
to connect. Compose saves the machine identity in a named volume. On subsequent
starts, run `docker compose up -d report-app` from the same project.

This revision built successfully on native Linux amd64 and arm64. Each runner
started CMDOP and read the sample report with the network disabled.
[View both Docker checks](https://github.com/commandoperator/cmdop-docker/actions/runs/45805255059).
Hosted sign-in and the external agent call still need end-to-end verification.
The preview is distributed as source.

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

[How the local MCP call works](commands-and-tasks.md#call-a-local-mcp-tool)
