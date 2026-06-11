from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .harness import ALLOWED_TASK_STATUSES, ROLE_OWNER_RE, STATUS_RE, validate_harness
from .markdown import slugify
from .paths import relative_posix


TASK_TITLE_RE = re.compile(r"^#\s+Task:\s*(?P<title>.+?)\s*$", re.MULTILINE)
CREATED_RE = re.compile(r"^Created:\s*(?P<created>.+?)\s*$", re.MULTILINE)
OBJECTIVE_RE = re.compile(r"^##\s+Objective\s*$\n(?P<body>.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)


@dataclass(frozen=True)
class TaskRecord:
    path: str
    title: str
    status: str
    role_owner: str
    created: str
    objective: str

    def to_json(self) -> dict[str, str]:
        return {
            "path": self.path,
            "title": self.title,
            "status": self.status,
            "role_owner": self.role_owner,
            "created": self.created,
            "objective": self.objective,
        }


@dataclass(frozen=True)
class TaskCreateResult:
    task: TaskRecord
    progress_path: str
    checkpoint_path: str

    def to_json(self) -> dict[str, object]:
        return {
            "task": self.task.to_json(),
            "progress_path": self.progress_path,
            "checkpoint_path": self.checkpoint_path,
        }


def task_files(root: Path) -> list[Path]:
    tasks_dir = root / "agents" / "tasks"
    if not tasks_dir.exists():
        return []
    return [
        path
        for path in sorted(tasks_dir.glob("*.md"))
        if path.name not in {"README.md", "_template.md"}
    ]


def list_tasks(root: Path, status: str | None = None) -> list[TaskRecord]:
    records = [parse_task_file(root, path) for path in task_files(root)]
    if status is not None:
        records = [record for record in records if record.status == status]
    return records


def next_task(root: Path) -> TaskRecord | None:
    ready = list_tasks(root, status="ready")
    if ready:
        return ready[0]
    planned = list_tasks(root, status="planned")
    return planned[0] if planned else None


def set_task_status(root: Path, raw_path: str, status: str) -> TaskRecord:
    if status not in ALLOWED_TASK_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_TASK_STATUSES))
        raise ValueError(f"Invalid task status: {status}. Allowed: {allowed}.")
    path = resolve_task_path(root, raw_path)
    text = path.read_text(encoding="utf-8")
    if STATUS_RE.search(text) is None:
        raise ValueError(f"Task file has no Status line: {relative_posix(path, root)}")
    updated = STATUS_RE.sub(f"Status: {status}", text, count=1)
    path.write_text(updated, encoding="utf-8")
    return parse_task_file(root, path)


def create_task(
    root: Path,
    title: str,
    objective: str,
    role_owner: str = "Conductor",
    status: str = "planned",
    owned_files: list[str] | None = None,
    do_not_edit: list[str] | None = None,
    verification_command: str = "python tools/llm_wiki.py task validate --strict",
    created: str | None = None,
) -> TaskCreateResult:
    if status not in ALLOWED_TASK_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_TASK_STATUSES))
        raise ValueError(f"Invalid task status: {status}. Allowed: {allowed}.")
    if not title.strip():
        raise ValueError("Task title is required.")
    if not objective.strip():
        raise ValueError("Task objective is required.")

    date = created or datetime.now().strftime("%Y-%m-%d")
    stem = unique_task_stem(root, f"{date}-{slugify(title)}")
    task_rel = Path("agents") / "tasks" / f"{stem}.md"
    progress_rel = Path("agents") / "tasks" / "progress" / f"{stem}.md"
    checkpoint_rel = Path("agents") / "tasks" / "checkpoints" / f"{stem}.md"

    task_path = root / task_rel
    progress_path = root / progress_rel
    checkpoint_path = root / checkpoint_rel
    task_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    task_path.write_text(
        render_task(
            title=title,
            status=status,
            role_owner=role_owner,
            created=date,
            objective=objective,
            owned_files=owned_files or ["none assigned yet"],
            do_not_edit=do_not_edit or ["raw/", "data/wiki.sqlite"],
            verification_command=verification_command,
        ),
        encoding="utf-8",
    )
    progress_path.write_text(render_progress(title, task_rel.as_posix(), status), encoding="utf-8")
    checkpoint_path.write_text(render_checkpoint(title, task_rel.as_posix()), encoding="utf-8")
    return TaskCreateResult(
        task=parse_task_file(root, task_path),
        progress_path=progress_rel.as_posix(),
        checkpoint_path=checkpoint_rel.as_posix(),
    )


def unique_task_stem(root: Path, base: str) -> str:
    tasks_dir = root / "agents" / "tasks"
    candidate = base
    index = 2
    while (tasks_dir / f"{candidate}.md").exists():
        candidate = f"{base}-{index}"
        index += 1
    return candidate


def task_metrics(root: Path) -> dict[str, object]:
    records = list_tasks(root)
    by_status = {status: 0 for status in sorted(ALLOWED_TASK_STATUSES)}
    for record in records:
        by_status[record.status] = by_status.get(record.status, 0) + 1
    closed = by_status.get("done", 0) + by_status.get("verified", 0)
    return {
        "total": len(records),
        "by_status": by_status,
        "open": len(records) - closed,
        "closed": closed,
    }


def readiness_report(root: Path) -> dict[str, object]:
    issues = validate_harness(root)
    pending_decisions: list[str] = []
    if not brief_is_approved(root / "PRODUCT.md"):
        pending_decisions.append("PRODUCT.md")
    if not brief_is_approved(root / "DESIGN.md"):
        pending_decisions.append("DESIGN.md")
    return {
        "environment_ready": not issues,
        "product_design_ready": not pending_decisions,
        "pending_decisions": pending_decisions,
        "harness_issue_count": len(issues),
        "task_metrics": task_metrics(root),
    }


def brief_is_approved(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace").casefold()
    draft_markers = [
        "draft-required-before-implementation",
        "no approved",
        "has not been recorded yet",
    ]
    return not any(marker in text for marker in draft_markers)


def validate_task_queue(root: Path):
    return validate_harness(root)


def parse_task_file(root: Path, path: Path) -> TaskRecord:
    text = path.read_text(encoding="utf-8")
    return TaskRecord(
        path=relative_posix(path, root),
        title=match_or_default(TASK_TITLE_RE, text, "title", path.stem),
        status=match_or_default(STATUS_RE, text, "status", ""),
        role_owner=match_or_default(ROLE_OWNER_RE, text, "owner", ""),
        created=match_or_default(CREATED_RE, text, "created", ""),
        objective=objective_summary(text),
    )


def resolve_task_path(root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    absolute = candidate if candidate.is_absolute() else root / candidate
    resolved_root = root.resolve()
    resolved = absolute.resolve()
    try:
        rel = resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Task path must be inside project root: {raw_path}") from exc
    parts = rel.parts
    if len(parts) != 3 or parts[0] != "agents" or parts[1] != "tasks" or not rel.name.endswith(".md"):
        raise ValueError(f"Task path must be a top-level agents/tasks Markdown file: {raw_path}")
    if rel.name in {"README.md", "_template.md"}:
        raise ValueError(f"Task path must be a concrete task file: {raw_path}")
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    return resolved


def match_or_default(pattern: re.Pattern[str], text: str, group: str, default: str) -> str:
    match = pattern.search(text)
    return match.group(group).strip() if match else default


def objective_summary(text: str) -> str:
    match = OBJECTIVE_RE.search(text)
    if match is None:
        return ""
    paragraphs = [line.strip() for line in match.group("body").splitlines() if line.strip()]
    return " ".join(paragraphs)


def render_task(
    title: str,
    status: str,
    role_owner: str,
    created: str,
    objective: str,
    owned_files: list[str],
    do_not_edit: list[str],
    verification_command: str,
) -> str:
    owned = "\n".join(f"- {item}" for item in owned_files)
    denied = "\n".join(f"- {item}" for item in do_not_edit)
    return f"""# Task: {title}

Status: {status}
Role owner: {role_owner}
Created: {created}

## Objective

{objective}

## Context Files

- AGENTS.md
- agents/tasks/README.md

## Ownership

Owned files:

{owned}

Do not edit:

{denied}

## Allowed Tooling

- Use only tooling granted by agents/tooling-matrix.md and this task file.

## Acceptance Checklist

- Scope is respected.
- Verification command is run.
- Completion evidence is recorded.

## Verification

Command:

```powershell
{verification_command}
```

Expected result:

- exits 0.

## Progress

- No work has started.
"""


def render_progress(title: str, task_path: str, status: str) -> str:
    return f"""# Progress: {title}

Linked task: `{task_path}`
Current status: {status}

## Completed Steps

- No steps have been completed yet.

## Current Blocker

- None recorded.

## Next Action

- Start the assigned task.

## Files Changed

- No files changed yet.

## Verification Run

- No verification run yet.

## Clean-Context Handoff Notes

- Read the linked task, this progress file, and the matching checkpoint before continuing.
"""


def render_checkpoint(title: str, task_path: str) -> str:
    return f"""# Checkpoint: {title}

Linked task: `{task_path}`

## Preflight Checks

- Worktree state checked.
- Owned files and do-not-edit files confirmed.
- Required context reviewed.

## Implementation Evidence

- No implementation evidence recorded yet.

## Verification Evidence

- No verification evidence recorded yet.

## Review Evidence

- No review evidence recorded yet.

## Wiki and Log Updates

- No wiki or log updates recorded yet.

## Residual Risk

- No residual risk recorded yet.
"""
