# CMDOP machine base image candidate

Each build takes the latest stable CMDOP release for its target Linux architecture
(amd64 or arm64). Docker fetches the official installer as a build input. When a
release changes the installer, Docker rebuilds the installation layer. The installer
checks the binary against that release's SHA-256 before installing it.

Rebuild the image and recreate the container to upgrade. Its named home volume
preserves registration. Inspect the installed version with the command below.

Build for the local Docker engine and check the installed binary from this directory:

```sh
docker build -t cmdop-machine:local .
docker run --rm --network none cmdop-machine:local --version
```

For the identity persistence check, choose a fresh named volume for this instance.
Run the following command twice with the same volume. The first interactive run lets you review the release terms. If you accept them,
the client saves your choice in the volume. The two public keys should match.

```sh
docker run --rm -it --network none --cap-drop ALL --security-opt no-new-privileges \
  --mount type=volume,source=cmdop-reference-home,target=/home/cmdop \
  cmdop-machine:local key
```

Keep this home volume private and give each additional instance its own volume.
Online operation requires enrollment. The product application and its SDK caller
will be verified separately; this candidate currently covers machine packaging.

### First sign-in

Use the same home volume for each sign-in step and the foreground process.
Set a recognizable machine name before enrollment. From an interactive shell:

```sh
machine() {
  docker run --rm -it --cap-drop ALL --security-opt no-new-privileges \
    --mount type=volume,source=cmdop-reference-home,target=/home/cmdop \
    cmdop-machine:local "$@"
}
machine config set name my-product-demo
machine signin email "$EMAIL_ADDRESS"
machine signin code --email "$EMAIL_ADDRESS" --code "$EMAIL_CODE"
```

Supply your own email and the code sent to it. If the response requests a second
factor, use its attempt value with
`machine signin second-factor --attempt "$ATTEMPT" --code "$AUTHENTICATOR_CODE"`.
After admission, `machine run --no-sessions` starts the foreground client using
the saved configuration. Verify the named machine appears online before running SDK examples.

### Updates in a running reference container

The reference image keeps the executable in `/opt/cmdop/bin`, which belongs
to UID 10001. The command in `/usr/local/bin` points there. Compose starts
the client as PID 1 with `restart: unless-stopped` and sets
`CMDOP_RESTARTED_BY_CONTAINER=1`. The opt-in needs a client release that
recognizes it. CMDOP 0.1.16 recognizes launchd and systemd only.

Use the rebuild procedure for released 0.1.16 containers. For a supporting
release, verify the update in a disposable enrolled instance when a newer
signed release is available. Record the running version, machine ID and Docker
restart count. Allow the scheduled check to run, or use `cmdop update --now`
to wake the same updater. Confirm an increased restart count on the same
container, the new running version in machine status, and the same machine ID
online. Then read the report using its existing agent grant. Recreate from a
freshly rebuilt image to carry that version into a replacement container.
