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
    Path("SITE_GATES.md"),
    Path("SITE_INTAKE.md"),
    Path("STACK.md"),
    Path("PRODUCT.md"),
    Path("DESIGN.md"),
    Path("agents") / "harness" / "README.md",
    Path("agents") / "harness" / "site-gates-template.md",
    Path("agents") / "harness" / "site-intake-template.md",
    Path("agents") / "harness" / "stack-options.md",
    Path("agents") / "harness" / "prd-template.md",
    Path("agents") / "harness" / "spec-template.md",
    Path("agents") / "harness" / "task-template.md",
    Path("agents") / "harness" / "progress-template.md",
    Path("agents") / "harness" / "checkpoint-template.md",
    Path("agents") / "harness" / "acceptance-checklists.md",
    Path("agents") / "harness" / "metrics.md",
    Path("agents") / "resources" / "tooling-sources.json",
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
OWNED_FILES_BLOCK_RE = re.compile(r"Owned files:\s*\n(?P<body>.*?)(?=\n\S|^##\s+|\Z)", re.MULTILINE | re.DOTALL)
INLINE_OWNED_FILES_RE = re.compile(r"^\s*-\s*Owned files:\s*(?P<value>.+?)\s*$", re.MULTILINE)
OPEN_TASK_STATUSES = {"planned", "ready", "in_progress", "blocked", "review"}


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
    issues.extend(validate_owned_file_conflicts(root, sorted(tasks_dir.glob("*.md"))))
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

    issues.extend(validate_linked_support_files(root, task_path))
    return issues


def validate_linked_support_files(root: Path, task_path: Path) -> list[LintIssue]:
    rel = relative_posix(task_path, root)
    task_rel = relative_posix(task_path, root)
    stem = task_path.stem
    issues: list[LintIssue] = []
    for label, support_path in [
        ("progress", root / "agents" / "tasks" / "progress" / f"{stem}.md"),
        ("checkpoint", root / "agents" / "tasks" / "checkpoints" / f"{stem}.md"),
    ]:
        if not support_path.exists():
            issues.append(LintIssue("warning", rel, f"Missing linked {label} file: {relative_posix(support_path, root)}"))
            continue
        try:
            support_text = support_path.read_text(encoding="utf-8")
        except OSError as exc:
            issues.append(LintIssue("warning", relative_posix(support_path, root), f"Cannot read linked {label} file: {exc}"))
            continue
        if task_rel not in support_text:
            issues.append(
                LintIssue(
                    "warning",
                    relative_posix(support_path, root),
                    f"Linked {label} file must reference task: {task_rel}",
                )
            )
    return issues


def validate_owned_file_conflicts(root: Path, task_paths: list[Path]) -> list[LintIssue]:
    ownership: list[tuple[Path, str]] = []
    for task_path in task_paths:
        if task_path.name in {"README.md", "_template.md"}:
            continue
        try:
            text = task_path.read_text(encoding="utf-8")
        except OSError:
            continue
        status = task_status(text)
        if status not in OPEN_TASK_STATUSES:
            continue
        for owned in owned_files(text):
            ownership.append((task_path, owned))

    issues: list[LintIssue] = []
    for index, (left_path, left_owned) in enumerate(ownership):
        for right_path, right_owned in ownership[index + 1 :]:
            if left_path == right_path:
                continue
            if paths_overlap(left_owned, right_owned):
                issues.append(
                    LintIssue(
                        "warning",
                        relative_posix(right_path, root),
                        "Owned file conflict: "
                        f"{right_owned} overlaps {left_owned} in {relative_posix(left_path, root)}.",
                    )
                )
    return issues


def owned_files(text: str) -> list[str]:
    values: list[str] = []
    block_match = OWNED_FILES_BLOCK_RE.search(text)
    if block_match is not None:
        for line in block_match.group("body").splitlines():
            stripped = line.strip()
            if stripped.startswith("-"):
                values.extend(split_owned_value(stripped[1:].strip()))
    for match in INLINE_OWNED_FILES_RE.finditer(text):
        values.extend(split_owned_value(match.group("value")))
    return [value for value in values if is_concrete_owned_file(value)]


def split_owned_value(value: str) -> list[str]:
    return [item.strip().strip("`") for item in value.split(",") if item.strip()]


def is_concrete_owned_file(value: str) -> bool:
    lowered = value.casefold()
    if lowered in {"none", "none assigned yet", "n/a"}:
        return False
    if lowered.startswith("no "):
        return False
    return True


def paths_overlap(left: str, right: str) -> bool:
    left_norm = normalize_owned_path(left)
    right_norm = normalize_owned_path(right)
    return left_norm == right_norm or left_norm.startswith(right_norm + "/") or right_norm.startswith(left_norm + "/")


def normalize_owned_path(value: str) -> str:
    normalized = value.replace("\\", "/").strip().strip("/")
    return re.sub(r"/+", "/", normalized)


def task_status(text: str) -> str | None:
    match = STATUS_RE.search(text)
    return match.group("status").strip() if match else None


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def has_verification_evidence(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.casefold())
    if "no verification run yet" in normalized or "no verification evidence recorded yet" in normalized:
        return False
    has_evidence_label = "verification evidence" in normalized or "verification run" in normalized
    has_command = re.search(r"\b(python|npm|pytest|unittest|node|npx|pnpm|yarn|git)\b", normalized) is not None
    has_success = re.search(r"\b(exited 0|exit 0|passes|passed|no .*issues|0 failures|ok)\b", normalized) is not None
    return has_evidence_label and has_command and has_success
