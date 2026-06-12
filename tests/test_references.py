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
from llm_wiki.references import reference_status
from llm_wiki.tasks import readiness_report


APPROVED_INTAKE = """# Site Intake

Status: approved

goal: Sell premium consultations.
audience: Small business owners.
country: Poland
language: Polish
site_type: landing
catalog_mode: none
payment_request_mode: no-commerce
design_style: editorial, high-trust
reference_mode: user-provided
references_status: approved
content_sources: existing copy deck and photos
stack_expectations: frontend first, selected later
deploy_expectations: VPS after approval
backend: not-required
data: not-required
auth: not-required
admin: not-required
integrations: analytics
product_catalog_document: not-required
"""


APPROVED_REFERENCES = """# Site References

Status: approved

reference_analysis_status: complete
crawl_policy: bounded-crawl
page_inventory: complete
screenshot_manifest: raw/assets/references/manifest.json
figma_policy: create-file
figma_reference: https://figma.com/design/ABC123/Reference-Analysis
ux_visual_analysis: complete
user_reference_approval: approved
"""


class SiteReferenceGateTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def write_complete_manifest(self, root: Path) -> None:
        assets = root / "raw" / "assets" / "references"
        assets.mkdir(parents=True)
        desktop = assets / "example-home-desktop.png"
        mobile = assets / "example-home-mobile.png"
        desktop.write_bytes(b"desktop screenshot")
        mobile.write_bytes(b"mobile screenshot")
        manifest = {
            "figma_file": "https://figma.com/design/ABC123/Reference-Analysis",
            "references": [
                {
                    "url": "https://example.com",
                    "crawl_policy": "bounded-crawl",
                    "pages": [
                        {
                            "url": "https://example.com/",
                            "desktop_screenshot": "raw/assets/references/example-home-desktop.png",
                            "mobile_screenshot": "raw/assets/references/example-home-mobile.png",
                            "figma_node": "https://figma.com/design/ABC123/Reference-Analysis?node-id=1-2",
                        }
                    ],
                    "skipped_urls": [
                        {"url": "https://example.com/login", "reason": "login/private area excluded"}
                    ],
                    "blockers": [],
                }
            ],
        }
        (assets / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def write_ready_project(self, root: Path) -> None:
        (root / "PRODUCT.md").write_text("Status: approved\n", encoding="utf-8")
        (root / "DESIGN.md").write_text("Status: approved\n", encoding="utf-8")
        (root / "STACK.md").write_text("status: selected\nselected_profile: next-static\n", encoding="utf-8")
        (root / "SITE_INTAKE.md").write_text(APPROVED_INTAKE, encoding="utf-8")

    def test_missing_references_file_blocks_reference_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status = reference_status(Path(tmp))

            self.assertFalse(status["exists"])
            self.assertFalse(status["reference_analysis_ready"])
            self.assertIn("SITE_REFERENCES.md is missing.", status["message"])
            self.assertIn("SITE_REFERENCES.md", [blocker["path"] for blocker in status["blockers"]])

    def test_draft_references_template_reports_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_REFERENCES.md").write_text(
                "# Site References\n\nStatus: draft\n\nreference_analysis_status: pending\n",
                encoding="utf-8",
            )

            status = reference_status(root)

            self.assertTrue(status["exists"])
            self.assertEqual(status["status"], "draft")
            self.assertFalse(status["reference_analysis_ready"])
            self.assertIn("crawl_policy", status["missing_fields"])
            self.assertIn("screenshot_manifest", status["missing_fields"])

    def test_approved_complete_references_are_ready_with_manifest_and_figma_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_REFERENCES.md").write_text(APPROVED_REFERENCES, encoding="utf-8")
            self.write_complete_manifest(root)

            status = reference_status(root)

            self.assertTrue(status["reference_analysis_ready"])
            self.assertEqual(status["pending_reference_gates"], [])
            self.assertEqual(status["manifest"]["captured_page_count"], 1)
            self.assertEqual(status["fields"]["figma_policy"], "create-file")

    def test_invalid_figma_reference_blocks_reference_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_REFERENCES.md").write_text(
                APPROVED_REFERENCES.replace("https://figma.com/design/ABC123/Reference-Analysis", "pending"),
                encoding="utf-8",
            )
            self.write_complete_manifest(root)

            status = reference_status(root)

            self.assertFalse(status["reference_analysis_ready"])
            self.assertIn("figma_reference", status["pending_reference_gates"])

    def test_manifest_missing_screenshot_blocks_reference_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_REFERENCES.md").write_text(APPROVED_REFERENCES, encoding="utf-8")
            self.write_complete_manifest(root)
            (root / "raw" / "assets" / "references" / "example-home-mobile.png").unlink()

            status = reference_status(root)

            self.assertFalse(status["reference_analysis_ready"])
            self.assertIn("screenshot_manifest", status["pending_reference_gates"])
            self.assertTrue(status["manifest"]["issues"])

    def test_readiness_requires_intake_approval_and_reference_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_ready_project(root)

            missing_report = readiness_report(root)

            self.assertFalse(missing_report["references_ready"])
            self.assertFalse(missing_report["site_implementation_ready"])
            self.assertIn("references", missing_report["pending_decisions"])
            self.assertIn("SITE_REFERENCES.md", [blocker["path"] for blocker in missing_report["blockers"]])

            (root / "SITE_REFERENCES.md").write_text(APPROVED_REFERENCES, encoding="utf-8")
            self.write_complete_manifest(root)

            ready_report = readiness_report(root)

            self.assertTrue(ready_report["references_ready"])
            self.assertTrue(ready_report["site_implementation_ready"])
            self.assertNotIn("references", ready_report["pending_decisions"])

    def test_site_references_cli_json_reports_machine_readable_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SITE_REFERENCES.md").write_text(APPROVED_REFERENCES, encoding="utf-8")
            self.write_complete_manifest(root)

            code, output = self.run_cli("--root", str(root), "site", "references", "--json")

            self.assertEqual(code, 0, output)
            payload = json.loads(output)
            self.assertTrue(payload["reference_analysis_ready"])
            self.assertEqual(payload["path"], "SITE_REFERENCES.md")
            self.assertEqual(payload["manifest"]["reference_count"], 1)


if __name__ == "__main__":
    unittest.main()
