# Read a report from the product's local MCP server

The sample app ships a deterministic build report. Its stdio tool `latest_build`
reads that file. The SDK caller selects a machine and runs a fixed helper under its
exec grant. The helper starts the server, discovers the tool and validates its answer.

Copy this directory into the product on the target. Use a Python 3.13 environment
with `fastmcp==4.2.6` and `mcp==2.3.0`. Run `python read_report.py` in that environment
to check setup. Set LOCAL_MCP_PYTHON and LOCAL_MCP_HELPER in the calling environment
to the absolute paths of that interpreter and read_report.py **on the target**.

With CMDOP_URL, CMDOP_TOKEN and CMDOP_MACHINE set for that target, run the paired
examples from the SDK examples directory:

```sh
EXAMPLES_EXEC=1 ONLY=local-mcp ./run.sh
```

Through CMDOP MCP, select the same machine and call exec_run with argv containing
those two absolute paths and timeout_secs set to 60. Expect demo-build, three passed
tests and zero failures. These counts come from a packaged sample report.

### Container fixture

Build the standalone sample server from this directory:

```sh
docker build -t cmdop-report-fixture .
docker run --rm --network none cmdop-report-fixture python /opt/report/read_report.py
```

The second command exercises discovery and the report tool inside the container. A stdio
MCP client can instead launch `docker run --rm -i --network none cmdop-report-fixture`.
The container needs no listening port. This fixture packages the application side. The
full reference image will also start the CMDOP machine client and persist its registration.
