from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_wiki.capabilities import capability_audit
from llm_wiki.cli import main


class CapabilityAuditTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_capability_audit_detects_local_commands_and_codex_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp) / ".codex"
            (codex_home / "skills" / "playwright").mkdir(parents=True)
            (codex_home / "skills" / "playwright" / "SKILL.md").write_text("---\nname: playwright\n---\n")
            (codex_home / "plugins" / "cache" / "openai-curated" / "github" / "skills" / "github").mkdir(parents=True)
            (codex_home / "plugins" / "cache" / "openai-curated" / "github" / "skills" / "github" / "SKILL.md").write_text("---\nname: github\n---\n")

            def fake_which(name: str) -> str | None:
                return f"C:/bin/{name}.exe" if name in {"python", "git"} else None

            with patch("llm_wiki.capabilities.shutil.which", side_effect=fake_which):
                report = capability_audit(ROOT, codex_home=codex_home)

            items = {item["id"]: item for item in report["items"]}
            self.assertEqual(items["local.python"]["status"], "available")
            self.assertEqual(items["local.git"]["status"], "available")
            self.assertEqual(items["skill.playwright"]["status"], "available")
            self.assertEqual(items["plugin.github"]["status"], "available")
            self.assertEqual(items["plugin.browser"]["status"], "missing")
            self.assertEqual(report["status"], "needs-setup")
            self.assertTrue(report["next_actions"])
            self.assertIn("permission", report["next_actions"][0]["prompt"].casefold())

    def test_capability_catalog_covers_tooling_matrix_families(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = capability_audit(ROOT, codex_home=Path(tmp))

        ids = {item["id"] for item in report["items"]}
        for capability_id in [
            "mcp.filesystem",
            "mcp.sqlite",
            "mcp.node-repl",
            "skill.imagegen",
            "plugin.sentry",
            "plugin.remotion",
            "plugin.canva",
            "plugin.creative-production",
            "plugin.data-analytics",
            "plugin.documents",
            "plugin.spreadsheets",
        ]:
            self.assertIn(capability_id, ids)

    def test_tools_audit_json_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, output = self.run_cli("--root", str(ROOT), "tools", "audit", "--json", "--codex-home", tmp)

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        self.assertIn(payload["status"], {"ready", "needs-setup"})
        self.assertIn("summary", payload)
        self.assertIn("items", payload)
        self.assertIn("next_actions", payload)

    def test_site_doctor_includes_tooling_report(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "site", "doctor", "--json", "--skip-self-test")

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        self.assertIn("tooling", payload)
        self.assertIn("next_actions", payload["tooling"])

    def test_site_doctor_human_output_includes_tooling_summary(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "site", "doctor", "--skip-self-test")

        self.assertEqual(code, 0, output)
        self.assertIn("Tooling:", output)


if __name__ == "__main__":
    unittest.main()
