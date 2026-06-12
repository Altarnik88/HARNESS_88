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
from llm_wiki.site_generator import SITE_STARTER_TEMPLATE_ROOT, create_site_project


def is_source_project() -> bool:
    return (ROOT / "README.md").read_text(encoding="utf-8").lstrip().startswith("# HARNESS_88")


class SiteGeneratorTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_create_site_project_omits_local_only_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"

            result = create_site_project(ROOT, target)

            self.assertEqual(result.target, target)
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / "START_HERE.md").exists())
            self.assertTrue((target / "SITE_GATES.md").exists())
            self.assertTrue((target / "SITE_INTAKE.md").exists())
            self.assertTrue((target / "SITE_REFERENCES.md").exists())
            self.assertTrue((target / "STACK.md").exists())
            self.assertTrue((target / "LICENSE").exists())
            self.assertTrue((target / "NOTICE" / "THIRD_PARTY.md").exists())
            self.assertTrue((target / "agents" / "harness" / "stack-options.md").exists())
            self.assertTrue((target / "agents" / "protocols" / "wiki-operations.md").exists())
            self.assertTrue((target / "agents" / "resources" / "tooling-sources.json").exists())
            self.assertFalse((target / "frontend").exists())
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
            self.assertNotIn("optional bundled Next.js starter", (target / "README.md").read_text(encoding="utf-8"))
            self.assertIn("No frontend app is bundled", (target / "README.md").read_text(encoding="utf-8"))
            self.assertIn("status: unselected", (target / "STACK.md").read_text(encoding="utf-8"))
            self.assertFalse((target / "frontend").exists())

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
            self.assertEqual(payload["pending_decisions"], ["PRODUCT.md", "DESIGN.md", "STACK.md", "SITE_INTAKE.md", "references"])
            self.assertFalse(payload["intake_ready"])
            self.assertFalse(payload["references_ready"])
            self.assertFalse(payload["reference_analysis_ready"])
            self.assertFalse(payload["delivery_gates_ready"])
            self.assertFalse(payload["publish_ready"])

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["--root", str(target), "site", "intake", "--json"])

            self.assertEqual(code, 0)
            intake = json.loads(stdout.getvalue())
            self.assertEqual(intake["path"], "SITE_INTAKE.md")
            self.assertFalse(intake["intake_ready"])

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["--root", str(target), "site", "references", "--json"])

            self.assertEqual(code, 0)
            references = json.loads(stdout.getvalue())
            self.assertEqual(references["path"], "SITE_REFERENCES.md")
            self.assertFalse(references["reference_analysis_ready"])

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["--root", str(target), "site", "gates", "--json"])

            self.assertEqual(code, 0)
            gates = json.loads(stdout.getvalue())
            self.assertEqual(gates["path"], "SITE_GATES.md")
            self.assertFalse(gates["publish_ready"])

    def test_generated_project_includes_agentic_delivery_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"
            create_site_project(ROOT, target)

            workflow = (target / "agents" / "workflows" / "agentic-site-delivery.md").read_text(encoding="utf-8")
            tooling = (target / "AGENT_SITE_TOOLING.md").read_text(encoding="utf-8")
            start_here = (target / "START_HERE.md").read_text(encoding="utf-8")

            for needle in [
                "ecommerce with online payment",
                "purchase request/lead form for a manager",
                "Reference Analysis Gate",
                "SITE_REFERENCES.md",
                "Bounded",
                "Figma reference artifact",
                "Total Agent Audit",
                "Remediation Plan and Fix Loop",
                "Final User Approval",
                "publication instructions for the approved target",
            ]:
                self.assertIn(needle, workflow)
            self.assertIn("Do not begin serious frontend implementation", tooling)
            self.assertIn("site references --json", tooling)
            self.assertIn("Never ask the user to paste secrets into chat", tooling)
            self.assertIn("ecommerce/catalog/payment/request mode", start_here)
            self.assertIn("VPS/VDS vs hosting", start_here)
            self.assertIn("pros and cons", start_here)
            self.assertIn("site intake --json", start_here)
            self.assertIn("site references --json", start_here)
            self.assertIn("site gates --json", start_here)
            self.assertIn("SITE_INTAKE.md", tooling)
            self.assertIn("SITE_REFERENCES.md", tooling)
            self.assertIn("SITE_GATES.md", tooling)
            self.assertTrue((target / "agents" / "workflows" / "secret-broker.md").exists())
            self.assertIn(
                "task evidence --json",
                (target / "agents" / "tasks" / "README.md").read_text(encoding="utf-8"),
            )

    def test_generated_project_includes_conversation_delegation_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"
            create_site_project(ROOT, target)

            protocol = (target / "agents" / "protocols" / "conversation-delegation.md").read_text(encoding="utf-8")
            workflow = (target / "agents" / "workflows" / "agentic-site-delivery.md").read_text(encoding="utf-8")
            team = (target / "agents" / "TEAM.md").read_text(encoding="utf-8")
            delegation = (target / "agents" / "templates" / "delegation-brief.md").read_text(encoding="utf-8")
            tooling = (target / "AGENT_SITE_TOOLING.md").read_text(encoding="utf-8")
            intake = (target / "SITE_INTAKE.md").read_text(encoding="utf-8")

            for needle in [
                "user language",
                "https://dribbble.com/",
                "https://www.behance.net/",
                "https://www.awwwards.com/",
                "agent-first",
            ]:
                self.assertIn(needle, protocol)
            self.assertIn("Reference Research", team)
            self.assertIn("Reference Research", workflow)
            self.assertIn("User language", delegation)
            self.assertIn("Reference/source scope", delegation)
            self.assertIn("questions in the user's language", tooling)
            self.assertIn("update the role/tooling contract before delegating", workflow)
            self.assertIn("primary site language, not the user/chat language", intake)
            self.assertIn("https://dribbble.com/", intake)

    def test_generated_project_includes_conductor_runtime_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"
            create_site_project(ROOT, target)

            start_here = (target / "START_HERE.md").read_text(encoding="utf-8")
            protocol = (target / "agents" / "protocols" / "conductor-runtime.md").read_text(encoding="utf-8")
            conductor = (target / "agents" / "conductor.md").read_text(encoding="utf-8")
            team = (target / "agents" / "TEAM.md").read_text(encoding="utf-8")
            design_artifact = (target / "agents" / "roles" / "design-artifact.md").read_text(encoding="utf-8")

            self.assertIn("python tools/llm_wiki.py conductor start", start_here)
            self.assertIn("Conductor online", start_here)
            self.assertIn("Conductor cannot self-assign worker phases", protocol)
            self.assertIn("agents/delegations/", protocol)
            self.assertIn("conductor start", conductor)
            self.assertIn("Design Artifact", team)
            self.assertIn("Figma reference board", design_artifact)

    def test_generated_project_includes_design_resource_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"
            create_site_project(ROOT, target)

            protocol = (target / "agents" / "protocols" / "design-resources.md").read_text(encoding="utf-8")
            registry = (target / "agents" / "resources" / "tooling-sources.json").read_text(encoding="utf-8")

            for needle in [
                "https://github.com/alchaincyf/huashu-design",
                "https://github.com/pbakaus/impeccable",
                "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
                "https://github.com/greensock/GSAP/",
                "plugin://canva@openai-curated-remote",
                "plugin://creative-production@openai-curated-remote",
            ]:
                self.assertIn(needle, protocol)
                self.assertIn(needle, registry)
            self.assertIn("Creative exploration is a first-class deliverable", protocol)
            self.assertIn("Registered design resources", protocol)

    def test_generated_project_includes_current_mcp_sources_without_node_repl_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"
            create_site_project(ROOT, target)

            registry = (target / "agents" / "resources" / "tooling-sources.json").read_text(encoding="utf-8")
            capabilities = (target / "src" / "llm_wiki" / "capabilities.py").read_text(encoding="utf-8")
            tooling = (target / "agents" / "tooling-matrix.md").read_text(encoding="utf-8")

            for needle in [
                "https://github.com/upstash/context7",
                "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
                "https://github.com/microsoft/playwright-mcp",
                "https://github.com/oraios/serena",
                "https://github.com/modelcontextprotocol/servers-archived/tree/main/src/sqlite",
            ]:
                self.assertIn(needle, registry)
            for text in [registry, capabilities, tooling]:
                self.assertNotIn("node_repl", text)
                self.assertNotIn("node-repl", text)

    def test_generated_project_includes_tooling_audit_onboarding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"
            create_site_project(ROOT, target)

            start_here = (target / "START_HERE.md").read_text(encoding="utf-8")
            tooling = (target / "AGENT_SITE_TOOLING.md").read_text(encoding="utf-8")
            readme = (target / "README.md").read_text(encoding="utf-8")

            for text in [start_here, tooling, readme]:
                self.assertIn("python tools/llm_wiki.py tools audit", text)
                self.assertIn("agents/resources/tooling-sources.json", text)
                self.assertIn("python tools/llm_wiki.py site doctor --skip-self-test", text)
            self.assertIn("agents/protocols/tooling-onboarding.md", start_here)
            self.assertIn("agents/protocols/tooling-onboarding.md", tooling)
            self.assertTrue((target / "agents" / "protocols" / "tooling-onboarding.md").exists())
            self.assertIn("asks permission before installing", tooling)

    def test_cli_site_init_creates_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"

            code, output = self.run_cli("--root", str(ROOT), "site", "init", str(target))

            self.assertEqual(code, 0)
            self.assertIn("Created clean site project", output)
            self.assertTrue((target / "README.md").exists())

    def test_starter_templates_match_generated_overlay_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"

            create_site_project(ROOT, target)

            for template_path in sorted(SITE_STARTER_TEMPLATE_ROOT.rglob("*")):
                if not template_path.is_file():
                    continue
                rel = template_path.relative_to(SITE_STARTER_TEMPLATE_ROOT)
                self.assertEqual(
                    template_path.read_text(encoding="utf-8"),
                    (target / rel).read_text(encoding="utf-8"),
                    f"Generated file drifted from template: {rel.as_posix()}",
                )

    @unittest.skipUnless(is_source_project(), "Only the source project should recursively self-test generated starters.")
    def test_cli_site_init_self_test_passes_generated_core_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean-site"

            code, output = self.run_cli("--root", str(ROOT), "site", "init", str(target), "--self-test", "--json")

            self.assertEqual(code, 0, output)
            payload = json.loads(output)
            self.assertEqual(payload["self_test"]["status"], "passed")
            self.assertTrue((target / "wiki" / "review.md").read_text(encoding="utf-8").endswith("No review items recorded yet.\n"))

    @unittest.skipUnless(is_source_project(), "Only the source project should recursively self-test generated starters.")
    def test_cli_site_self_test_creates_temporary_project_and_passes(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "site", "self-test", "--json")

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        self.assertEqual(payload["status"], "passed")
        self.assertIn("python-tests", [step["name"] for step in payload["quality_results"]])


if __name__ == "__main__":
    unittest.main()
