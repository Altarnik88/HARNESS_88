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
            "agents/protocols/design-resources.md",
            "agents/protocols/tooling-onboarding.md",
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

    def test_design_resources_contract_is_documented(self) -> None:
        protocol = (ROOT / "agents" / "protocols" / "design-resources.md").read_text(encoding="utf-8")
        tooling = (ROOT / "agents" / "tooling-matrix.md").read_text(encoding="utf-8")
        ux = (ROOT / "agents" / "roles" / "ux-product-design.md").read_text(encoding="utf-8")
        visual = (ROOT / "agents" / "roles" / "visual-design.md").read_text(encoding="utf-8")
        reference = (ROOT / "agents" / "roles" / "reference-research.md").read_text(encoding="utf-8")
        frontend = (ROOT / "agents" / "roles" / "frontend-implementation.md").read_text(encoding="utf-8")
        workflow = (ROOT / "agents" / "workflows" / "agentic-site-delivery.md").read_text(encoding="utf-8")
        delegation = (ROOT / "agents" / "templates" / "delegation-brief.md").read_text(encoding="utf-8")

        for needle in [
            "https://github.com/alchaincyf/huashu-design",
            "https://github.com/pbakaus/impeccable",
            "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
            "https://github.com/greensock/GSAP/",
            "plugin://canva@openai-curated-remote",
        ]:
            self.assertIn(needle, protocol)

        for text in [tooling, ux, visual, reference, frontend, workflow, delegation]:
            self.assertIn("agents/protocols/design-resources.md", text)

    def test_tooling_onboarding_contract_is_documented(self) -> None:
        protocol = (ROOT / "agents" / "protocols" / "tooling-onboarding.md").read_text(encoding="utf-8")
        conductor = (ROOT / "agents" / "conductor.md").read_text(encoding="utf-8")
        tooling = (ROOT / "AGENT_SITE_TOOLING.md").read_text(encoding="utf-8")
        start_here = (ROOT / "START_HERE.md").read_text(encoding="utf-8")

        for needle in [
            "python tools/llm_wiki.py tools audit --json",
            "next_actions",
            "agents/resources/tooling-sources.json",
            "permission",
            "GitHub",
            "Codex plugin",
        ]:
            self.assertIn(needle, protocol)

        for text in [conductor, tooling, start_here]:
            self.assertIn("agents/protocols/tooling-onboarding.md", text)


if __name__ == "__main__":
    unittest.main()
