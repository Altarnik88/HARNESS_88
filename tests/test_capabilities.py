from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_wiki.capabilities import capability_audit
from llm_wiki.cli import main


class CapabilityAuditTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_capability_audit_detects_local_commands_and_codex_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp) / ".codex"
            (codex_home / "skills" / "playwright").mkdir(parents=True)
            (codex_home / "skills" / "playwright" / "SKILL.md").write_text("---\nname: playwright\n---\n")
            (codex_home / "plugins" / "cache" / "openai-curated" / "github" / "skills" / "github").mkdir(parents=True)
            (codex_home / "plugins" / "cache" / "openai-curated" / "github" / "skills" / "github" / "SKILL.md").write_text("---\nname: github\n---\n")

            def fake_which(name: str) -> str | None:
                return f"C:/bin/{name}.exe" if name in {"python", "git"} else None

            with patch("llm_wiki.capabilities.shutil.which", side_effect=fake_which):
                report = capability_audit(ROOT, codex_home=codex_home)

            items = {item["id"]: item for item in report["items"]}
            self.assertEqual(items["local.python"]["status"], "available")
            self.assertEqual(items["local.git"]["status"], "available")
            self.assertEqual(items["skill.playwright"]["status"], "available")
            self.assertEqual(items["plugin.github"]["status"], "available")
            self.assertEqual(items["plugin.browser"]["status"], "missing")
            self.assertEqual(report["status"], "needs-setup")
            self.assertTrue(report["next_actions"])
            self.assertIn("permission", report["next_actions"][0]["prompt"].casefold())

    def test_capability_catalog_covers_tooling_matrix_families(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = capability_audit(ROOT, codex_home=Path(tmp))

        ids = {item["id"] for item in report["items"]}
        for capability_id in [
            "mcp.filesystem",
            "mcp.sqlite",
            "skill.huashu-design",
            "skill.impeccable",
            "skill.ui-ux-pro-max",
            "library.gsap",
            "skill.imagegen",
            "plugin.sentry",
            "plugin.remotion",
            "plugin.canva",
            "plugin.creative-production",
            "plugin.data-analytics",
            "plugin.documents",
            "plugin.spreadsheets",
        ]:
            self.assertIn(capability_id, ids)
        self.assertNotIn("mcp.node-repl", ids)

    def test_tools_audit_json_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, output = self.run_cli("--root", str(ROOT), "tools", "audit", "--json", "--codex-home", tmp)

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        self.assertIn(payload["status"], {"ready", "needs-setup"})
        self.assertIn("summary", payload)
        self.assertIn("items", payload)
        self.assertIn("next_actions", payload)

    def test_site_doctor_includes_tooling_report(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "site", "doctor", "--json", "--skip-self-test")

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        self.assertIn("tooling", payload)
        self.assertIn("next_actions", payload["tooling"])

    def test_site_doctor_human_output_includes_tooling_summary(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "site", "doctor", "--skip-self-test")

        self.assertEqual(code, 0, output)
        self.assertIn("Tooling:", output)

    def test_tools_audit_human_output_is_compact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, output = self.run_cli("--root", str(ROOT), "tools", "audit", "--codex-home", tmp)

        self.assertEqual(code, 0, output)
        self.assertIn("Host-managed MCP/tools:", output)
        self.assertIn("Capabilities needing attention:", output)
        self.assertIn("use --json for full detail", output)
        self.assertNotIn("Capabilities:\n- available", output)

    def test_capability_audit_includes_recorded_resource_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            registry = root / "agents" / "resources" / "tooling-sources.json"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "resources": {
                            "local.gh": {
                                "source_type": "github",
                                "label": "GitHub CLI",
                                "url": "https://github.com/cli/cli",
                                "notes": "Official GitHub CLI source repository.",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            with patch("llm_wiki.capabilities.shutil.which", return_value=None):
                report = capability_audit(root, codex_home=Path(tmp) / ".codex")

        items = {item["id"]: item for item in report["items"]}
        action = next(action for action in report["next_actions"] if action["id"] == "local.gh")
        self.assertEqual(items["local.gh"]["resource_url"], "https://github.com/cli/cli")
        self.assertEqual(action["resource_url"], "https://github.com/cli/cli")
        self.assertIn("agents/resources/tooling-sources.json", action["source_registry"])

    def test_capability_audit_blocks_github_download_without_recorded_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            registry = root / "agents" / "resources" / "tooling-sources.json"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "resources": {
                            "skill.playwright": {
                                "source_type": "github",
                                "label": "Playwright skill",
                                "url": "",
                                "notes": "Record the exact user-approved skill repository before download.",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            with patch("llm_wiki.capabilities.shutil.which", return_value=None):
                report = capability_audit(root, codex_home=Path(tmp) / ".codex")

        action = next(action for action in report["next_actions"] if action["id"] == "skill.playwright")
        self.assertEqual(action["resource_url"], "")
        self.assertIn("No approved GitHub URL is recorded", action["prompt"])
        self.assertIn("agents/resources/tooling-sources.json", action["prompt"])
        self.assertTrue(action["blocked"])
        self.assertEqual(action["group"], "codex_skills")

    def test_design_resource_sources_are_registered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = capability_audit(ROOT, codex_home=Path(tmp))

        items = {item["id"]: item for item in report["items"]}
        expected_urls = {
            "skill.huashu-design": "https://github.com/alchaincyf/huashu-design",
            "skill.impeccable": "https://github.com/pbakaus/impeccable",
            "skill.ui-ux-pro-max": "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
            "library.gsap": "https://github.com/greensock/GSAP/",
            "plugin.canva": "plugin://canva@openai-curated-remote",
        }
        for capability_id, url in expected_urls.items():
            self.assertEqual(items[capability_id]["resource_url"], url)

    def test_mcp_source_links_are_registered_and_node_repl_is_not_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = capability_audit(ROOT, codex_home=Path(tmp))

        items = {item["id"]: item for item in report["items"]}
        expected_urls = {
            "mcp.context7": "https://github.com/upstash/context7",
            "mcp.filesystem": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
            "skill.playwright": "https://github.com/microsoft/playwright-mcp",
            "mcp.serena": "https://github.com/oraios/serena",
            "mcp.sqlite": "https://github.com/modelcontextprotocol/servers-archived/tree/main/src/sqlite",
        }
        for capability_id, url in expected_urls.items():
            self.assertEqual(items[capability_id]["resource_url"], url)
        self.assertNotIn("mcp.node-repl", items)

    def test_mcp_servers_are_reported_as_host_managed_when_not_locally_detectable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = capability_audit(ROOT, codex_home=Path(tmp))

        items = {item["id"]: item for item in report["items"]}
        self.assertEqual(items["mcp.serena"]["status"], "host-managed")
        self.assertFalse(items["mcp.serena"]["requires_permission"])
        self.assertIn("host-managed", items["mcp.serena"]["detected_by"])
        self.assertIn("host_managed", report["summary"])
        self.assertGreaterEqual(report["summary"]["host_managed"], 1)
        self.assertNotIn("mcp.serena", {action["id"] for action in report["next_actions"]})

    def test_tools_audit_groups_next_actions_without_removing_flat_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("llm_wiki.capabilities.shutil.which", return_value=None):
                report = capability_audit(ROOT, codex_home=Path(tmp))

        self.assertIn("next_actions", report)
        self.assertIn("next_action_groups", report)
        groups = report["next_action_groups"]
        self.assertIn("required_local_tools", groups)
        self.assertIn("codex_skills", groups)
        self.assertIn("codex_plugins", groups)
        self.assertIn("host_managed_mcp", groups)
        self.assertIn("optional_design_resources", groups)

        required_ids = {action["id"] for action in groups["required_local_tools"]}
        self.assertIn("local.python", required_ids)
        self.assertIn("local.git", required_ids)
        flat_ids = {action["id"] for action in report["next_actions"]}
        self.assertIn("local.python", flat_ids)

    def test_plugin_uri_missing_action_uses_connect_permission_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = capability_audit(ROOT, codex_home=Path(tmp))

        action = next(action for action in report["next_actions"] if action["id"] == "plugin.canva")
        self.assertEqual(action["resource_url"], "plugin://canva@openai-curated-remote")
        self.assertEqual(action["permission_kind"], "codex-plugin-connect")
        self.assertFalse(action["blocked"])
        self.assertIn("connect", action["prompt"].casefold())

    def test_host_managed_mcp_group_has_no_install_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = capability_audit(ROOT, codex_home=Path(tmp))

        groups = report["next_action_groups"]
        serena = next(action for action in groups["host_managed_mcp"] if action["id"] == "mcp.serena")
        self.assertFalse(serena["requires_permission"])
        self.assertEqual(serena["prompt"], "")
        self.assertIn("host", serena["suggested_action"].casefold())


if __name__ == "__main__":
    unittest.main()
