"""Read the reference application's report through its registered CMDOP machine."""
import json
import os

import cmdop


def main():
    required = ("CMDOP_URL", "CMDOP_TOKEN", "CMDOP_MACHINE")
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing:
        raise SystemExit("Set the following caller environment variables: " + ", ".join(missing))

    try:
        with cmdop.connect(url=os.environ["CMDOP_URL"], token=os.environ["CMDOP_TOKEN"]) as client:
            machine = client.machine(os.environ["CMDOP_MACHINE"].strip())
            result = machine.fs.read(path="/opt/report/build.json", deadline=15)
    except cmdop.CmdopError as error:
        raise SystemExit(f"CMDOP could not read the report ({error.code}): {error.message}") from None
    except cmdop.CarrierError:
        raise SystemExit("Could not complete the SDK request. Check CMDOP_URL and connectivity.") from None
    if result.truncated or result.encoding != "utf8":
        raise SystemExit("Expected a complete UTF-8 build report")
    try:
        report = json.loads(result.data)
    except json.JSONDecodeError:
        raise SystemExit("The selected machine returned invalid report JSON.") from None
    expected = {"job": "demo-build", "tests_passed": 3, "tests_failed": 0}
    if report != expected or any(type(report[key]) is not int for key in ("tests_passed", "tests_failed")):
        raise SystemExit("Unexpected build report from the selected machine")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
