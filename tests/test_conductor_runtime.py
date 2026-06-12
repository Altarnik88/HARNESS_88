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
from llm_wiki.harness import validate_harness


MINIMAL_TASK = """# Task: Reference Analysis

Status: ready
Role owner: {owner}
Created: 2026-06-12
Phase: reference-analysis
Delegation packet: {packet}

## Objective

Complete reference analysis through assigned role agents.

## Context Files

- AGENTS.md
- agents/TEAM.md

## Ownership

Owned files:

- SITE_REFERENCES.md

Do not edit:

- frontend/

## Allowed Tooling

- Use only tooling granted by agents/tooling-matrix.md and this task file.

## Acceptance Checklist

- Scope is respected.

## Verification

Command:

```powershell
python tools/llm_wiki.py site references --json
```

Expected result:

- exits 0.

## Progress

- No work has started.
"""


class ConductorRuntimeTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_conductor_start_json_returns_chat_bootstrap_packet(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "conductor", "start", "--json")

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        self.assertEqual(payload["mode"], "conductor")
        self.assertIn("Conductor online", payload["chat_banner"])
        self.assertIn("agents/TEAM.md", payload["read_order"])
        self.assertIn("python tools/llm_wiki.py task readiness --json", payload["required_checks"])
        self.assertIn("readiness", payload)
        self.assertIn("next_actions", payload)
        self.assertIn("create delegation packets", " ".join(payload["allowed_local_actions"]))
        self.assertIn("self-assign worker phases", " ".join(payload["forbidden_local_actions"]))

    def test_conductor_start_human_output_starts_with_online_banner(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "conductor", "start")

        self.assertEqual(code, 0, output)
        self.assertTrue(output.startswith("Conductor online"), output)
        self.assertIn("Mode: conductor", output)
        self.assertIn("Next actions:", output)

    def test_conductor_route_reference_analysis_lists_roles_and_denied_scope(self) -> None:
        code, output = self.run_cli(
            "--root",
            str(ROOT),
            "conductor",
            "route",
            "--phase",
            "reference-analysis",
            "--json",
        )

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        self.assertEqual(payload["phase"], "reference-analysis")
        self.assertTrue(payload["requires_delegation"])
        self.assertEqual(
            payload["lead_roles"],
            ["Reference Research", "UX/Product Design", "Visual Design", "Design Artifact", "QA & Accessibility"],
        )
        denied = " ".join(payload["denied_scope"])
        self.assertIn("checkout", denied)
        self.assertIn("private", denied)
        self.assertIn("form-submission", denied)
        self.assertIn("python tools/llm_wiki.py site references --json", payload["verification"])

    def test_conductor_delegate_creates_task_bundle_and_delegation_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            code, output = self.run_cli(
                "--root",
                str(root),
                "conductor",
                "delegate",
                "--phase",
                "reference-analysis",
                "--title",
                "Reference Analysis",
                "--objective",
                "Analyze approved references without building the site.",
                "--owner",
                "Reference Research",
                "--user-language",
                "Russian",
                "--owned",
                "SITE_REFERENCES.md",
                "raw/assets/references/",
                "--do-not-edit",
                "frontend/",
                "PRODUCT.md",
                "--verification",
                "python tools/llm_wiki.py site references --json",
                "--created",
                "2026-06-12",
                "--json",
            )

            self.assertEqual(code, 0, output)
            payload = json.loads(output)
            task_path = root / payload["task"]["path"]
            progress_path = root / payload["progress_path"]
            checkpoint_path = root / payload["checkpoint_path"]
            packet_path = root / payload["delegation_packet"]

            self.assertTrue(task_path.exists())
            self.assertTrue(progress_path.exists())
            self.assertTrue(checkpoint_path.exists())
            self.assertTrue(packet_path.exists())
            self.assertEqual(payload["task"]["phase"], "reference-analysis")
            self.assertEqual(payload["task"]["delegation_packet"], payload["delegation_packet"])
            task_text = task_path.read_text(encoding="utf-8")
            packet_text = packet_path.read_text(encoding="utf-8")
            self.assertIn("Phase: reference-analysis", task_text)
            self.assertIn(f"Delegation packet: {payload['delegation_packet']}", task_text)
            self.assertIn("Role: Reference Research", packet_text)
            self.assertIn("User language:", packet_text)
            self.assertIn("Code permission:", packet_text)
            self.assertIn("Expected output:", packet_text)

    def test_task_validate_rejects_worker_phase_owned_by_conductor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = root / "agents" / "tasks" / "2026-06-12-reference-analysis.md"
            task.parent.mkdir(parents=True, exist_ok=True)
            task.write_text(
                MINIMAL_TASK.format(owner="Conductor", packet="agents/delegations/2026-06-12-reference-analysis.md"),
                encoding="utf-8",
            )
            support = root / "agents" / "tasks"
            (support / "progress").mkdir(parents=True, exist_ok=True)
            (support / "checkpoints").mkdir(parents=True, exist_ok=True)
            (support / "progress" / task.name).write_text(
                f"# Progress\n\nLinked task: `agents/tasks/{task.name}`\n",
                encoding="utf-8",
            )
            (support / "checkpoints" / task.name).write_text(
                f"# Checkpoint\n\nLinked task: `agents/tasks/{task.name}`\n",
                encoding="utf-8",
            )

            messages = [issue.message for issue in validate_harness(root)]

            self.assertTrue(any("Worker phase reference-analysis cannot be owned by Conductor" in message for message in messages))

    def test_task_validate_rejects_missing_or_incomplete_delegation_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = root / "agents" / "tasks" / "2026-06-12-reference-analysis.md"
            task.parent.mkdir(parents=True, exist_ok=True)
            packet_rel = "agents/delegations/2026-06-12-reference-analysis.md"
            task.write_text(MINIMAL_TASK.format(owner="Reference Research", packet=packet_rel), encoding="utf-8")
            support = root / "agents" / "tasks"
            (support / "progress").mkdir(parents=True, exist_ok=True)
            (support / "checkpoints").mkdir(parents=True, exist_ok=True)
            (support / "progress" / task.name).write_text(
                f"# Progress\n\nLinked task: `agents/tasks/{task.name}`\n",
                encoding="utf-8",
            )
            (support / "checkpoints" / task.name).write_text(
                f"# Checkpoint\n\nLinked task: `agents/tasks/{task.name}`\n",
                encoding="utf-8",
            )

            missing_messages = [issue.message for issue in validate_harness(root)]
            self.assertTrue(any("Missing delegation packet" in message for message in missing_messages))

            packet = root / packet_rel
            packet.parent.mkdir(parents=True, exist_ok=True)
            packet.write_text(
                "# Delegation Packet\n\nRole: Reference Research\nTask file: agents/tasks/2026-06-12-reference-analysis.md\n",
                encoding="utf-8",
            )

            incomplete_messages = [issue.message for issue in validate_harness(root)]
            self.assertTrue(any("Delegation packet missing field" in message for message in incomplete_messages))


if __name__ == "__main__":
    unittest.main()
