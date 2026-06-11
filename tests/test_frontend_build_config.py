from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FrontendBuildConfigTests(unittest.TestCase):
    def test_layout_does_not_depend_on_network_fetched_google_fonts(self) -> None:
        layout = ROOT / "frontend" / "src" / "app" / "layout.tsx"

        text = layout.read_text(encoding="utf-8")

        self.assertNotIn("next/font/google", text)

    def test_home_page_uses_clean_starter_copy(self) -> None:
        page = ROOT / "frontend" / "src" / "app" / "page.tsx"

        text = page.read_text(encoding="utf-8")

        self.assertIn("Project ready", text)
        self.assertNotIn("To get started, edit the " + "page.tsx file.", text)


if __name__ == "__main__":
    unittest.main()
