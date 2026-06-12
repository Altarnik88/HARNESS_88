from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_wiki.harness import validate_harness


REQUIRED_HARNESS_FILES = [
    "START_HERE.md",
    "SITE_GATES.md",
    "SITE_INTAKE.md",
    "SITE_REFERENCES.md",
    "STACK.md",
    "PRODUCT.md",
    "DESIGN.md",
    "agents/harness/README.md",
    "agents/harness/site-gates-template.md",
    "agents/harness/site-intake-template.md",
    "agents/harness/site-references-template.md",
    "agents/harness/stack-options.md",
    "agents/harness/prd-template.md",
    "agents/harness/spec-template.md",
    "agents/harness/task-template.md",
    "agents/harness/progress-template.md",
    "agents/harness/checkpoint-template.md",
    "agents/harness/acceptance-checklists.md",
    "agents/harness/metrics.md",
    "agents/protocols/design-resources.md",
    "agents/protocols/tooling-onboarding.md",
    "agents/resources/tooling-sources.json",
    "agents/tasks/README.md",
    "agents/tasks/_template.md",
]


VALID_TASK = """# Task: Validate Harness

Status: verified
Role owner: Knowledge Steward
Created: 2026-06-11

## Objective

Validate one atomic task.

## Context Files

- AGENTS.md

## Ownership

- Owned files: agents/tasks/example.md
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

- Verification evidence: `python tools/llm_wiki.py lint --strict` exited 0.
"""

SECOND_VALID_TASK = VALID_TASK.replace("# Task: Validate Harness", "# Task: Validate Harness Two").replace(
    "Owned files: agents/tasks/example.md",
    "Owned files: agents/tasks/example.md",
)


class HarnessValidationTests(unittest.TestCase):
    def write_minimal_harness(self, root: Path) -> None:
        for rel in REQUIRED_HARNESS_FILES:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {path.stem}\n", encoding="utf-8")
        self.write_task_bundle(root, "2026-06-11-valid-task", VALID_TASK)

    def write_task_bundle(self, root: Path, stem: str, task_text: str) -> None:
        task_rel = Path("agents") / "tasks" / f"{stem}.md"
        progress_rel = Path("agents") / "tasks" / "progress" / f"{stem}.md"
        checkpoint_rel = Path("agents") / "tasks" / "checkpoints" / f"{stem}.md"
        (root / task_rel).parent.mkdir(parents=True, exist_ok=True)
        (root / task_rel).write_text(task_text, encoding="utf-8")
        (root / progress_rel).parent.mkdir(parents=True, exist_ok=True)
        (root / progress_rel).write_text(f"# Progress\n\nLinked task: `{task_rel.as_posix()}`\n", encoding="utf-8")
        (root / checkpoint_rel).parent.mkdir(parents=True, exist_ok=True)
        (root / checkpoint_rel).write_text(f"# Checkpoint\n\nLinked task: `{task_rel.as_posix()}`\n", encoding="utf-8")

    def messages(self, root: Path) -> list[str]:
        return [issue.message for issue in validate_harness(root)]

    def test_missing_required_root_brief_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_harness(root)
            (root / "PRODUCT.md").unlink()

            messages = self.messages(root)

            self.assertIn("Missing harness file: PRODUCT.md", messages)

    def test_missing_tooling_source_registry_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_harness(root)
            (root / "agents" / "resources" / "tooling-sources.json").unlink()

            messages = self.messages(root)

            self.assertIn("Missing harness file: agents/resources/tooling-sources.json", messages)

    def test_missing_design_resources_protocol_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_harness(root)
            (root / "agents" / "protocols" / "design-resources.md").unlink()

            messages = self.messages(root)

            self.assertIn("Missing harness file: agents/protocols/design-resources.md", messages)

    def test_missing_tooling_onboarding_protocol_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_harness(root)
            (root / "agents" / "protocols" / "tooling-onboarding.md").unlink()

            messages = self.messages(root)

            self.assertIn("Missing harness file: agents/protocols/tooling-onboarding.md", messages)

    def test_invalid_task_status_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_harness(root)
            task = root / "agents" / "tasks" / "2026-06-11-valid-task.md"
            task.write_text(VALID_TASK.replace("Status: verified", "Status: waiting"), encoding="utf-8")

            messages = self.messages(root)

            self.assertTrue(any("Invalid task status: waiting" in message for message in messages))

    def test_verified_task_without_verification_evidence_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_harness(root)
            task = root / "agents" / "tasks" / "2026-06-11-valid-task.md"
            task.write_text(VALID_TASK.replace("Verification evidence:", "No evidence:"), encoding="utf-8")

            messages = self.messages(root)

            self.assertTrue(any("Verified task lacks verification evidence" in message for message in messages))

    def test_progress_and_checkpoint_support_files_are_not_treated_as_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_harness(root)
            progress = root / "agents" / "tasks" / "progress" / "2026-06-11-note.md"
            checkpoint = root / "agents" / "tasks" / "checkpoints" / "2026-06-11-note.md"
            progress.parent.mkdir(parents=True, exist_ok=True)
            checkpoint.parent.mkdir(parents=True, exist_ok=True)
            progress.write_text("support file without task sections", encoding="utf-8")
            checkpoint.write_text("support file without task sections", encoding="utf-8")

            messages = self.messages(root)

            self.assertEqual(messages, [])

    def test_missing_linked_progress_file_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_harness(root)
            (root / "agents" / "tasks" / "progress" / "2026-06-11-valid-task.md").unlink()

            messages = self.messages(root)

            self.assertTrue(any("Missing linked progress file" in message for message in messages))

    def test_open_task_owned_file_conflict_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in REQUIRED_HARNESS_FILES:
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"# {path.stem}\n", encoding="utf-8")
            self.write_task_bundle(root, "2026-06-11-valid-task", VALID_TASK.replace("Status: verified", "Status: ready"))
            self.write_task_bundle(root, "2026-06-11-second-task", SECOND_VALID_TASK.replace("Status: verified", "Status: ready"))

            messages = self.messages(root)

            self.assertTrue(any("Owned file conflict" in message for message in messages))

    def test_current_project_harness_is_valid(self) -> None:
        messages = self.messages(ROOT)

        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()
