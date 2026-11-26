# Embed CMDOP in a report application

This local example uses the report application from the public SDK. CMDOP runs in
the foreground. Its caller starts the application's stdio MCP server on demand.

From the repository root, build the application with Docker Compose:

```sh
cd reference
docker compose build report-app
```

Compose builds the machine base with the latest stable CMDOP client and takes the
report fixture from a pinned SDK revision. To upgrade an enrolled instance from the same Compose project, run:

```sh
docker compose up -d --build report-app
```

Compose rebuilds the image and replaces the container when its image changes.
The existing home volume carries the machine identity into the replacement.

Check the packaged software offline:

```sh
docker run --rm --network none cmdop-report-app:local --version
docker run --rm --network none --entrypoint python cmdop-report-app:local /opt/report/read_report.py
```

The report caller checks that the local server offers `latest_build` and returns
the packaged `demo-build` result.

### Register and start the machine

From `reference/`, run the first-time connection command in a terminal:

```sh
./connect --name my-product-demo
```

It builds the image, lets you review CMDOP's terms, asks for your existing account
email and code, and prompts for an authenticator code if required. CMDOP selects
the account's contour and saves the machine identity in the Compose home volume.
Once registration succeeds, the command starts the foreground client in a detached
container. On first sign-in the command prints the contour URL. Run `./connect` again to rebuild and reconnect using the saved link without entering an email. Omitting `--name` preserves the registered name. If the volume already holds an
admitted identity, CMDOP reuses its original contour. Use a separate Compose
project and volume for an instance belonging to another account. The command waits up to 45 seconds for CMDOP to report its connection online.
If the wait expires, the client keeps running. Inspect `docker compose logs report-app`. On subsequent starts use
`docker compose up -d report-app` from the same project.

If the server refuses a previously enrolled machine and you want to grant it access
again, run this from the same Compose project. The existing home volume retains its key and name.

```sh
docker compose stop report-app && ./connect --sign-in
```

If CMDOP reports that the contour has reached its machine limit, check the plan
in the dashboard. Repeating account sign-in cannot increase that limit.

For the external SDK example, set the target interpreter to `/usr/local/bin/python`
and its helper to `/opt/report/read_report.py`. Use `docker compose stop report-app`
to stop it while keeping the identity for the next start. An enrolled container
starts again when the Docker engine restarts, unless you explicitly stopped it.

### Call the SDK from the running application

Supply the application with an agent token that can read the report on the registered
container machine. Set `CMDOP_URL`, `CMDOP_TOKEN` and `CMDOP_MACHINE` in the caller's
environment. After connection, `./connect` prints the SDK machine ID. To select
this container directly from the same Compose project, set it in your shell:

```sh
CMDOP_MACHINE=$(docker compose exec -T report-app cmdop key) && export CMDOP_MACHINE
```

The ID is the container machine's public key. The agent token grants access.
From the same Compose project, run:

```sh
docker compose exec -e CMDOP_URL -e CMDOP_TOKEN -e CMDOP_MACHINE report-app \
  python /opt/report/read_via_sdk.py
```

The program asks the CMDOP service for `/opt/report/build.json` using `fs_read`.
It prints the validated report on success. On a fresh machine, the default file policy permits this path. The image
ships the report as a readable file for the application user (UID 10001).
A read-only agent grant is sufficient for this SDK call. If you restrict
`roots` in `ceiling.json`, include `/opt/report` among the permitted directories
for this example. See the [machine file policy](https://docs.cmdop.ai/reference/config/ceiling-json). The token is supplied at execution time and is separate from the
machine identity stored in the home volume.
