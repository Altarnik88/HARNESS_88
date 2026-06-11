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
from tests.test_tasks import TASK_TEMPLATE


class TaskCliTests(unittest.TestCase):
    def write_task(self, root: Path, slug: str, status: str) -> Path:
        path = root / "agents" / "tasks" / f"2026-06-11-{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            TASK_TEMPLATE.format(
                title=slug.title(),
                status=status,
                owner="Conductor",
                objective=f"Do {slug}.",
                slug=slug,
            ),
            encoding="utf-8",
        )
        return path

    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(list(args))
        return code, stdout.getvalue()

    def test_task_list_json_outputs_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "ready")

            code, output = self.run_cli("--root", str(root), "task", "list", "--json")

            self.assertEqual(code, 0)
            rows = json.loads(output)
            self.assertEqual(rows[0]["title"], "Alpha")
            self.assertEqual(rows[0]["status"], "ready")

    def test_task_next_prints_selected_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "planned")
            self.write_task(root, "beta", "ready")

            code, output = self.run_cli("--root", str(root), "task", "next")

            self.assertEqual(code, 0)
            self.assertIn("agents/tasks/2026-06-11-beta.md", output)
            self.assertIn("ready", output)

    def test_task_set_status_updates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_task(root, "alpha", "ready")

            code, output = self.run_cli(
                "--root",
                str(root),
                "task",
                "set-status",
                "agents/tasks/2026-06-11-alpha.md",
                "in_progress",
            )

            self.assertEqual(code, 0)
            self.assertIn("in_progress", output)
            self.assertIn("Status: in_progress", path.read_text(encoding="utf-8"))

    def test_task_create_json_creates_task_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            code, output = self.run_cli(
                "--root",
                str(root),
                "task",
                "create",
                "--title",
                "Write Product Brief",
                "--objective",
                "Capture approved product decisions.",
                "--owner",
                "Product Strategist",
                "--created",
                "2026-06-11",
                "--json",
            )

            self.assertEqual(code, 0)
            payload = json.loads(output)
            self.assertEqual(payload["task"]["path"], "agents/tasks/2026-06-11-write-product-brief.md")
            self.assertTrue((root / payload["progress_path"]).exists())
            self.assertTrue((root / payload["checkpoint_path"]).exists())

    def test_task_report_json_outputs_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "planned")
            self.write_task(root, "beta", "verified")

            code, output = self.run_cli("--root", str(root), "task", "report", "--json")

            self.assertEqual(code, 0)
            payload = json.loads(output)
            self.assertEqual(payload["total"], 2)
            self.assertEqual(payload["open"], 1)

    def test_task_readiness_reports_pending_product_design(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PRODUCT.md").write_text("Status: draft\n", encoding="utf-8")
            (root / "DESIGN.md").write_text("Status: needs-review\n", encoding="utf-8")
            (root / "STACK.md").write_text("status: unselected\nselected_profile: none\n", encoding="utf-8")

            code, output = self.run_cli("--root", str(root), "task", "readiness", "--json")

            self.assertEqual(code, 0)
            payload = json.loads(output)
            self.assertFalse(payload["product_design_ready"])
            self.assertEqual(payload["pending_decisions"], ["PRODUCT.md", "DESIGN.md", "STACK.md", "SITE_INTAKE.md", "references"])
            self.assertIn("blockers", payload)
            self.assertEqual(payload["briefs"]["PRODUCT.md"]["status"], "draft")
            self.assertFalse(payload["intake_ready"])
            self.assertFalse(payload["references_ready"])

    def test_task_set_status_requires_force_for_invalid_transition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "planned")

            code, output = self.run_cli(
                "--root",
                str(root),
                "task",
                "set-status",
                "agents/tasks/2026-06-11-alpha.md",
                "done",
            )

            self.assertNotEqual(code, 0)
            self.assertIn("Invalid task status transition", output)

            code, output = self.run_cli(
                "--root",
                str(root),
                "task",
                "set-status",
                "agents/tasks/2026-06-11-alpha.md",
                "done",
                "--force",
            )

            self.assertEqual(code, 0)
            self.assertIn("done", output)


if __name__ == "__main__":
    unittest.main()
