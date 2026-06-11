from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_wiki.cli import main


class SiteDoctorTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_site_doctor_json_reports_core_sections(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "site", "doctor", "--json", "--skip-self-test")

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        for key in [
            "readiness",
            "stack",
            "briefs",
            "tasks",
            "wiki",
            "frontend",
            "security",
            "generated_project_self_test",
        ]:
            self.assertIn(key, payload)
        self.assertEqual(payload["generated_project_self_test"]["status"], "skipped")
        self.assertEqual(payload["security"]["status"], "not-run")


if __name__ == "__main__":
    unittest.main()
