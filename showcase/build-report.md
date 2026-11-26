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

## Try it on a connected machine

For a product integration, package the helper with the application that owns the
report. Give a CMDOP agent execution access on that machine and select its ID.
The Python and TypeScript callers run the helper there and validate the returned
report. The local Docker run above verifies the application side independently.

[Application and setup](../examples/python/local_mcp/README.md) ·
[Python caller](../examples/python/local-mcp.py) ·
[TypeScript caller](../examples/typescript/local-mcp.ts)
