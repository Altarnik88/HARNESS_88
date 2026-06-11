from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class AgentInstructionTests(unittest.TestCase):
    def test_agent_instruction_files_stay_under_line_limit(self) -> None:
        for path in ROOT.rglob("*"):
            if path.name not in {"AGENTS.md", "CLAUDE.md"}:
                continue
            if any(part in {"node_modules", ".next", ".git"} for part in path.parts):
                continue
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(line_count, 150, str(path.relative_to(ROOT)))

    def test_root_agents_links_detailed_protocol_files(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        for rel in [
            "agents/protocols/mcp-policy.md",
            "agents/protocols/wiki-operations.md",
            "agents/protocols/skill-capture.md",
        ]:
            self.assertIn(rel, text)
            self.assertTrue((ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
