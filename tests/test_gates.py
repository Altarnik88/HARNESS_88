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
from llm_wiki.gates import gates_status


APPROVED_GATES = """# Site Delivery Gates

Status: approved

frontend_preview_approval: approved
backend_data_readiness: complete
total_audit: complete
remediation: complete
final_user_approval: approved
publish_operate_handoff: complete
"""


class SiteDeliveryGateTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_missing_gates_file_blocks_delivery_and_publish(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status = gates_status(Path(tmp))

            self.assertFalse(status["exists"])
            self.assertFalse(status["delivery_gates_ready"])
            self.assertFalse(status["publish_ready"])
            self.assertEqual(status["path"], "SITE_GATES.md")
            self.assertIn("SITE_GATES.md", [blocker["path"] for blocker in status["blockers"]])

    def test_draft_pending_template_reports_pending_gate_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_GATES.md").write_text(
                """# Site Delivery Gates

Status: draft

frontend_preview_approval: pending
backend_data_readiness: pending
total_audit: pending
remediation: pending
final_user_approval: pending
publish_operate_handoff: pending
""",
                encoding="utf-8",
            )

            status = gates_status(root)

            self.assertTrue(status["exists"])
            self.assertEqual(status["status"], "draft")
            self.assertEqual(status["missing_fields"], [])
            self.assertFalse(status["delivery_gates_ready"])
            self.assertFalse(status["publish_ready"])
            self.assertEqual(
                status["pending_delivery_gates"],
                [
                    "frontend_preview_approval",
                    "backend_data_readiness",
                    "total_audit",
                    "remediation",
                    "final_user_approval",
                    "publish_operate_handoff",
                ],
            )

    def test_approved_complete_gates_are_delivery_and_publish_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_GATES.md").write_text(APPROVED_GATES, encoding="utf-8")

            status = gates_status(root)

            self.assertTrue(status["delivery_gates_ready"])
            self.assertTrue(status["publish_ready"])
            self.assertEqual(status["pending_delivery_gates"], [])
            self.assertEqual(status["publish_blockers"], [])

    def test_backend_data_can_be_marked_not_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_GATES.md").write_text(
                APPROVED_GATES.replace("backend_data_readiness: complete", "backend_data_readiness: not-required"),
                encoding="utf-8",
            )

            status = gates_status(root)

            self.assertTrue(status["delivery_gates_ready"])
            self.assertTrue(status["publish_ready"])
            self.assertEqual(status["fields"]["backend_data_readiness"], "not-required")

    def test_remediation_can_accept_residual_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_GATES.md").write_text(
                APPROVED_GATES.replace("remediation: complete", "remediation: residual-risk-accepted"),
                encoding="utf-8",
            )

            status = gates_status(root)

            self.assertTrue(status["delivery_gates_ready"])
            self.assertTrue(status["publish_ready"])
            self.assertEqual(status["fields"]["remediation"], "residual-risk-accepted")

    def test_site_gates_cli_json_reports_machine_readable_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_GATES.md").write_text(APPROVED_GATES, encoding="utf-8")

            code, output = self.run_cli("--root", str(root), "site", "gates", "--json")

            self.assertEqual(code, 0, output)
            payload = json.loads(output)
            self.assertTrue(payload["delivery_gates_ready"])
            self.assertTrue(payload["publish_ready"])
            self.assertEqual(payload["fields"]["frontend_preview_approval"], "approved")


if __name__ == "__main__":
    unittest.main()
