"""Exercise the packaged enrollment helper with closed stdin and a fake CMDOP CLI."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    cli = root / "cmdop"
    cli.write_text("""#!/bin/sh
printf '%s\\n' "$*" >> "$COMMANDS"
case "$*" in
  'config show') printf '%s' "$CONFIG"; printf '%s' "$DIAGNOSTIC" >&2; exit "$CODE" ;;
  *) exit 50 ;;
esac
""")
    cli.chmod(0o755)
    commands = root / "commands"
    cases = [
        (0, '{"server":"wss://example.invalid/ws/machine"}', "", [], 0, "Using the saved machine link"),
        (0, '{"server":"wss://example.invalid/ws/machine"}', "", ["--sign-in"], 1, "interactive terminal"),
        (1, "", "cmdop needs its terms of use accepted", [], 1, "interactive terminal"),
        (1, json.dumps({"_invalid": {"field": "server"}}), "", [], 1, "field to fix"),
        (1, "", "permission denied", [], 1, "Could not read"),
        (0, "invalid json", "", [], 1, "Could not read"),
    ]
    for code, config, diagnostic, args, expected, message in cases:
        commands.write_text("")
        env = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}", COMMANDS=str(commands),
                   CODE=str(code), CONFIG=config, DIAGNOSTIC=diagnostic)
        result = subprocess.run(["python", "/opt/report/connect.py", *args], env=env,
                                stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
        assert result.returncode == expected and message in result.stdout + result.stderr, result
        assert commands.read_text().splitlines() == ["config show"]
