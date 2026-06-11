from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def is_source_project() -> bool:
    return (ROOT / "README.md").read_text(encoding="utf-8").lstrip().startswith("# HARNESS_88")


class StackNeutralDocsTests(unittest.TestCase):
    def read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_start_here_contains_first_chat_stack_flow(self) -> None:
        path = ROOT / "START_HERE.md"

        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8").casefold()
        for needle in [
            "first chat",
            "stack/fullstack",
            "readiness",
            "product.md",
            "design.md",
            "stack.md",
            "task",
        ]:
            self.assertIn(needle, text)

    def test_stack_md_starts_unselected(self) -> None:
        path = ROOT / "STACK.md"

        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8").casefold()
        self.assertIn("status: unselected", text)
        self.assertIn("selected_profile: none", text)
        self.assertIn("first project chat", text)

    def test_stack_profiles_are_documented(self) -> None:
        text = self.read("agents/harness/stack-options.md")

        for profile in ["next-static", "next-fullstack", "astro-content", "sveltekit", "custom"]:
            self.assertIn(profile, text)

    def test_root_docs_are_stack_neutral(self) -> None:
        docs = {
            rel: self.read(rel).casefold()
            for rel in [
                "README.md",
                "AGENTS.md",
                "AGENT_SITE_TOOLING.md",
                "PRODUCT.md",
                "DESIGN.md",
                "agents/TEAM.md",
                "agents/conductor.md",
            ]
        }
        combined = "\n".join(docs.values())

        self.assertIn("start_here.md", combined)
        self.assertIn("stack.md", combined)
        self.assertIn("autonomous core", combined)
        self.assertIn("optional bundled next.js starter", combined)
        self.assertNotIn("frontend stack: next.js app router", combined)
        self.assertNotIn("a next.js frontend in `frontend/`", combined)

    def test_one_agent_fallback_protocol_is_documented(self) -> None:
        text = (self.read("agents/TEAM.md") + "\n" + self.read("agents/conductor.md")).casefold()

        for needle in [
            "multi_agent_v1",
            "unavailable",
            "worker role",
            "task file",
            "progress",
            "checkpoint",
            "production-code changes",
        ]:
            self.assertIn(needle, text)

    def test_task_template_uses_date_placeholder(self) -> None:
        text = self.read("agents/tasks/_template.md")

        self.assertNotIn("Created: 2026-06-11", text)
        self.assertIn("Created: YYYY-MM-DD", text)

    def test_review_records_next_postcss_audit_item(self) -> None:
        if not is_source_project():
            self.skipTest("Known Next/PostCSS audit item is source-project review history.")

        text = self.read("wiki/review.md").casefold()

        for needle in ["next@16.2.9", "postcss@8.4.31", "npm audit", "auto-fix"]:
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
