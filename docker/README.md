# Run a connected Docker application

Connect the sample application to your CMDOP account and ask an agent for its build report.
From the SDK checkout, with Docker Compose running:

```sh
cd docker/reference
./connect --name my-product-demo
```

Follow the sign-in prompts. When the machine is online, ask your connected agent:

> On my-product-demo, run `/usr/local/bin/python /opt/report/read_report.py`
> and tell me the job name and test counts.

The application's local MCP server reads a packaged report for `demo-build` with
three passed tests and zero failures. To read it from your own application,
follow the [SDK caller guide](../docs/docker/call.md). Keep the Compose volume
to reuse the enrolled machine identity.

[Compose file](reference/compose.yaml) · [Connection guide](../docs/docker/connect.md) · [Updates](../docs/docker/updates.md)

The files in `reference/` come from [cmdop-docker](https://github.com/commandoperator/cmdop-docker/tree/main/reference).
Contribute application changes there. The [source revision](SOURCE) identifies this copy.
