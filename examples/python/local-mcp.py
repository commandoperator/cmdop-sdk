"""Read the example product's build report on an explicitly selected machine."""
import json
import os

import cmdop

if os.environ.get("EXAMPLES_EXEC") != "1":
    raise SystemExit("Set EXAMPLES_EXEC=1 to run the example helper.")
target = os.environ["CMDOP_MACHINE"].strip()
if not target:
    raise SystemExit("Set CMDOP_MACHINE to the target ID.")
with cmdop.connect() as client:
    result = client.machine(target).exec_run(
        argv=[os.environ["LOCAL_MCP_PYTHON"], os.environ["LOCAL_MCP_HELPER"]],
        timeout_secs=60, deadline=70)
    if result.exit_code != 0 or result.signal or result.cancelled or result.truncated or result.timed_out:
        raise RuntimeError("build report unavailable")
    if json.loads(result.stdout) != {"job": "demo-build", "tests_passed": 3, "tests_failed": 0}:
        raise RuntimeError("unexpected build report")
    print("demo-build: 3 tests passed")
