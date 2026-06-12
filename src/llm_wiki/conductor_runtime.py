from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from .tasks import TaskCreateResult, create_task, readiness_report


READ_ORDER = [
    "AGENTS.md",
    "START_HERE.md",
    "STACK.md",
    "agents/TEAM.md",
    "agents/tooling-matrix.md",
    "agents/conductor.md",
    "agents/protocols/conductor-runtime.md",
    "agents/protocols/conversation-delegation.md",
    "agents/workflows/agentic-site-delivery.md",
    "wiki/index.md",
    "wiki/log.md",
]

REQUIRED_CHECKS = [
    "python tools/llm_wiki.py tools audit --json",
    "python tools/llm_wiki.py site intake --json",
    "python tools/llm_wiki.py site references --json",
    "python tools/llm_wiki.py site gates --json",
    "python tools/llm_wiki.py task readiness --json",
]

ALLOWED_LOCAL_ACTIONS = [
    "read state and gates",
    "create delegation packets",
    "create or update task/progress/checkpoint files",
    "run verification commands",
    "review worker output",
    "write final integration summaries",
]

FORBIDDEN_LOCAL_ACTIONS = [
    "self-assign worker phases",
    "perform reference research as Conductor",
    "build frontend/backend production code as Conductor",
    "mark gates approved without worker evidence and explicit user approval",
]


ROUTES: dict[str, dict[str, object]] = {
    "reference-analysis": {
        "phase": "reference-analysis",
        "lead_roles": [
            "Reference Research",
            "UX/Product Design",
            "Visual Design",
            "Design Artifact",
            "QA & Accessibility",
        ],
        "supporting_roles": ["Conductor"],
        "requires_delegation": True,
        "required_context": [
            "AGENTS.md",
            "SITE_INTAKE.md",
            "SITE_REFERENCES.md",
            "agents/TEAM.md",
            "agents/protocols/conductor-runtime.md",
            "agents/protocols/conversation-delegation.md",
            "agents/protocols/design-resources.md",
            "agents/tooling-matrix.md",
            "agents/workflows/agentic-site-delivery.md",
            "agents/roles/reference-research.md",
            "agents/roles/ux-product-design.md",
            "agents/roles/visual-design.md",
            "agents/roles/design-artifact.md",
            "agents/roles/qa-accessibility.md",
        ],
        "denied_scope": [
            "checkout/cart flows unless explicitly approved",
            "private/login/account/admin pages",
            "form-submission or destructive flows",
            "production frontend implementation",
            "credential or secret collection",
        ],
        "verification": "python tools/llm_wiki.py site references --json",
    },
    "frontend-build": {
        "phase": "frontend-build",
        "lead_roles": ["Frontend Implementation"],
        "supporting_roles": ["UX/Product Design", "Visual Design", "QA & Accessibility"],
        "requires_delegation": True,
        "required_context": [
            "PRODUCT.md",
            "DESIGN.md",
            "STACK.md",
            "SITE_INTAKE.md",
            "SITE_REFERENCES.md",
            "agents/workflows/agentic-site-delivery.md",
        ],
        "denied_scope": ["backend/data mutations", "publish/deploy actions", "unapproved reference or design changes"],
        "verification": "python tools/llm_wiki.py quality",
    },
    "backend-data": {
        "phase": "backend-data",
        "lead_roles": ["Backend/Data"],
        "supporting_roles": ["DevOps/Release"],
        "requires_delegation": True,
        "required_context": [
            "PRODUCT.md",
            "STACK.md",
            "SITE_INTAKE.md",
            "agents/workflows/secret-broker.md",
            "agents/workflows/agentic-site-delivery.md",
        ],
        "denied_scope": ["secret values in files or chat", "database mutations without explicit delegation"],
        "verification": "python tools/llm_wiki.py quality",
    },
}


@dataclass(frozen=True)
class ConductorDelegateResult:
    task_result: TaskCreateResult
    delegation_packet: str

    def to_json(self) -> dict[str, object]:
        payload = self.task_result.to_json()
        payload["delegation_packet"] = self.delegation_packet
        task = payload["task"]
        assert isinstance(task, dict)
        task["delegation_packet"] = self.delegation_packet
        return payload


def start_packet(root: Path) -> dict[str, object]:
    readiness = readiness_report(root)
    next_actions = [
        "Say 'Conductor online' in the main chat before site work.",
        "Read gates and blockers before delegating worker phases.",
        "Use conductor route/delegate before reference, design, frontend, backend, QA, release, or wiki closeout work.",
    ]
    suggested = readiness.get("suggested_tasks", [])
    if isinstance(suggested, list):
        next_actions.extend(str(item.get("title", item)) for item in suggested if isinstance(item, dict))
    return {
        "mode": "conductor",
        "chat_banner": "Conductor online. I will coordinate HARNESS_88 through gated delegation packets before worker phases.",
        "allowed_local_actions": ALLOWED_LOCAL_ACTIONS,
        "forbidden_local_actions": FORBIDDEN_LOCAL_ACTIONS,
        "read_order": READ_ORDER,
        "required_checks": REQUIRED_CHECKS,
        "readiness": readiness,
        "next_actions": next_actions,
    }


def route_packet(phase: str) -> dict[str, object]:
    if phase not in ROUTES:
        allowed = ", ".join(sorted(ROUTES))
        raise ValueError(f"Unknown conductor phase: {phase}. Allowed: {allowed}.")
    return dict(ROUTES[phase])


def delegate(
    root: Path,
    *,
    phase: str,
    title: str,
    objective: str,
    owner: str,
    user_language: str,
    owned_files: list[str],
    do_not_edit: list[str],
    verification_command: str,
    created: str | None = None,
) -> ConductorDelegateResult:
    route = route_packet(phase)
    task_result = create_task(
        root,
        title=title,
        objective=objective,
        role_owner=owner,
        status="planned",
        owned_files=owned_files,
        do_not_edit=do_not_edit,
        verification_command=verification_command,
        created=created,
        phase=phase,
        delegation_packet="",
    )
    stem = Path(task_result.task.path).stem
    packet_rel = Path("agents") / "delegations" / f"{stem}.md"
    packet_path = root / packet_rel
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(
        render_delegation_packet(
            route=route,
            role=owner,
            task_path=task_result.task.path,
            progress_path=task_result.progress_path,
            checkpoint_path=task_result.checkpoint_path,
            objective=objective,
            user_language=user_language,
            owned_files=owned_files,
            do_not_edit=do_not_edit,
            verification_command=verification_command,
        ),
        encoding="utf-8",
    )
    task_path = root / task_result.task.path
    text = task_path.read_text(encoding="utf-8")
    text = text.replace("Delegation packet: pending", f"Delegation packet: {packet_rel.as_posix()}", 1)
    task_path.write_text(text, encoding="utf-8")
    updated_task = task_result.task.__class__(
        path=task_result.task.path,
        title=task_result.task.title,
        status=task_result.task.status,
        role_owner=task_result.task.role_owner,
        created=task_result.task.created,
        objective=task_result.task.objective,
        phase=phase,
        delegation_packet=packet_rel.as_posix(),
    )
    return ConductorDelegateResult(
        task_result=TaskCreateResult(
            task=updated_task,
            progress_path=task_result.progress_path,
            checkpoint_path=task_result.checkpoint_path,
        ),
        delegation_packet=packet_rel.as_posix(),
    )


def render_delegation_packet(
    *,
    route: dict[str, object],
    role: str,
    task_path: str,
    progress_path: str,
    checkpoint_path: str,
    objective: str,
    user_language: str,
    owned_files: list[str],
    do_not_edit: list[str],
    verification_command: str,
) -> str:
    owned = "\n".join(f"- {item}" for item in owned_files) or "- none; read-only"
    denied = "\n".join(f"- {item}" for item in do_not_edit) or "- raw/\n- data/wiki.sqlite"
    context = "\n".join(f"- {item}" for item in route["required_context"])
    denied_scope = "\n".join(f"- {item}" for item in route["denied_scope"])
    return f"""# Delegation Packet: {Path(task_path).stem}

Role: {role}
Sub-agent: {role} worker
Phase: {route["phase"]}

Task file: {task_path}
Progress file: {progress_path}
Checkpoint file: {checkpoint_path}

Objective:
{objective}

Context to read:
{context}

User language:
{user_language}

Reference/source scope:
{denied_scope}

Ownership / scope:
Owned files:
{owned}

Do not edit:
{denied}

Required plugins/MCP/skills:
- Use only tools granted in agents/tooling-matrix.md for {role}.
- Default deny: all unlisted skills, plugins, MCP servers, and write scopes are forbidden.

Code permission:
assigned files only

Expected output:
- Complete the delegated {route["phase"]} work with evidence in the task, progress, checkpoint, and referenced artifacts.

Verification:
{verification_command}

Clean-context resume instructions:
- Read the task, progress, checkpoint, this packet, and linked product/design decisions before continuing.
- Update progress and checkpoint files before reporting completion.
"""


def cmd_conductor(args: argparse.Namespace, root: Path) -> int:
    if args.conductor_command == "start":
        payload = start_packet(root)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_start_packet(payload)
        return 0
    if args.conductor_command == "route":
        try:
            payload = route_packet(args.phase)
        except ValueError as exc:
            print(str(exc))
            return 2
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_route_packet(payload)
        return 0
    if args.conductor_command == "delegate":
        try:
            result = delegate(
                root,
                phase=args.phase,
                title=args.title,
                objective=args.objective,
                owner=args.owner,
                user_language=args.user_language,
                owned_files=args.owned or [],
                do_not_edit=args.do_not_edit or [],
                verification_command=args.verification,
                created=args.created or None,
            )
        except ValueError as exc:
            print(str(exc))
            return 2
        if args.json:
            print(json.dumps(result.to_json(), ensure_ascii=False, indent=2))
        else:
            print(f"Created {result.task_result.task.path}")
            print(f"Progress: {result.task_result.progress_path}")
            print(f"Checkpoint: {result.task_result.checkpoint_path}")
            print(f"Delegation packet: {result.delegation_packet}")
        return 0
    raise ValueError(f"Unknown conductor command: {args.conductor_command}")


def print_start_packet(payload: dict[str, object]) -> None:
    print(payload["chat_banner"])
    print("Mode: conductor")
    print("Allowed local actions:")
    for item in payload["allowed_local_actions"]:
        print(f"- {item}")
    print("Forbidden local actions:")
    for item in payload["forbidden_local_actions"]:
        print(f"- {item}")
    print("Next actions:")
    for item in payload["next_actions"]:
        print(f"- {item}")


def print_route_packet(payload: dict[str, object]) -> None:
    print(f"Phase: {payload['phase']}")
    print(f"Requires delegation: {'yes' if payload['requires_delegation'] else 'no'}")
    print("Lead roles:")
    for role in payload["lead_roles"]:
        print(f"- {role}")
    print("Denied scope:")
    for item in payload["denied_scope"]:
        print(f"- {item}")
    print(f"Verification: {payload['verification']}")
