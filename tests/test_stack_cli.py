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


class StackCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_stack_list_outputs_available_profiles(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "stack", "list")

        self.assertEqual(code, 0)
        for profile in ["next-static", "next-fullstack", "astro-content", "sveltekit", "custom"]:
            self.assertIn(profile, output)
        self.assertIn("Pros:", output)
        self.assertIn("Cons:", output)
        self.assertIn("Deployment:", output)

    def test_stack_list_json_includes_profile_metadata(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "stack", "list", "--json")

        self.assertEqual(code, 0)
        profiles = {row["name"]: row for row in json.loads(output)}
        next_static = profiles["next-static"]
        for key in [
            "commands",
            "required_tools",
            "ci_policy",
            "frontend",
            "backend",
            "deploy_notes",
            "languages",
            "frameworks",
            "services",
            "best_for",
            "pros",
            "cons",
            "scaffold_policy",
            "selection_questions",
            "deployment_options",
        ]:
            self.assertIn(key, next_static)
        self.assertTrue(next_static["frontend"])
        self.assertFalse(next_static["backend"])
        self.assertIn("TypeScript", next_static["languages"])
        self.assertTrue(next_static["pros"])
        self.assertTrue(next_static["cons"])
        self.assertIn("approved scaffold task", next_static["scaffold_policy"].casefold())
        deployment_options = {row["name"].casefold(): row for row in next_static["deployment_options"]}
        self.assertIn("vps/vds", deployment_options)
        self.assertIn("managed hosting", deployment_options)
        self.assertTrue(deployment_options["vps/vds"]["pros"])
        self.assertTrue(deployment_options["vps/vds"]["cons"])
        self.assertTrue(deployment_options["managed hosting"]["pros"])
        self.assertTrue(deployment_options["managed hosting"]["cons"])

    def test_stack_status_reads_stack_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "STACK.md").write_text(
                "status: unselected\nselected_profile: none\nnote: stack is selected in the first project chat\n",
                encoding="utf-8",
            )

            code, output = self.run_cli("--root", str(root), "stack", "status")

            self.assertEqual(code, 0)
            self.assertIn("unselected", output)
            self.assertIn("none", output)

    def test_stack_select_updates_stack_md_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            frontend.mkdir()
            (frontend / "package.json").write_text("{}", encoding="utf-8")

            code, output = self.run_cli("--root", str(root), "stack", "select", "next-static")

            self.assertEqual(code, 0)
            self.assertIn("next-static", output)
            text = (root / "STACK.md").read_text(encoding="utf-8")
            self.assertIn("status: selected", text)
            self.assertIn("selected_profile: next-static", text)
            self.assertFalse((frontend / "node_modules").exists())
            self.assertIn("No dependencies were installed and no frontend was scaffolded", output)

    def test_unknown_stack_profile_prints_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, output = self.run_cli("--root", tmp, "stack", "select", "rails")

            self.assertNotEqual(code, 0)
            self.assertIn("Unknown stack profile: rails", output)
            self.assertIn("next-static", output)
            self.assertIn("custom", output)

    def test_stack_status_json_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "STACK.md").write_text(
                "status: selected\nselected_profile: sveltekit\nnote: selected during first chat\n",
                encoding="utf-8",
            )

            code, output = self.run_cli("--root", str(root), "stack", "status", "--json")

            self.assertEqual(code, 0)
            payload = json.loads(output)
            self.assertEqual(payload["status"], "selected")
            self.assertEqual(payload["selected_profile"], "sveltekit")

    def test_stack_deploy_template_json_is_profile_aware_and_inactive(self) -> None:
        code, output = self.run_cli("--root", str(ROOT), "stack", "deploy-template", "next-static", "--json")

        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        self.assertEqual(payload["profile"], "next-static")
        self.assertEqual(payload["status"], "inactive-until-stack-approved")
        self.assertEqual(payload["template_path"], "agents/harness/deploy-handoff-template.md")
        self.assertFalse(payload["selects_stack"])
        self.assertTrue(payload["handoff"]["frontend"])
        self.assertFalse(payload["handoff"]["backend"])
        self.assertIn("security secret-plan", payload["handoff"]["secret_handling"])

    def test_stack_deploy_template_does_not_update_stack_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stack = root / "STACK.md"
            stack.write_text("status: unselected\nselected_profile: none\nnote: untouched\n", encoding="utf-8")

            code, output = self.run_cli("--root", str(root), "stack", "deploy-template", "sveltekit", "--json")

            self.assertEqual(code, 0, output)
            self.assertEqual(stack.read_text(encoding="utf-8"), "status: unselected\nselected_profile: none\nnote: untouched\n")

    def test_deploy_handoff_template_mentions_all_profiles_and_is_inactive(self) -> None:
        text = (ROOT / "agents" / "harness" / "deploy-handoff-template.md").read_text(encoding="utf-8")

        self.assertIn("inactive until stack/profile approval", text.casefold())
        for profile in ["next-static", "next-fullstack", "astro-content", "sveltekit", "custom"]:
            self.assertIn(profile, text)


if __name__ == "__main__":
    unittest.main()
