from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_wiki.cli import main


class CliContractTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_task_readiness_json_preserves_top_level_keys(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "task", "readiness", "--json")

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        for key in [
            "environment_ready",
            "core_development_ready",
            "site_implementation_ready",
            "pending_decisions",
            "pending_delivery_gates",
            "task_metrics",
            "briefs",
            "intake",
            "references",
            "delivery_gates",
            "blockers",
            "publish_blockers",
            "files_to_edit",
            "next_command",
            "suggested_tasks",
        ]:
            self.assertIn(key, payload)

    def test_site_doctor_json_preserves_top_level_sections(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "site", "doctor", "--json", "--skip-self-test")

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        for key in ["readiness", "stack", "tooling", "security", "generated_project_self_test", "status"]:
            self.assertIn(key, payload)

    def test_tools_audit_json_preserves_top_level_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, output = self.run_cli("--root", str(ROOT), "tools", "audit", "--json", "--codex-home", tmp)

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        for key in [
            "status",
            "root",
            "codex_home",
            "source_registry",
            "setup_policy",
            "summary",
            "items",
            "next_actions",
        ]:
            self.assertIn(key, payload)

    def test_cli_support_helpers_are_extractable(self) -> None:
        from llm_wiki.cli_support import site_lock_state, summary_count, yes_no

        self.assertEqual(yes_no(True), "yes")
        self.assertEqual(yes_no(False), "no")
        self.assertEqual(site_lock_state({"site_implementation_ready": True}), "unlocked")
        self.assertEqual(site_lock_state({"site_implementation_ready": False}), "locked")
        self.assertEqual(summary_count({"bucket": {"count": 3}}, "bucket"), 3)

    def test_cli_command_handlers_are_extractable(self) -> None:
        from llm_wiki.cli_security import cmd_security
        from llm_wiki.cli_site import cmd_site
        from llm_wiki.cli_tasks import cmd_task
        from llm_wiki.cli_tools import cmd_tools

        self.assertTrue(callable(cmd_security))
        self.assertTrue(callable(cmd_site))
        self.assertTrue(callable(cmd_task))
        self.assertTrue(callable(cmd_tools))


if __name__ == "__main__":
    unittest.main()
