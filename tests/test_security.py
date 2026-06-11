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


if __name__ == "__main__":
    unittest.main()
