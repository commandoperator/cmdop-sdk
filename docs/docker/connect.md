# Connect a Docker container

The [reference application preview](https://github.com/commandoperator/cmdop-docker/tree/aa96b3869e7d99782550817e483e74df9d364f02/reference)
packages the application, local MCP server, Python SDK and CMDOP machine client together.
To try this revision with Docker Compose, run:

```sh
git clone https://github.com/commandoperator/cmdop-docker.git
cd cmdop-docker
git checkout aa96b3869e7d99782550817e483e74df9d364f02
cd reference
./connect --name my-product-demo
```

The command builds the image with the latest stable CMDOP client and prompts for
your existing account email and sign-in code. It waits for the registered machine
to connect, then prints the SDK machine ID and the contour URL when available.
Look for `my-product-demo` under **All machines**. Compose keeps the machine
identity in a named volume. On subsequent
starts, run `./connect` from the same project to rebuild and reconnect using the
saved link and machine name. If the server refuses a machine you want to enroll
again, run `docker compose stop report-app && ./connect --sign-in`. The home
volume retains its identity. If the contour has reached its machine limit,
review the limit in the dashboard.

This revision built successfully on native Linux amd64 and arm64. Each runner
matched the packaged binary to the stable release checksum and read the sample report with the network disabled.
[View both Docker checks](https://github.com/commandoperator/cmdop-docker/actions/runs/45822269392).
On November 26, 2026, an owner enrolled the Linux ARM64 preview in a hosted
contour. An external MCP client selected the online container, read the report
with `fs_read`, and used `exec_run` to call its local `latest_build` tool.
Both calls appeared in the container's Activity view. Both returned the packaged
report for `demo-build` with three passed tests and zero failures.
The preview is distributed as source.

[Read the report from the connected container](call.md).
