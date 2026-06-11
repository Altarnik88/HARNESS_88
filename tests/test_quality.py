from __future__ import annotations

import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_wiki.quality import build_quality_steps, resolve_command, run_quality


class QualityGateTests(unittest.TestCase):
    def test_default_steps_include_frontend_lint_when_manifest_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "frontend").mkdir()
            (root / "frontend" / "package.json").write_text("{}", encoding="utf-8")

            steps = build_quality_steps(root, full=False)

            self.assertEqual(
                [step.name for step in steps],
                ["python-tests", "wiki-rebuild", "wiki-lint-strict", "frontend-lint"],
            )

    def test_full_steps_add_frontend_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "frontend").mkdir()
            (root / "frontend" / "package.json").write_text("{}", encoding="utf-8")

            steps = build_quality_steps(root, full=True)

            self.assertEqual(steps[-2].name, "frontend-lint")
            self.assertEqual(steps[-1].name, "frontend-build")

    def test_run_quality_continues_after_failed_step(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            calls: list[str] = []

            def fake_runner(step):
                calls.append(step.name)
                if step.name == "python-tests":
                    return 5, "failed tests", ""
                return 0, "ok", ""

            results = run_quality(root, runner=fake_runner)

            self.assertEqual(calls, ["python-tests", "wiki-rebuild", "wiki-lint-strict"])
            self.assertEqual(results[0].exit_code, 5)
            self.assertEqual(results[-1].exit_code, 0)

    def test_quality_results_are_json_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def fake_runner(step):
                return 0, "ok", ""

            results = run_quality(root, runner=fake_runner)

            rendered = json.dumps([result.to_json() for result in results])
            self.assertIn("python-tests", rendered)

    def test_resolve_command_uses_shutil_which_result(self) -> None:
        with patch("llm_wiki.quality.shutil.which", return_value="C:/node/npm.cmd"):
            command = resolve_command(["npm", "run", "lint"])

        self.assertEqual(command[0], "C:/node/npm.cmd")
        self.assertEqual(command[1:], ["run", "lint"])


if __name__ == "__main__":
    unittest.main()
