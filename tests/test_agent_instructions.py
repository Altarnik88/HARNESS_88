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
            "agents/protocols/conversation-delegation.md",
        ]:
            self.assertIn(rel, text)
            self.assertTrue((ROOT / rel).exists())

    def test_agent_first_language_reference_contract_is_documented(self) -> None:
        protocol = (ROOT / "agents" / "protocols" / "conversation-delegation.md").read_text(encoding="utf-8")
        team = (ROOT / "agents" / "TEAM.md").read_text(encoding="utf-8")
        conductor = (ROOT / "agents" / "conductor.md").read_text(encoding="utf-8")
        tooling = (ROOT / "agents" / "tooling-matrix.md").read_text(encoding="utf-8")
        delegation = (ROOT / "agents" / "templates" / "delegation-brief.md").read_text(encoding="utf-8")
        workflow = (ROOT / "agents" / "workflows" / "agentic-site-delivery.md").read_text(encoding="utf-8")
        intake = (ROOT / "SITE_INTAKE.md").read_text(encoding="utf-8")

        for needle in [
            "user language",
            "SITE_INTAKE.md",
            "https://dribbble.com/",
            "https://www.behance.net/",
            "https://www.awwwards.com/",
            "agent-first",
        ]:
            self.assertIn(needle, protocol)

        self.assertIn("Reference Research", team)
        self.assertIn("agent-first", conductor)
        self.assertIn("Reference Research", tooling)
        self.assertIn("User language", delegation)
        self.assertIn("Reference/source scope", delegation)
        self.assertIn("If no suitable role or tooling grant exists", team)
        self.assertIn("update the role/tooling contract before delegating", workflow)
        self.assertIn("update the role file and this matrix before delegating", tooling)
        self.assertIn("stop and update that contract before delegating", delegation)
        self.assertIn("primary site language, not the user/chat language", intake)


if __name__ == "__main__":
    unittest.main()
