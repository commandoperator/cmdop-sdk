# Read a build report from a container

“Did the tests pass?” A product can answer that question by giving an agent one
tool, `latest_build`. In this example the tool reads a JSON report packaged
with the application. Calling it returns the job name and test counts. No build
starts when you ask the question.

## Try it locally

From the root of this repository, with Docker running:

```sh
docker build -t cmdop-build-report:local examples/python/local_mcp
docker run --rm --network none --cap-drop ALL cmdop-build-report:local python /opt/report/read_report.py
```

The second command starts a local MCP session, discovers the tool and calls it.
The report travels over the process's standard input and output. Its result is:

```json
{"job": "demo-build", "tests_passed": 3, "tests_failed": 0}
```

## Ask from a connected chat

Follow the [Docker enrollment guide](https://github.com/commandoperator/cmdop-sdk/blob/09543b0/docs/docker/connect.md)
to add the reference application to your contour. Give the caller command execution access on that machine.
Use the name you chose at enrollment in this prompt:

> On my CMDOP machine named my-product-demo, run
> `/usr/local/bin/python /opt/report/read_report.py` and tell me the job name
> and how many tests passed or failed.

In a hosted run on November 26, 2026, the external MCP client selected the online
Linux ARM64 container and ran the helper. The container's local `latest_build`
tool returned `demo-build`, three passed and zero failed. The owner could see
the successful `exec_run` on that machine's Activity tab.

A caller with file-read access can also ask, “Read `/opt/report/build.json`
on my-product-demo and summarize it.” In the same run, that request returned the
same report and appeared separately as `fs_read` in Activity.

[SDK and chat setup for this container](https://github.com/commandoperator/cmdop-sdk/blob/09543b0/docs/docker/call.md) ·
[Python caller](../examples/python/local-mcp.py) ·
[TypeScript caller](../examples/typescript/local-mcp.ts)
