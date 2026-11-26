"""Wait for the machine's authenticated connection after enrollment."""
import json
import subprocess
import time


def wait_online(timeout=45):
    deadline = time.monotonic() + timeout
    state = "starting"
    while (remaining := deadline - time.monotonic()) > 0:
        try:
            result = subprocess.run(
                ["cmdop", "control", "status.get"],
                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                timeout=min(3, remaining),
            )
            if result.returncode:
                state = "control socket unavailable"
            else:
                link = json.loads(result.stdout)["link"]
                state = link["state"]
                if state == "up":
                    contour = link.get("contour") or {}
                    address = contour.get("base_url")
                    print(f"CMDOP is online at {address}." if address else "CMDOP is online in your contour.")
                    return
                if state == "failed":
                    reason = link.get("reason") or "The client could not establish a connection."
                    raise SystemExit(
                        f"Connection failed: {reason}\n"
                        "Check the configured server address and TLS settings, then restart report-app."
                    )
                if state == "refused":
                    if link.get("reason") == "over_plan":
                        raise SystemExit("This contour has reached its machine limit. Check the contour plan.")
                    raise SystemExit(
                        "The server refused this machine. To enroll it again, run "
                        "docker compose stop report-app && ./connect --sign-in from reference/."
                    )
        except (ValueError, KeyError, TypeError, subprocess.TimeoutExpired):
            state = "status unavailable"
        time.sleep(min(1, max(0, deadline - time.monotonic())))
    raise SystemExit(f"Connection pending ({state}). Check docker compose logs report-app.")


if __name__ == "__main__":
    wait_online()
