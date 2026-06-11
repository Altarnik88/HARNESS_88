from __future__ import annotations

import re
from pathlib import Path

from .db import LintIssue
from .paths import relative_posix


ALLOWED_TASK_STATUSES = {
    "planned",
    "ready",
    "in_progress",
    "blocked",
    "review",
    "verified",
    "done",
}

REQUIRED_HARNESS_FILES = [
    Path("START_HERE.md"),
    Path("STACK.md"),
    Path("PRODUCT.md"),
    Path("DESIGN.md"),
    Path("agents") / "harness" / "README.md",
    Path("agents") / "harness" / "stack-options.md",
    Path("agents") / "harness" / "prd-template.md",
    Path("agents") / "harness" / "spec-template.md",
    Path("agents") / "harness" / "task-template.md",
    Path("agents") / "harness" / "progress-template.md",
    Path("agents") / "harness" / "checkpoint-template.md",
    Path("agents") / "harness" / "acceptance-checklists.md",
    Path("agents") / "harness" / "metrics.md",
    Path("agents") / "tasks" / "README.md",
    Path("agents") / "tasks" / "_template.md",
]

REQUIRED_TASK_SECTIONS = [
    "objective",
    "context files",
    "ownership",
    "allowed tooling",
    "acceptance checklist",
    "verification",
]

STATUS_RE = re.compile(r"^Status:\s*(?P<status>[A-Za-z0-9_-]+)\s*$", re.MULTILINE)
ROLE_OWNER_RE = re.compile(r"^Role owner:\s*(?P<owner>.+?)\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)


def validate_harness(root: Path) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for rel in REQUIRED_HARNESS_FILES:
        if not (root / rel).exists():
            issues.append(LintIssue("warning", rel.as_posix(), f"Missing harness file: {rel.as_posix()}"))

    tasks_dir = root / "agents" / "tasks"
    if not tasks_dir.exists():
        return issues

    for task_path in sorted(tasks_dir.glob("*.md")):
        if task_path.name in {"README.md", "_template.md"}:
            continue
        issues.extend(validate_task_file(root, task_path))
    return issues


def validate_task_file(root: Path, task_path: Path) -> list[LintIssue]:
    rel = relative_posix(task_path, root)
    try:
        text = task_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [LintIssue("warning", rel, f"Cannot read task file: {exc}")]

    issues: list[LintIssue] = []
    if not text.lstrip().startswith("# Task:"):
        issues.append(LintIssue("warning", rel, "Task file must start with '# Task:'."))

    status = task_status(text)
    if status is None:
        issues.append(LintIssue("warning", rel, "Missing task status."))
    elif status not in ALLOWED_TASK_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_TASK_STATUSES))
        issues.append(LintIssue("warning", rel, f"Invalid task status: {status}. Allowed: {allowed}."))

    if ROLE_OWNER_RE.search(text) is None:
        issues.append(LintIssue("warning", rel, "Missing role owner."))

    section_titles = {normalize_heading(match.group("title")) for match in HEADING_RE.finditer(text)}
    for section in REQUIRED_TASK_SECTIONS:
        if section not in section_titles:
            issues.append(LintIssue("warning", rel, f"Missing task section: {section}."))
    if "progress" not in section_titles and "completion evidence" not in section_titles:
        issues.append(LintIssue("warning", rel, "Missing task section: progress or completion evidence."))

    if status in {"verified", "done"} and not has_verification_evidence(text):
        issues.append(LintIssue("warning", rel, "Verified task lacks verification evidence."))

    return issues


def task_status(text: str) -> str | None:
    match = STATUS_RE.search(text)
    return match.group("status").strip() if match else None


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def has_verification_evidence(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.casefold())
    evidence_markers = [
        "verification evidence",
        "verification passed",
        "verification run",
        "tests passed",
    ]
    return any(marker in normalized for marker in evidence_markers)
