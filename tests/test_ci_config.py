from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CiConfigTests(unittest.TestCase):
    def test_quality_workflow_splits_core_and_optional_frontend_jobs(self) -> None:
        text = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")

        self.assertIn("core-quality:", text)
        self.assertIn("optional-frontend:", text)
        self.assertIn("python tools/llm_wiki.py quality --skip-frontend", text)
        self.assertIn("frontend/package.json", text)


if __name__ == "__main__":
    unittest.main()
