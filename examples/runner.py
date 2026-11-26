"""Registry example runner: explicit setup, compiled JS, private process logs."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from catalog import CatalogError, load, public_index, select


# Agent examples emit bounded JSON diagnostics. Display only our own messages.
AGENT_HINTS = {
    "target_unavailable": "Check CMDOP_MACHINE and the machine's online status.",
    "agent_tools_unavailable": "Check that the machine offers agent_list and agent_prompt.",
    "requested_agent_unavailable": "Check the named agent's installation on the selected machine.",
    "requested_agent_busy": "Wait for the named agent to finish its current task.",
    "unsupported_tier": "Check that the installed agent supports a text-only prompt.",
}


def agent_hint(errors) -> str:
    errors.seek(0)
    try:
        report = json.loads(errors.read(4097))
    except (ValueError, RecursionError):
        return ""
    if isinstance(report, dict) and report.get("state") == "failed":
        reason = report.get("reason")
        if isinstance(reason, str) and reason in AGENT_HINTS:
            return f" {reason}: {AGENT_HINTS[reason]}"
    return ""


def execute(root: Path, chosen: list[dict], version: str, build_only: bool = False) -> int:
    for key in (() if build_only else ("CMDOP_URL", "CMDOP_TOKEN")):
        if not os.environ.get(key, "").strip():
            raise CatalogError(f"setup_required: {key}")
    for tool in (("node", "npm") if build_only else ("node", "npm", "uv")):
        if not shutil.which(tool):
            raise CatalogError(f"missing_tool: {tool}")
    major = int(subprocess.check_output(["node", "-p", "process.versions.node.split('.')[0]"], text=True).strip())
    if major < 20:
        raise CatalogError("node_20_or_later_required")
    with tempfile.TemporaryDirectory(prefix="cmdop-examples-") as temporary:
        work = Path(temporary)
        shutil.copytree(root / "typescript", work / "typescript",
                        ignore=shutil.ignore_patterns("node_modules", "build"))
        if any(row["id"] == "google-flights" for row in chosen):
            helpers = Path("python/local_mcp")
            (work / helpers).mkdir(parents=True)
            shutil.copy2(root / helpers / "search_flights.py", work / helpers)
        (work / "package.json").write_text(json.dumps({"private": True, "type": "module"}))
        config = {"compilerOptions": {"target": "ES2022", "module": "NodeNext",
                  "moduleResolution": "NodeNext", "types": ["node"], "strict": True,
                  "skipLibCheck": True, "rootDir": "typescript", "outDir": "build"},
                  "include": [row["typescript"] for row in chosen]}
        (work / "tsconfig.json").write_text(json.dumps(config))
        with tempfile.TemporaryFile() as log:
            for args in (["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund",
                          f"@cmdop/sdk@{version}", "typescript@6.0.3", "@types/node@22.20.5"],
                         ["node", "node_modules/typescript/bin/tsc", "-p", "tsconfig.json"]):
                if subprocess.run(args, cwd=work, stdout=log, stderr=log, timeout=180).returncode:
                    raise CatalogError("package_setup_or_compilation_failed")
        if build_only:
            print(f"COMPILED {len(chosen)} entries; no examples or machine calls executed")
            return 0
        failed = 0
        for row in chosen:
            stop_pair = False
            for language in ("typescript", "python"):
                if stop_pair:
                    print(f"SKIP {language} {row['id']} counterpart_incomplete", flush=True)
                    continue
                if language == "typescript":
                    source = Path(row[language]).relative_to("typescript").with_suffix(".js")
                    args = ["node", str(work / "build" / source)]
                else:
                    args = ["uv", "run", "--isolated", "--no-project", "--quiet", "--with",
                            f"cmdop=={version}", "python", str(root / row[language])]
                detail = ""
                handle = None
                with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
                    try:
                        code = subprocess.run(args, stdout=output, stderr=errors, timeout=120).returncode
                    except subprocess.TimeoutExpired:
                        code = -1  # Outcome uncertain; do not reissue remote work.
                    if code == 3 and row.get("agentId"):
                        output.seek(0)
                        try:
                            value = json.loads(output.read(16385))
                            if value.get("agent") == row["agentId"] and value.get("state") == "running" and type(value.get("task")) is int:
                                handle = value["task"]
                                detail = f" task={handle}"
                        except (ValueError, AttributeError):
                            pass
                    elif code == 1 and row.get("agentId"):
                        detail = agent_hint(errors)
                if code == 0:
                    status = "PASS" if row["assertion"] == "outcome" else "SMOKE"
                else:
                    status = "RUNNING" if handle is not None else "UNKNOWN" if code == -1 else "FAIL"
                    failed += 1
                    stop_pair = bool(set(row["effects"]) - {"read"})
                print(f"{status} {language} {row['id']}{detail}", flush=True)
        print("SMOKE is process completion only; workflow proof requires its own receipt.")
        return int(failed != 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="show validated metadata without running")
    parser.add_argument("--plan", action="store_true", help="check selection/effects without installing or connecting")
    parser.add_argument("--build-only", action="store_true", help="compile selected TS with published SDK; do not run examples")
    parser.add_argument("--sync-index", action="store_true", help="refresh the SDK workspace's generated public index")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    try:
        data = load(root)
        if args.sync_index:
            destination = root.parent / "github" / "examples" / "README.md"
            if not destination.parent.is_dir():
                raise CatalogError("sdk_source_workspace_required")
            destination.write_text(public_index(data))
            print("Generated public examples index updated")
            return 0
        if args.list:
            print(json.dumps(data, indent=2))
            return 0
        chosen = select(data, os.environ.get("ONLY"), os.environ)
        if args.plan:
            print(json.dumps([row["id"] for row in chosen]))
            return 0
        version = os.environ.get("VERSION") or data["sdkVersion"]
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            raise CatalogError("invalid_sdk_version")
        print("SELECTED " + ",".join(row["id"] for row in chosen), flush=True)
        return execute(root, chosen, version, build_only=args.build_only)
    except CatalogError as error:
        print(str(error), file=sys.stderr)
    except Exception:
        print("example_runner_failed; raw logs omitted; uncertain work is not retried", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
