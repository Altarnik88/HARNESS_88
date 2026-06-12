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
from llm_wiki.security import run_security_audit, security_exit_code


NPM_AUDIT_JSON = json.dumps(
    {
        "vulnerabilities": {
            "postcss": {
                "name": "postcss",
                "severity": "moderate",
                "via": [
                    {
                        "title": "PostCSS line return parsing error",
                        "url": "https://github.com/advisories/example",
                    }
                ],
                "range": "<8.4.32",
                "fixAvailable": False,
            }
        },
        "metadata": {"vulnerabilities": {"moderate": 1, "total": 1}},
    }
)


class SecurityAuditTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_security_audit_skips_when_frontend_manifest_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, output = self.run_cli("--root", tmp, "security", "audit", "--json", "--no-record")

            self.assertEqual(code, 0, output)
            payload = json.loads(output)
            self.assertEqual(payload["status"], "skipped")
            self.assertEqual(payload["unresolved_count"], 0)

    def test_security_audit_records_unresolved_npm_items_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            frontend.mkdir()
            (frontend / "package.json").write_text("{}", encoding="utf-8")
            (frontend / "package-lock.json").write_text("{}", encoding="utf-8")

            def fake_runner(command: list[str], cwd: Path) -> tuple[int, str, str]:
                return 1, NPM_AUDIT_JSON, ""

            result = run_security_audit(root, runner=fake_runner)

            self.assertEqual(result.status, "issues")
            self.assertEqual(result.unresolved_count, 1)
            self.assertEqual(security_exit_code(result), 0)
            self.assertIn("postcss", (root / "wiki" / "review.md").read_text(encoding="utf-8"))

    def test_security_audit_allowlist_marks_matching_items_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            frontend.mkdir()
            (frontend / "package.json").write_text("{}", encoding="utf-8")
            (frontend / "package-lock.json").write_text("{}", encoding="utf-8")
            allowlist = root / "security-allowlist.json"
            allowlist.write_text(json.dumps({"allow": ["postcss"]}), encoding="utf-8")

            def fake_runner(command: list[str], cwd: Path) -> tuple[int, str, str]:
                return 1, NPM_AUDIT_JSON, ""

            result = run_security_audit(root, allowlist_path=allowlist, runner=fake_runner)

            self.assertEqual(result.unresolved_count, 0)
            self.assertEqual(result.allowed_count, 1)

    def test_security_audit_reports_network_unavailable_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            frontend.mkdir()
            (frontend / "package.json").write_text("{}", encoding="utf-8")
            (frontend / "package-lock.json").write_text("{}", encoding="utf-8")

            def fake_runner(command: list[str], cwd: Path) -> tuple[int, str, str]:
                return (
                    1,
                    "",
                    "npm warn audit request to https://registry.npmjs.org/-/npm/v1/security/advisories/bulk failed, reason: connect EACCES 198.20.0.36:443",
                )

            result = run_security_audit(root, no_record=True, runner=fake_runner)

            self.assertEqual(result.status, "network-unavailable")
            self.assertEqual(result.unresolved_count, 0)
            self.assertIn("network access", result.message)
            self.assertEqual(result.to_json()["availability_reason"], "network")

    def test_security_audit_reports_malformed_output_as_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            frontend.mkdir()
            (frontend / "package.json").write_text("{}", encoding="utf-8")
            (frontend / "package-lock.json").write_text("{}", encoding="utf-8")

            def fake_runner(command: list[str], cwd: Path) -> tuple[int, str, str]:
                return 1, "not-json", "npm error audit endpoint returned an error"

            result = run_security_audit(root, no_record=True, runner=fake_runner)

            self.assertEqual(result.status, "unavailable")
            self.assertEqual(result.to_json()["availability_reason"], "parse-error")

    def test_secret_plan_cli_returns_redacted_dry_run_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            code, output = self.run_cli(
                "--root",
                str(root),
                "security",
                "secret-plan",
                "--provider",
                "supabase",
                "--vars",
                "SUPABASE_URL",
                "SUPABASE_SERVICE_ROLE_KEY",
                "--operation",
                "configure deployment env",
                "--json",
            )

            self.assertEqual(code, 0, output)
            payload = json.loads(output)
            self.assertEqual(payload["provider"], "supabase")
            self.assertEqual(payload["required_variable_names"], ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"])
            self.assertEqual(payload["operation"], "configure deployment env")
            self.assertEqual(payload["status"], "dry-run")
            self.assertFalse(payload["secret_values_visible"])
            self.assertIn("broker", payload["next_action"].casefold())
            self.assertFalse((root / ".env").exists())

    def test_secret_plan_rejects_secret_values_without_echoing_them(self) -> None:
        secret_value = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.super-secret-payload"
        with tempfile.TemporaryDirectory() as tmp:
            code, output = self.run_cli(
                "--root",
                tmp,
                "security",
                "secret-plan",
                "--provider",
                "supabase",
                "--vars",
                f"SUPABASE_SERVICE_ROLE_KEY={secret_value}",
                "--operation",
                "configure deployment env",
                "--json",
            )

            self.assertEqual(code, 2, output)
            payload = json.loads(output)
            self.assertEqual(payload["status"], "rejected")
            self.assertFalse(payload["secret_values_visible"])
            self.assertNotIn(secret_value, output)
            self.assertIn("variable names only", payload["message"])

    def test_secret_plan_rejects_uppercase_token_without_echoing_it(self) -> None:
        secret_value = "A" * 40
        with tempfile.TemporaryDirectory() as tmp:
            code, output = self.run_cli(
                "--root",
                tmp,
                "security",
                "secret-plan",
                "--provider",
                "supabase",
                "--vars",
                secret_value,
                "--operation",
                "configure deployment env",
                "--json",
            )

            self.assertEqual(code, 2, output)
            payload = json.loads(output)
            self.assertEqual(payload["status"], "rejected")
            self.assertFalse(payload["secret_values_visible"])
            self.assertNotIn(secret_value, output)

    def test_secret_broker_protocol_documents_secret_plan_command(self) -> None:
        text = (ROOT / "agents" / "workflows" / "secret-broker.md").read_text(encoding="utf-8")

        self.assertIn("security secret-plan", text)
        self.assertIn("dry-run", text)
        self.assertIn("Secret values: not visible to agents", text)


if __name__ == "__main__":
    unittest.main()
