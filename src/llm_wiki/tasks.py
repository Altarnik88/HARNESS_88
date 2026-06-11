from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .harness import ALLOWED_TASK_STATUSES, ROLE_OWNER_RE, STATUS_RE, validate_harness
from .intake import intake_status
from .markdown import slugify
from .paths import relative_posix
from .stack import stack_is_selected


TASK_TITLE_RE = re.compile(r"^#\s+Task:\s*(?P<title>.+?)\s*$", re.MULTILINE)
CREATED_RE = re.compile(r"^Created:\s*(?P<created>.+?)\s*$", re.MULTILINE)
OBJECTIVE_RE = re.compile(r"^##\s+Objective\s*$\n(?P<body>.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
BRIEF_STATUS_RE = re.compile(r"^Status:\s*(?P<status>[A-Za-z0-9_-]+)\s*$", re.MULTILINE)
ALLOWED_BRIEF_STATUSES = {"draft", "approved", "needs-review"}

ALLOWED_STATUS_TRANSITIONS = {
    "planned": {"ready", "blocked"},
    "ready": {"in_progress", "blocked"},
    "in_progress": {"review", "blocked"},
    "blocked": {"planned", "ready", "in_progress"},
    "review": {"in_progress", "verified", "blocked"},
    "verified": {"done", "in_progress"},
    "done": set(),
}


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


def set_task_status(root: Path, raw_path: str, status: str, force: bool = False) -> TaskRecord:
    if status not in ALLOWED_TASK_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_TASK_STATUSES))
        raise ValueError(f"Invalid task status: {status}. Allowed: {allowed}.")
    path = resolve_task_path(root, raw_path)
    text = path.read_text(encoding="utf-8")
    match = STATUS_RE.search(text)
    if match is None:
        raise ValueError(f"Task file has no Status line: {relative_posix(path, root)}")
    current = match.group("status").strip()
    if current not in ALLOWED_TASK_STATUSES:
        raise ValueError(f"Cannot transition from invalid task status: {current}. Use --force after repair.")
    allowed_next = ALLOWED_STATUS_TRANSITIONS.get(current, set())
    if not force and status != current and status not in allowed_next:
        allowed_text = ", ".join(sorted(allowed_next)) or "none"
        raise ValueError(
            f"Invalid task status transition: {current} -> {status}. "
            f"Allowed next statuses: {allowed_text}. Use --force for queue repair."
        )
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
    product_design_pending: list[str] = []
    briefs = {
        "PRODUCT.md": brief_status(root / "PRODUCT.md"),
        "DESIGN.md": brief_status(root / "DESIGN.md"),
    }
    for name, status in briefs.items():
        if not status["approved"]:
            product_design_pending.append(name)
    pending_decisions.extend(product_design_pending)
    stack_ready = stack_is_selected(root)
    if not stack_ready:
        pending_decisions.append("STACK.md")
    intake = intake_status(root)
    intake_ready = bool(intake["intake_ready"])
    references_ready = bool(intake["references_ready"])
    if not intake_ready:
        pending_decisions.append("SITE_INTAKE.md")
    if not references_ready:
        pending_decisions.append("references")
    blockers = readiness_blockers(root, issues, briefs, stack_ready, intake)
    files_to_edit = sorted({blocker["path"] for blocker in blockers if blocker.get("path")})
    core_development_ready = not issues
    site_implementation_ready = not pending_decisions
    return {
        "environment_ready": core_development_ready,
        "core_development_ready": core_development_ready,
        "product_design_ready": not product_design_pending,
        "stack_ready": stack_ready,
        "intake_ready": intake_ready,
        "references_ready": references_ready,
        "site_implementation_ready": site_implementation_ready,
        "implementation_ready": site_implementation_ready,
        "pending_decisions": pending_decisions,
        "harness_issue_count": len(issues),
        "task_metrics": task_metrics(root),
        "briefs": briefs,
        "intake": intake,
        "blockers": blockers,
        "files_to_edit": files_to_edit,
        "next_command": next_readiness_command(blockers),
        "suggested_tasks": suggested_readiness_tasks(pending_decisions),
    }


def brief_is_approved(path: Path) -> bool:
    return bool(brief_status(path)["approved"])


def brief_status(path: Path) -> dict[str, object]:
    rel = path.name
    if not path.exists():
        return {
            "path": rel,
            "exists": False,
            "status": "missing",
            "approved": False,
            "allowed_statuses": sorted(ALLOWED_BRIEF_STATUSES),
            "message": f"{rel} is missing.",
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    match = BRIEF_STATUS_RE.search(text)
    if match is None:
        return {
            "path": rel,
            "exists": True,
            "status": "missing",
            "approved": False,
            "allowed_statuses": sorted(ALLOWED_BRIEF_STATUSES),
            "message": f"{rel} must declare Status: draft, approved, or needs-review.",
        }
    status = match.group("status").strip().casefold()
    if status not in ALLOWED_BRIEF_STATUSES:
        return {
            "path": rel,
            "exists": True,
            "status": status,
            "approved": False,
            "allowed_statuses": sorted(ALLOWED_BRIEF_STATUSES),
            "message": f"{rel} has invalid status '{status}'. Use draft, approved, or needs-review.",
        }
    return {
        "path": rel,
        "exists": True,
        "status": status,
        "approved": status == "approved",
        "allowed_statuses": sorted(ALLOWED_BRIEF_STATUSES),
        "message": f"{rel} is approved." if status == "approved" else f"{rel} is {status}; set Status: approved after decisions are accepted.",
    }


def readiness_blockers(
    root: Path,
    issues,
    briefs: dict[str, dict[str, object]],
    stack_ready: bool,
    intake: dict[str, object],
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    for issue in issues:
        blockers.append(
            {
                "area": "harness",
                "path": issue.path,
                "message": issue.message,
                "next_command": "python tools/llm_wiki.py task validate --strict",
            }
        )
    for name, status in briefs.items():
        if not status["approved"]:
            blockers.append(
                {
                    "area": "brief",
                    "path": name,
                    "message": str(status["message"]),
                    "next_command": f"Edit {name}, then set Status: approved when accepted.",
                }
            )
    if not stack_ready:
        blockers.append(
            {
                "area": "stack",
                "path": "STACK.md",
                "message": "Stack profile is not selected.",
                "next_command": "python tools/llm_wiki.py stack list",
            }
        )
    for blocker in intake.get("blockers", []):
        assert isinstance(blocker, dict)
        blockers.append({key: str(value) for key, value in blocker.items()})
    if not list_tasks(root):
        blockers.append(
            {
                "area": "task",
                "path": "agents/tasks/",
                "message": "No concrete task file exists yet.",
                "next_command": 'python tools/llm_wiki.py task create --title "First Implementation Slice" --objective "Build the first approved site slice."',
            }
        )
    return blockers


def next_readiness_command(blockers: list[dict[str, str]]) -> str:
    return blockers[0]["next_command"] if blockers else "python tools/llm_wiki.py quality --skip-frontend"


def suggested_readiness_tasks(pending_decisions: list[str]) -> list[dict[str, str]]:
    suggestions: list[dict[str, str]] = []
    if "PRODUCT.md" in pending_decisions:
        suggestions.append(
            {
                "title": "Approve Product Brief",
                "objective": "Capture the product goal, audience, scope, and acceptance criteria, then set PRODUCT.md to Status: approved.",
            }
        )
    if "DESIGN.md" in pending_decisions:
        suggestions.append(
            {
                "title": "Approve Design Brief",
                "objective": "Capture visual direction, UX constraints, accessibility, and component rules, then set DESIGN.md to Status: approved.",
            }
        )
    if "STACK.md" in pending_decisions:
        suggestions.append(
            {
                "title": "Select Stack Profile",
                "objective": "Choose a stack/fullstack profile and record it with python tools/llm_wiki.py stack select <profile>.",
            }
        )
    if "SITE_INTAKE.md" in pending_decisions:
        suggestions.append(
            {
                "title": "Approve Site Intake",
                "objective": "Capture the first-run site intake in SITE_INTAKE.md and set Status: approved after decisions are accepted.",
            }
        )
    if "references" in pending_decisions:
        suggestions.append(
            {
                "title": "Approve Site References",
                "objective": "Record user-provided or agent-suggested references and set references_status: approved in SITE_INTAKE.md.",
            }
        )
    return suggestions


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
