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
from llm_wiki.intake import intake_status
from llm_wiki.tasks import readiness_report


APPROVED_INTAKE = """# Site Intake

Status: approved

goal: Sell premium consultations.
audience: Small business owners.
country: Poland
language: Polish
site_type: ecommerce
catalog_mode: product-catalog
payment_request_mode: mixed
design_style: editorial, high-trust
reference_mode: user-provided
references_status: approved
content_sources: existing copy deck and photos
stack_expectations: frontend first, selected later
deploy_expectations: VPS after approval
backend: required
data: product database
auth: admin only
admin: product manager console
integrations: payment provider and CRM
product_catalog_document: needed
"""


class IntakeStatusTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_missing_intake_file_blocks_intake_and_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status = intake_status(Path(tmp))

            self.assertFalse(status["exists"])
            self.assertFalse(status["intake_ready"])
            self.assertFalse(status["references_ready"])
            self.assertIn("SITE_INTAKE.md is missing.", status["message"])
            self.assertIn("SITE_INTAKE.md", [blocker["path"] for blocker in status["blockers"]])

    def test_draft_template_reports_required_missing_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_INTAKE.md").write_text(
                "# Site Intake\n\nStatus: draft\n\ngoal: unknown\nreferences_status: pending\n",
                encoding="utf-8",
            )

            status = intake_status(root)

            self.assertTrue(status["exists"])
            self.assertEqual(status["status"], "draft")
            self.assertFalse(status["intake_ready"])
            self.assertIn("audience", status["missing_fields"])
            self.assertIn("site_type", status["missing_fields"])
            self.assertFalse(status["references_ready"])

    def test_approved_complete_intake_is_ready_and_records_catalog_need(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_INTAKE.md").write_text(APPROVED_INTAKE, encoding="utf-8")

            status = intake_status(root)

            self.assertTrue(status["intake_ready"])
            self.assertTrue(status["references_ready"])
            self.assertTrue(status["product_catalog_document_required"])
            self.assertEqual(status["fields"]["product_catalog_document"], "needed")

    def test_references_pending_blocks_site_readiness_after_other_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PRODUCT.md").write_text("Status: approved\n", encoding="utf-8")
            (root / "DESIGN.md").write_text("Status: approved\n", encoding="utf-8")
            (root / "STACK.md").write_text("status: selected\nselected_profile: next-static\n", encoding="utf-8")
            (root / "SITE_INTAKE.md").write_text(
                APPROVED_INTAKE.replace("references_status: approved", "references_status: pending"),
                encoding="utf-8",
            )

            report = readiness_report(root)

            self.assertTrue(report["intake_ready"])
            self.assertFalse(report["references_ready"])
            self.assertFalse(report["site_implementation_ready"])
            self.assertIn("references", report["pending_decisions"])

    def test_site_intake_cli_json_reports_machine_readable_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_INTAKE.md").write_text(APPROVED_INTAKE, encoding="utf-8")

            code, output = self.run_cli("--root", str(root), "site", "intake", "--json")

            self.assertEqual(code, 0, output)
            payload = json.loads(output)
            self.assertTrue(payload["intake_ready"])
            self.assertTrue(payload["references_ready"])
            self.assertEqual(payload["fields"]["site_type"], "ecommerce")


if __name__ == "__main__":
    unittest.main()
