from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_wiki.tasks import (
    create_task,
    list_tasks,
    next_task,
    readiness_report,
    set_task_status,
    task_metrics,
    validate_task_queue,
)


TASK_TEMPLATE = """# Task: {title}

Status: {status}
Role owner: {owner}
Created: 2026-06-11

## Objective

{objective}

## Context Files

- AGENTS.md

## Ownership

- Owned files: agents/tasks/{slug}.md
- Do not edit: raw/

## Allowed Tooling

- LLM Wiki CLI only.

## Acceptance Checklist

- Scope is respected.

## Verification

Command:

```powershell
python tools/llm_wiki.py lint --strict
```

Expected result:

- exits 0.

## Progress

- Verification evidence: pending until verified.
"""


class TaskQueueTests(unittest.TestCase):
    def write_task(
        self,
        root: Path,
        slug: str,
        title: str,
        status: str,
        owner: str = "Conductor",
        objective: str = "Do one atomic thing.",
    ) -> Path:
        path = root / "agents" / "tasks" / f"2026-06-11-{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            TASK_TEMPLATE.format(
                title=title,
                status=status,
                owner=owner,
                objective=objective,
                slug=slug,
            ),
            encoding="utf-8",
        )
        return path

    def test_list_tasks_reads_top_level_task_files_and_ignores_support_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "Alpha", "ready")
            self.write_task(root, "beta", "Beta", "done")
            support = root / "agents" / "tasks" / "progress" / "2026-06-11-alpha.md"
            support.parent.mkdir(parents=True, exist_ok=True)
            support.write_text("# Progress only", encoding="utf-8")

            tasks = list_tasks(root)

            self.assertEqual([task.title for task in tasks], ["Alpha", "Beta"])
            self.assertEqual([task.status for task in tasks], ["ready", "done"])

    def test_list_tasks_filters_by_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "Alpha", "ready")
            self.write_task(root, "beta", "Beta", "planned")

            tasks = list_tasks(root, status="ready")

            self.assertEqual([task.title for task in tasks], ["Alpha"])

    def test_next_task_prefers_ready_then_planned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "Alpha", "planned")
            self.write_task(root, "beta", "Beta", "ready")

            task = next_task(root)

            self.assertIsNotNone(task)
            assert task is not None
            self.assertEqual(task.title, "Beta")

    def test_next_task_falls_back_to_planned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "Alpha", "planned")

            task = next_task(root)

            self.assertIsNotNone(task)
            assert task is not None
            self.assertEqual(task.status, "planned")

    def test_set_task_status_updates_only_status_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_task(root, "alpha", "Alpha", "ready")
            before = path.read_text(encoding="utf-8")

            updated = set_task_status(root, "agents/tasks/2026-06-11-alpha.md", "in_progress")
            after = path.read_text(encoding="utf-8")

            self.assertEqual(updated.status, "in_progress")
            self.assertIn("Status: in_progress", after)
            self.assertEqual(after.replace("Status: in_progress", "Status: ready"), before)

    def test_set_task_status_rejects_invalid_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "Alpha", "ready")

            with self.assertRaises(ValueError):
                set_task_status(root, "agents/tasks/2026-06-11-alpha.md", "waiting")

    def test_validate_task_queue_returns_harness_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "Alpha", "waiting")

            issues = validate_task_queue(root)

            self.assertTrue(any("Invalid task status: waiting" in issue.message for issue in issues))

    def test_create_task_creates_task_progress_and_checkpoint_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = create_task(
                root,
                title="Write Product Brief",
                objective="Capture the approved product goal.",
                role_owner="Product Strategist",
                created="2026-06-11",
            )

            self.assertEqual(result.task.title, "Write Product Brief")
            self.assertEqual(result.task.status, "planned")
            self.assertTrue((root / result.task.path).exists())
            self.assertTrue((root / result.progress_path).exists())
            self.assertTrue((root / result.checkpoint_path).exists())
            self.assertIn("Product Strategist", (root / result.task.path).read_text(encoding="utf-8"))

    def test_create_task_uses_unique_slug_when_file_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            first = create_task(root, "Write Product Brief", "First.", created="2026-06-11")
            second = create_task(root, "Write Product Brief", "Second.", created="2026-06-11")

            self.assertEqual(first.task.path, "agents/tasks/2026-06-11-write-product-brief.md")
            self.assertEqual(second.task.path, "agents/tasks/2026-06-11-write-product-brief-2.md")

    def test_task_metrics_counts_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_task(root, "alpha", "Alpha", "planned")
            self.write_task(root, "beta", "Beta", "ready")
            self.write_task(root, "gamma", "Gamma", "done")

            metrics = task_metrics(root)

            self.assertEqual(metrics["total"], 3)
            self.assertEqual(metrics["by_status"]["planned"], 1)
            self.assertEqual(metrics["by_status"]["ready"], 1)
            self.assertEqual(metrics["by_status"]["done"], 1)
            self.assertEqual(metrics["open"], 2)

    def test_readiness_report_marks_draft_product_and_design_as_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PRODUCT.md").write_text("Status: draft-required-before-implementation\n", encoding="utf-8")
            (root / "DESIGN.md").write_text("Status: draft-required-before-implementation\n", encoding="utf-8")

            report = readiness_report(root)

            self.assertFalse(report["product_design_ready"])
            self.assertIn("PRODUCT.md", report["pending_decisions"])
            self.assertIn("DESIGN.md", report["pending_decisions"])


if __name__ == "__main__":
    unittest.main()
