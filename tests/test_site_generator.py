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
from llm_wiki.site_generator import create_site_project


class SiteGeneratorTests(unittest.TestCase):
    def test_create_site_project_omits_local_only_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"

            result = create_site_project(ROOT, target)

            self.assertEqual(result.target, target)
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / "START_HERE.md").exists())
            self.assertTrue((target / "STACK.md").exists())
            self.assertTrue((target / "LICENSE").exists())
            self.assertTrue((target / "NOTICE" / "THIRD_PARTY.md").exists())
            self.assertTrue((target / "agents" / "harness" / "stack-options.md").exists())
            self.assertTrue((target / "frontend" / "src" / "app" / "page.tsx").exists())
            self.assertTrue((target / "raw" / "sources" / ".gitkeep").exists())
            self.assertTrue((target / "raw" / "assets" / ".gitkeep").exists())
            self.assertTrue((target / "wiki" / "index.md").exists())
            self.assertTrue((target / "wiki" / "log.md").exists())
            self.assertTrue((target / "wiki" / "review.md").exists())
            self.assertFalse((target / Path(".agents") / "skills").exists())
            self.assertFalse((target / Path(".codex") / "skills").exists())
            self.assertFalse((target / "docs" / "presentations").exists())
            self.assertFalse((target / "raw" / "sources" / "2026-06-11-harness-engineering-article.md").exists())
            historic_task = "2026-06-11-" + "autonomous-harness-completion.md"
            self.assertFalse((target / "agents" / "tasks" / historic_task).exists())
            self.assertFalse((target / "data" / "wiki.sqlite").exists())

    def test_create_site_project_removes_absolute_local_paths_and_demo_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"

            create_site_project(ROOT, target)

            text = "\n".join(
                path.read_text(encoding="utf-8", errors="replace")
                for path in target.rglob("*")
                if path.is_file() and path.suffix.lower() in {".md", ".tsx", ".ts", ".json", ".yml", ".yaml", ".toml", ".css"}
            )
            self.assertNotIn("C:\\Users\\Io", text)
            self.assertNotIn("To get started, edit the " + "page.tsx file.", text)
            self.assertIn("optional bundled Next.js starter", (target / "README.md").read_text(encoding="utf-8"))
            self.assertIn("status: unselected", (target / "STACK.md").read_text(encoding="utf-8"))
            self.assertIn("Project ready", (target / "frontend" / "src" / "app" / "page.tsx").read_text(encoding="utf-8"))

    def test_generated_project_readiness_reports_pending_briefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"
            create_site_project(ROOT, target)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["--root", str(target), "task", "readiness", "--json"])

            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["environment_ready"])
            self.assertFalse(payload["product_design_ready"])
            self.assertEqual(payload["pending_decisions"], ["PRODUCT.md", "DESIGN.md", "STACK.md"])

    def test_cli_site_init_creates_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(["--root", str(ROOT), "site", "init", str(target)])

            self.assertEqual(code, 0)
            self.assertIn("Created clean site project", stdout.getvalue())
            self.assertTrue((target / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
