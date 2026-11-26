"""Run a bounded POSIX fixture on an explicit machine. Requires EXAMPLES_EXEC=1."""

import os
import cmdop


def successful(result):
    if result.exit_code != 0 or result.signal is not None or result.timed_out or result.cancelled or result.truncated:
        raise RuntimeError("command_not_successful")


def main():
    if os.environ.get("EXAMPLES_EXEC") != "1":
        raise SystemExit("opt_in_required: EXAMPLES_EXEC=1")
    target = os.environ.get("CMDOP_MACHINE", "").strip()
    if not target:
        raise SystemExit("explicit_machine_id_required")
    with cmdop.connect() as client:
        rows = [row for row in client.machines_list() if row.id == target and row.state == "online"]
        if len(rows) != 1 or "exec_run" not in rows[0].tools or rows[0].os not in ("macos", "linux"):
            raise RuntimeError("target_unavailable_or_unsupported")
        machine = client.machine(target)
        result = machine.exec_run(argv=["uname", "-s"], timeout_secs=10, deadline=15)
        successful(result)
        if not result.stdout.strip():
            raise RuntimeError("missing_system_name")
        run = machine.stream("for i in 1 2 3; do echo line $i; done", timeout_secs=10, deadline=15)
        chunks = []
        for piece in run:
            if piece.stream == "stdout":
                chunks.append(piece.data)
        successful(run.result)
        if "".join(chunks).replace("\r\n", "\n") != "line 1\nline 2\nline 3\n":
            raise RuntimeError("unexpected_stream_output")
        print("command result and streamed fixture verified")


if __name__ == "__main__":
    main()
