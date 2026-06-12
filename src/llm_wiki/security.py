from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SecurityRunner = Callable[[list[str], Path], tuple[int, str, str]]

PROVIDER_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
VARIABLE_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
LONG_SECRET_TOKEN_RE = re.compile(r"[A-Za-z0-9_./+=-]{32,}")
SECRET_MARKERS = (
    "sk-",
    "ghp_",
    "github_pat_",
    "xoxb-",
    "eyj",
    "service_role=",
    "secret=",
    "token=",
    "password=",
    "api_key=",
)


@dataclass(frozen=True)
class SecurityIssue:
    package: str
    severity: str
    title: str
    via: list[str]
    url: str
    fix_available: bool | str
    allowed: bool = False

    def to_json(self) -> dict[str, object]:
        return {
            "package": self.package,
            "severity": self.severity,
            "title": self.title,
            "via": self.via,
            "url": self.url,
            "fix_available": self.fix_available,
            "allowed": self.allowed,
        }


@dataclass(frozen=True)
class SecurityAuditResult:
    status: str
    command: list[str]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    issues: list[SecurityIssue]
    message: str
    recorded_review: bool = False
    availability_reason: str = ""

    @property
    def unresolved_count(self) -> int:
        return len([issue for issue in self.issues if not issue.allowed])

    @property
    def allowed_count(self) -> int:
        return len([issue for issue in self.issues if issue.allowed])

    def to_json(self) -> dict[str, object]:
        return {
            "status": self.status,
            "command": self.command,
            "cwd": self.cwd,
            "exit_code": self.exit_code,
            "message": self.message,
            "availability_reason": self.availability_reason,
            "unresolved_count": self.unresolved_count,
            "allowed_count": self.allowed_count,
            "recorded_review": self.recorded_review,
            "issues": [issue.to_json() for issue in self.issues],
            "stderr": self.stderr,
        }


def build_secret_plan(provider: str, variable_names: list[str], operation: str) -> dict[str, object]:
    provider_id = provider.strip().casefold()
    operation_text = operation.strip()
    validate_secret_plan_metadata(provider_id, variable_names, operation_text)
    return {
        "provider": provider_id,
        "required_variable_names": variable_names,
        "operation": operation_text,
        "status": "dry-run",
        "secret_values_visible": False,
        "next_action": (
            "Ask the user to run the local secret broker and provide these variable values there; "
            "do not paste secret values into chat, project files, MCP arguments, or logs."
        ),
    }


def validate_secret_plan_metadata(provider: str, variable_names: list[str], operation: str) -> None:
    if not provider or not PROVIDER_RE.fullmatch(provider):
        raise ValueError("Provider must be a non-secret provider id such as supabase, stripe, vercel, or custom.")
    if not variable_names:
        raise ValueError("At least one required variable name is required.")
    for name in variable_names:
        if not VARIABLE_NAME_RE.fullmatch(name):
            raise ValueError("Secret-plan --vars accepts variable names only; do not pass values or key=value pairs.")
        if looks_like_secret_value(name):
            raise ValueError("Secret-plan --vars accepts variable names only; do not pass secret values.")
    if not operation:
        raise ValueError("Operation must describe the non-secret broker action.")
    if looks_like_secret_value(operation):
        raise ValueError("Operation must not contain secret-looking values.")


def looks_like_secret_value(value: str) -> bool:
    normalized = value.strip().casefold()
    if "=" in value:
        return True
    if any(marker in normalized for marker in SECRET_MARKERS):
        return True
    if LONG_SECRET_TOKEN_RE.fullmatch(value) and "_" not in value:
        return True
    if LONG_SECRET_TOKEN_RE.search(value) and not VARIABLE_NAME_RE.fullmatch(value):
        return True
    return False


def rejected_secret_plan_receipt(message: str) -> dict[str, object]:
    return {
        "status": "rejected",
        "message": message,
        "secret_values_visible": False,
        "next_action": "Provide only non-secret metadata: provider id, variable names, and operation description.",
    }


def run_security_audit(
    root: Path,
    blocking: bool = False,
    no_record: bool = False,
    allowlist_path: Path | None = None,
    runner: SecurityRunner | None = None,
) -> SecurityAuditResult:
    frontend = root / "frontend"
    package_json = frontend / "package.json"
    package_lock = frontend / "package-lock.json"
    command = ["npm", "audit", "--json"]
    if not package_json.exists():
        return SecurityAuditResult(
            status="skipped",
            command=command,
            cwd=str(frontend),
            exit_code=0,
            stdout="",
            stderr="",
            issues=[],
            message="No frontend/package.json found; npm audit skipped.",
        )
    if not package_lock.exists():
        return SecurityAuditResult(
            status="skipped",
            command=command,
            cwd=str(frontend),
            exit_code=0,
            stdout="",
            stderr="",
            issues=[],
            message="No frontend/package-lock.json found; npm audit skipped.",
        )

    execute = runner or run_npm_audit
    exit_code, stdout, stderr = execute(command, frontend)
    issues = parse_npm_audit_json(stdout, load_allowlist(allowlist_path))
    if issues:
        status = "issues" if any(not issue.allowed for issue in issues) else "allowed"
        recorded = False
        if not no_record and any(not issue.allowed for issue in issues):
            record_security_review_items(root, [issue for issue in issues if not issue.allowed])
            recorded = True
        return SecurityAuditResult(
            status=status,
            command=command,
            cwd=str(frontend),
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            issues=issues,
            message="npm audit reported unresolved security items."
            if status == "issues"
            else "npm audit findings are covered by the allowlist.",
            recorded_review=recorded,
        )
    if exit_code != 0:
        availability_reason = audit_unavailable_reason(stdout, stderr)
        return SecurityAuditResult(
            status="network-unavailable" if availability_reason == "network" else "unavailable",
            command=command,
            cwd=str(frontend),
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            issues=[],
            message=unavailable_message(availability_reason),
            availability_reason=availability_reason,
        )
    return SecurityAuditResult(
        status="clean",
        command=command,
        cwd=str(frontend),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        issues=[],
        message="npm audit reported no vulnerabilities.",
    )


def run_npm_audit(command: list[str], cwd: Path) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            resolve_command(command),
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except OSError as exc:
        return 1, "", str(exc)
    return completed.returncode, completed.stdout, completed.stderr


def audit_unavailable_reason(stdout: str, stderr: str) -> str:
    combined = f"{stdout}\n{stderr}".casefold()
    network_markers = [
        " eacces ",
        " econnreset ",
        " enotfound ",
        " etimedout ",
        " eai_again ",
        "network",
        "could not resolve",
        "connect timeout",
        "connection refused",
    ]
    padded = f" {combined} "
    if "registry.npmjs.org" in combined and any(marker in padded for marker in network_markers):
        return "network"
    if any(marker in padded for marker in network_markers):
        return "network"
    return "parse-error"


def unavailable_message(reason: str) -> str:
    if reason == "network":
        return "npm audit could not reach the npm registry; network access may be unavailable or blocked."
    return "npm audit did not return parseable vulnerability JSON."


def resolve_command(command: list[str]) -> list[str]:
    if not command:
        return command
    resolved = shutil.which(command[0])
    if resolved:
        return [resolved, *command[1:]]
    return command


def parse_npm_audit_json(stdout: str, allowlist: set[str] | None = None) -> list[SecurityIssue]:
    allowlist = allowlist or set()
    try:
        payload = json.loads(stdout or "{}")
    except json.JSONDecodeError:
        return []
    vulnerabilities = payload.get("vulnerabilities")
    if not isinstance(vulnerabilities, dict):
        return []
    issues: list[SecurityIssue] = []
    for package, row in sorted(vulnerabilities.items()):
        if not isinstance(row, dict):
            continue
        via_values, title, url = parse_via(row.get("via", []))
        issue = SecurityIssue(
            package=str(row.get("name") or package),
            severity=str(row.get("severity") or "unknown"),
            title=title or str(package),
            via=via_values,
            url=url,
            fix_available=parse_fix_available(row.get("fixAvailable")),
        )
        issues.append(mark_allowed(issue, allowlist))
    return issues


def parse_via(raw_via: Any) -> tuple[list[str], str, str]:
    via_values: list[str] = []
    title = ""
    url = ""
    if not isinstance(raw_via, list):
        raw_via = [raw_via]
    for item in raw_via:
        if isinstance(item, dict):
            item_title = str(item.get("title") or item.get("name") or "")
            if item_title:
                via_values.append(item_title)
            if not title and item_title:
                title = item_title
            if not url and item.get("url"):
                url = str(item["url"])
        elif item:
            via_values.append(str(item))
            if not title:
                title = str(item)
    return via_values, title, url


def parse_fix_available(value: Any) -> bool | str:
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        name = value.get("name")
        version = value.get("version")
        if name and version:
            return f"{name}@{version}"
    return False


def mark_allowed(issue: SecurityIssue, allowlist: set[str]) -> SecurityIssue:
    searchable = " ".join([issue.package, issue.title, issue.url, *issue.via]).casefold()
    allowed = any(token.casefold() in searchable for token in allowlist)
    return SecurityIssue(
        package=issue.package,
        severity=issue.severity,
        title=issue.title,
        via=issue.via,
        url=issue.url,
        fix_available=issue.fix_available,
        allowed=allowed,
    )


def load_allowlist(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {str(item) for item in payload}
    if isinstance(payload, dict):
        raw = payload.get("allow", [])
        if isinstance(raw, list):
            return {str(item) for item in raw}
    return set()


def record_security_review_items(root: Path, issues: list[SecurityIssue]) -> None:
    review_path = root / "wiki" / "review.md"
    if review_path.exists():
        text = review_path.read_text(encoding="utf-8")
    else:
        review_path.parent.mkdir(parents=True, exist_ok=True)
        text = """---
title: Review
type: overview
status: draft
confidence: medium
sources: []
tags: []
summary: Human-in-the-loop decisions and unresolved review items.
---

# Review
"""
    section_lines = [
        "",
        "## Security audit unresolved items",
        "",
        "Generated by `python tools/llm_wiki.py security audit`.",
        "",
    ]
    for issue in issues:
        section_lines.append(f"- `{issue.package}` ({issue.severity}): {issue.title}")
    section = "\n".join(section_lines).rstrip() + "\n"
    marker = "## Security audit unresolved items"
    if marker in text:
        text = text[: text.index(marker)].rstrip() + "\n" + section
    else:
        text = text.rstrip() + "\n" + section
    review_path.write_text(text, encoding="utf-8")


def security_exit_code(result: SecurityAuditResult, blocking: bool = False) -> int:
    return 1 if blocking and result.unresolved_count and result.status == "issues" else 0
