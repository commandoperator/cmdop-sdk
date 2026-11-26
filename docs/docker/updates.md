# Client updates in Docker

**In short:** Rebuild the reference image to pick up the latest stable CMDOP release and recreate the container with its existing machine-home volume.

## Upgrade the reference application

From the same Compose project and the same reference checkout used for enrollment:

```sh
cd reference
docker compose up -d --build report-app
docker compose exec -T report-app cmdop --version
docker compose exec -T report-app python /opt/report/wait_online.py
```

The installer verifies the release binary during the build. The home volume holds
the identity and registration. Use the registered machine ID to confirm that your
application can still read the report after the container reconnects.

## Updates while the container is running

The published reference with CMDOP 0.1.16 needs the rebuild procedure above.
Its foreground client can check for a release, but its supervisor detection
recognizes launchd and systemd. Docker restart policies need explicit client
support. The reference keeps the executable in a directory owned by the service user,
runs CMDOP as PID 1 and sets `CMDOP_RESTARTED_BY_CONTAINER=1` alongside
`restart: unless-stopped`. A client release that supports this setting is required.

For runtime updates an integrating image needs a writable executable directory
for the service user, a supervisor that restarts the client after installation,
and a client release that recognizes that supervisor. Keep the app and the
surrounding system directories read-only to that user. Rebuilding the image also
updates the baseline used when a container is replaced.

[Docker overview and enrollment](../docker.md)
