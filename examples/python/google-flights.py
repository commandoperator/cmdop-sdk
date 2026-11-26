"""Search Bali to Bangkok through Fli on the selected CMDOP machine."""
import json
import os
from pathlib import Path

import cmdop

if any(os.environ.get(key) != "1" for key in ("EXAMPLES_EXEC", "EXAMPLES_NETWORK")):
    raise SystemExit("Set EXAMPLES_EXEC=1 and EXAMPLES_NETWORK=1")
date = os.environ["FLIGHT_DATE"]
helper = Path(__file__).with_name("local_mcp") / "search_flights.py"
argv = [os.environ["FLI_UVX"], "--offline", "--from", "flights[mcp]==0.11.1", "python", "-", date]
with cmdop.connect() as client:
    result = client.machine(os.environ["CMDOP_MACHINE"]).exec_run(
        argv=argv, stdin=helper.read_text(), timeout_secs=40, deadline=45)
    if result.exit_code != 0 or result.signal or result.cancelled or result.truncated or result.timed_out:
        raise RuntimeError("Flight search failed on the target machine")
    report = json.loads(result.stdout)
    if report.get("date") != date or not isinstance(report.get("flights"), list):
        raise RuntimeError("Unexpected flight report")
    print(json.dumps(report, indent=2))
