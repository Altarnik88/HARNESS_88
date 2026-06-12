from __future__ import annotations

from pathlib import Path

from .capabilities import capability_audit
from .db import collect_lint_issues
from .harness import validate_harness
from .security import run_security_audit
from .site_self_test import run_generated_site_self_test
from .stack import read_stack_status
from .tasks import readiness_report, task_metrics


def build_doctor_report(root: Path, skip_self_test: bool = False, run_security: bool = False) -> dict[str, object]:
    readiness = readiness_report(root)
    wiki_issues = collect_lint_issues(root)
    task_issues = validate_harness(root)
    report: dict[str, object] = {
        "readiness": readiness,
        "stack": read_stack_status(root),
        "briefs": readiness["briefs"],
        "intake": readiness["intake"],
        "references": readiness["references"],
        "gates": readiness["delivery_gates"],
        "tasks": {
            "metrics": task_metrics(root),
            "issue_count": len(task_issues),
            "issues": [issue.__dict__ for issue in task_issues],
        },
        "wiki": {
            "issue_count": len(wiki_issues),
            "issues": [issue.__dict__ for issue in wiki_issues],
        },
        "frontend": frontend_state(root),
        "security": security_state(root, run_security),
        "tooling": capability_audit(root),
        "generated_project_self_test": generated_self_test_state(root, skip_self_test),
    }
    report["status"] = doctor_status(report)
    return report


def frontend_state(root: Path) -> dict[str, object]:
    frontend = root / "frontend"
    package_json = frontend / "package.json"
    node_modules = frontend / "node_modules"
    return {
        "present": package_json.exists(),
        "path": "frontend",
        "dependencies_installed": node_modules.exists(),
        "next_command": "cd frontend && npm ci" if package_json.exists() and not node_modules.exists() else "",
    }


def security_state(root: Path, run_security: bool) -> dict[str, object]:
    if not run_security:
        return {
            "status": "not-run",
            "next_command": "python tools/llm_wiki.py security audit --json --no-record",
        }
    return run_security_audit(root, no_record=True).to_json()


def generated_self_test_state(root: Path, skip_self_test: bool) -> dict[str, object]:
    if skip_self_test:
        return {"status": "skipped", "next_command": "python tools/llm_wiki.py site self-test"}
    return run_generated_site_self_test(root).to_json()


def doctor_status(report: dict[str, object]) -> str:
    readiness = report["readiness"]
    assert isinstance(readiness, dict)
    wiki = report["wiki"]
    assert isinstance(wiki, dict)
    generated = report["generated_project_self_test"]
    assert isinstance(generated, dict)
    if wiki.get("issue_count"):
        return "issues"
    if generated.get("status") == "failed":
        return "issues"
    if not readiness.get("environment_ready"):
        return "issues"
    return "ok"
