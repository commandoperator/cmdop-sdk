"""Offline catalog/runner policy checks; no tools, registries, machines or models contacted."""

import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from catalog import CatalogError, load, public_index, select
import runner

ROOT = Path(__file__).resolve().parent


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.data = load(ROOT)

    def test_existing_pairs_resolve_and_only_reads_are_default(self):
        self.assertIn("local-mcp", {row["id"] for row in self.data["examples"]})
        rows = select(self.data, None, {"EXAMPLES_EXEC": "1", "AGENT_PROMPT": "1"})
        self.assertEqual([row["id"] for row in rows], ["hello", "fleet", "files", "showtime", "agents"])
        self.assertTrue(all(row["effects"] == ["read"] for row in rows))

    def test_generated_public_index_matches_catalog_and_includes_named_paths(self):
        expected = public_index(self.data)
        export_dir = ROOT.parent / "github/examples"
        index = (export_dir if export_dir.is_dir() else ROOT) / "README.md"
        self.assertEqual(index.read_text(), expected)
        self.assertIn("[codex.py](python/agents/codex.py)", expected)
        self.assertIn("[claude-code.ts](typescript/agents/claude-code.ts)", expected)

    def test_only_does_not_bypass_execution_or_prompt_opt_in(self):
        for name in ("command", "local-mcp", "prompt-codex", "prompt-claude-code"):
            with self.assertRaisesRegex(CatalogError, "opt_in_required"):
                select(self.data, name, {"CMDOP_MACHINE": "fixture"})
        with self.assertRaisesRegex(CatalogError, "opt_in_required"):
            select(self.data, "prompt-codex", {"EXAMPLES_EXEC": "1", "CMDOP_MACHINE": "fixture"})

    def test_effect_opt_in_does_not_replace_explicit_target(self):
        with self.assertRaisesRegex(CatalogError, "explicit_machine"):
            select(self.data, "command", {"EXAMPLES_EXEC": "1"})
        self.assertEqual(select(self.data, "command", {"EXAMPLES_EXEC": "1", "CMDOP_MACHINE": "fixture"})[0]["id"], "command")

    def test_unknown_empty_and_duplicate_requests_fail(self):
        for name in ("unknown", " , ", "hello,", "hello,hello", "../command"):
            with self.assertRaises(CatalogError):
                select(self.data, name, {})
        with self.assertRaisesRegex(CatalogError, "no_examples"):
            select({"examples": []}, None, {})

    def invalid_inventory(self, mutate):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = copy.deepcopy(self.data)
            for row in data["examples"]:
                for lang in ("python", "typescript"):
                    path = root / row[lang]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()
            mutate(root, data)
            (root / "catalog.json").write_text(json.dumps(data))
            with self.assertRaises(CatalogError):
                load(root)

    def test_missing_half_duplicate_and_unknown_effect_are_rejected(self):
        self.invalid_inventory(lambda r, d: (r / d["examples"][0]["python"]).unlink())
        self.invalid_inventory(lambda r, d: d["examples"].append(d["examples"][0]))
        self.invalid_inventory(lambda r, d: d["examples"][0].update(effects=["magic"]))
        self.invalid_inventory(lambda r, d: d["examples"][-1].update(default=True))

    def test_symlink_escape_is_rejected(self):
        def escape(root, data):
            file = root / data["examples"][0]["python"]
            file.unlink()
            file.symlink_to(Path(__file__).resolve())
        self.invalid_inventory(escape)

    def test_cli_rejects_disallowed_selection_before_execute(self):
        with patch.dict(os.environ, {"ONLY": "command"}, clear=True), patch("sys.argv", ["runner.py"]), \
             patch.object(runner, "execute") as execute, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(runner.main(), 1)
            execute.assert_not_called()

    def simulate_runner(self, name, code, stderr=b""):
        row = next(row for row in self.data["examples"] if row["id"] == name)
        commands = []
        def run(args, **kwargs):
            commands.append(args)
            if args[0] == "npm" or "tsc" in args[1]:
                return SimpleNamespace(returncode=0)
            kwargs["stderr"].write(stderr)
            if code == 3:
                kwargs["stdout"].write(json.dumps({"agent": row["agentId"], "state": "running", "task": 7}).encode())
            if code == -1:
                raise subprocess.TimeoutExpired(args, 120)
            return SimpleNamespace(returncode=code)
        output = io.StringIO()
        with patch.dict(os.environ, {"CMDOP_URL": "https://example.test", "CMDOP_TOKEN": "cmdop_test"}, clear=True), \
             patch.object(runner.shutil, "which", return_value="fixture"), \
             patch.object(runner.subprocess, "check_output", return_value="20"), \
             patch.object(runner.subprocess, "run", side_effect=run), contextlib.redirect_stdout(output):
            result = runner.execute(ROOT, [row], "3.6.0")
        return result, output.getvalue(), commands

    def test_pending_agent_retains_handle_and_prevents_second_prompt(self):
        result, output, commands = self.simulate_runner("prompt-codex", 3)
        self.assertEqual(result, 1)
        self.assertIn("RUNNING typescript prompt-codex task=7", output)
        self.assertIn("SKIP python prompt-codex counterpart_incomplete", output)
        self.assertFalse(any(args[0] == "uv" for args in commands))

    def test_failed_agent_prints_only_known_local_hints(self):
        for reason in ("requested_agent_busy", "private-detail", ["private-detail"]):
            diagnostic = json.dumps({"state": "failed", "reason": reason, "log": "private-detail"})
            result, output, commands = self.simulate_runner("prompt-codex", 1, diagnostic.encode())
            self.assertEqual(result, 1)
            self.assertEqual("Wait for the named agent" in output, reason == "requested_agent_busy")
            self.assertNotIn("private-detail", output)
            self.assertFalse(any(args[0] == "uv" for args in commands))

    def test_launcher_warnings_do_not_hide_final_agent_diagnostic(self):
        warning = b"private-warning " * 300 + b"\n"
        diagnostic = b'{"state":"failed","reason":"CarrierError","log":"private-response"}\n'
        result, output, commands = self.simulate_runner("prompt-codex", 1, warning + diagnostic)
        self.assertEqual(result, 1)
        self.assertIn("CarrierError: Check connectivity", output)
        self.assertNotIn("private", output)
        self.assertFalse(any(args[0] == "uv" for args in commands))

    def test_timeout_is_unknown_and_not_reissued_in_other_language(self):
        result, output, commands = self.simulate_runner("command", -1)
        self.assertEqual(result, 1)
        self.assertIn("UNKNOWN typescript command", output)
        self.assertFalse(any(args[0] == "uv" for args in commands))

    def test_smoke_is_never_labeled_workflow_pass(self):
        result, output, _ = self.simulate_runner("hello", 0)
        self.assertEqual(result, 0)
        self.assertIn("SMOKE typescript hello", output)
        self.assertNotIn("PASS ", output)


if __name__ == "__main__":
    unittest.main()
