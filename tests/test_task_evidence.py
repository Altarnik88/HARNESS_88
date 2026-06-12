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
from llm_wiki.evidence import evidence_report


TASK = """# Task: {title}

Status: {status}
Role owner: Conductor
Created: 2026-06-11

## Objective

Do one evidence-backed thing.

## Context Files

- AGENTS.md

## Ownership

Owned files:

- src/example.py

Do not edit:

- raw/

## Allowed Tooling

- LLM Wiki CLI only.

## Acceptance Checklist

- Scope is respected.

## Verification

Command:

```powershell
python tools/llm_wiki.py task validate --strict
```

Expected result:

- exits 0.

## Progress

{progress}
"""


PROGRESS = """# Progress: {title}

Linked task: `agents/tasks/{stem}.md`
Current status: {status}

## Completed Steps

- Implementation evidence recorded in checkpoint.

## Current Blocker

- None.

## Next Action

- Verify.

## Files Changed

- src/example.py

## Verification Run

{verification}

## Clean-Context Handoff Notes

- Read the checkpoint.
"""


CHECKPOINT = """# Checkpoint: {title}

Linked task: `agents/tasks/{stem}.md`

## Preflight Checks

- Worktree state checked.

## Implementation Evidence

{implementation}

## Verification Evidence

{verification}

## Review Evidence

{review}

## Wiki and Log Updates

{wiki_log}

## Residual Risk

{residual_risk}
"""


def write_bundle(
    root: Path,
    *,
    stem: str = "2026-06-11-evidence-task",
    title: str = "Evidence Task",
    status: str = "verified",
    task_progress: str = "- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0.",
    progress_verification: str = "- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0.",
    implementation: str = "- Added the evidence summary parser.",
    checkpoint_verification: str = "- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0.",
    review: str = "- Reviewed the JSON contract for raw evidence leakage.",
    wiki_log: str = "- Updated `wiki/log.md` with the durable decision.",
    residual_risk: str = "- Secret broker implementation remains deferred.",
) -> Path:
    task_rel = Path("agents") / "tasks" / f"{stem}.md"
    progress_rel = Path("agents") / "tasks" / "progress" / f"{stem}.md"
    checkpoint_rel = Path("agents") / "tasks" / "checkpoints" / f"{stem}.md"
    (root / task_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / progress_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / checkpoint_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / task_rel).write_text(
        TASK.format(title=title, status=status, progress=task_progress),
        encoding="utf-8",
    )
    (root / progress_rel).write_text(
        PROGRESS.format(
            title=title,
            stem=stem,
            status=status,
            verification=progress_verification,
        ),
        encoding="utf-8",
    )
    (root / checkpoint_rel).write_text(
        CHECKPOINT.format(
            title=title,
            stem=stem,
            implementation=implementation,
            verification=checkpoint_verification,
            review=review,
            wiki_log=wiki_log,
            residual_risk=residual_risk,
        ),
        encoding="utf-8",
    )
    return root / task_rel


class TaskEvidenceTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(list(args))
        return code, stdout.getvalue()

    def test_complete_task_bundle_reports_evidence_flags_and_summary_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_bundle(root)

            report = evidence_report(root)

            self.assertEqual(report["task_metrics"]["total"], 1)
            self.assertEqual(report["summary"]["missing_support_files"]["count"], 0)
            self.assertEqual(report["summary"]["verification_evidence"]["count"], 1)
            self.assertEqual(report["summary"]["implementation_evidence"]["paths"], ["agents/tasks/2026-06-11-evidence-task.md"])
            self.assertEqual(report["summary"]["residual_risk"]["count"], 0)
            self.assertEqual(report["summary"]["residual_risk_states"]["deferred"]["count"], 1)
            self.assertEqual(report["issues"], [])
            row = report["tasks"][0]
            self.assertTrue(row["support_files"]["progress"]["exists"])
            self.assertTrue(row["support_files"]["checkpoint"]["exists"])
            self.assertEqual(row["residual_risk_state"], "deferred")
            self.assertEqual(
                row["evidence"],
                {
                    "implementation": True,
                    "verification": True,
                    "review": True,
                    "wiki_log": True,
                    "residual_risk": False,
                },
            )

    def test_missing_progress_and_checkpoint_files_are_reported_without_raw_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = root / "agents" / "tasks" / "2026-06-11-missing-support.md"
            task.parent.mkdir(parents=True, exist_ok=True)
            task.write_text(TASK.format(title="Missing Support", status="planned", progress="- No work has started."), encoding="utf-8")

            report = evidence_report(root)

            self.assertEqual(report["summary"]["missing_support_files"]["count"], 2)
            self.assertEqual(
                report["summary"]["missing_support_files"]["paths"],
                [
                    "agents/tasks/progress/2026-06-11-missing-support.md",
                    "agents/tasks/checkpoints/2026-06-11-missing-support.md",
                ],
            )
            self.assertEqual(len(report["issues"]), 2)
            self.assertNotIn("No work has started", json.dumps(report, ensure_ascii=False))

    def test_verified_task_without_verification_evidence_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_bundle(
                root,
                status="verified",
                task_progress="- No work has started.",
                progress_verification="- No verification run yet.",
                checkpoint_verification="- No verification evidence recorded yet.",
            )

            report = evidence_report(root)

            self.assertEqual(report["summary"]["verified_without_verification"]["count"], 1)
            self.assertEqual(report["summary"]["verified_without_verification"]["paths"], ["agents/tasks/2026-06-11-evidence-task.md"])
            self.assertTrue(any("Verified task lacks verification evidence" in issue["message"] for issue in report["issues"]))

    def test_placeholder_residual_risk_does_not_count_as_residual_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_bundle(root, residual_risk="- No residual risk recorded yet.")

            report = evidence_report(root)

            self.assertEqual(report["summary"]["residual_risk"]["count"], 0)
            self.assertFalse(report["tasks"][0]["evidence"]["residual_risk"])
            self.assertEqual(report["tasks"][0]["residual_risk_state"], "none")

    def test_plain_none_residual_risk_does_not_count_as_residual_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_bundle(root, residual_risk="- None.")

            report = evidence_report(root)

            self.assertEqual(report["summary"]["residual_risk"]["count"], 0)
            self.assertEqual(report["tasks"][0]["residual_risk_state"], "none")

    def test_accepted_residual_risk_does_not_count_as_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_bundle(root, residual_risk="- Known optional frontend audit item is accepted as non-blocking for this core task.")

            report = evidence_report(root)

            self.assertEqual(report["summary"]["residual_risk"]["count"], 0)
            self.assertEqual(report["summary"]["residual_risk_states"]["accepted"]["count"], 1)
            self.assertEqual(report["tasks"][0]["residual_risk_state"], "accepted")
            self.assertFalse(report["tasks"][0]["evidence"]["residual_risk"])

    def test_unresolved_residual_risk_counts_as_residual_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_bundle(root, residual_risk="- Unresolved moderate npm audit finding remains open.")

            report = evidence_report(root)

            self.assertEqual(report["summary"]["residual_risk"]["count"], 1)
            self.assertEqual(report["summary"]["residual_risk"]["paths"], ["agents/tasks/2026-06-11-evidence-task.md"])
            self.assertEqual(report["summary"]["residual_risk_states"]["unresolved"]["count"], 1)
            self.assertEqual(report["tasks"][0]["residual_risk_state"], "unresolved")
            self.assertTrue(report["tasks"][0]["evidence"]["residual_risk"])

    def test_task_evidence_cli_json_outputs_stable_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_bundle(root)

            code, output = self.run_cli("--root", str(root), "task", "evidence", "--json")

            self.assertEqual(code, 0)
            payload = json.loads(output)
            self.assertEqual(payload["summary"]["verification_evidence"]["count"], 1)
            self.assertEqual(payload["tasks"][0]["checkpoint_path"], "agents/tasks/checkpoints/2026-06-11-evidence-task.md")
            self.assertNotIn("Added the evidence summary parser", output)


if __name__ == "__main__":
    unittest.main()
