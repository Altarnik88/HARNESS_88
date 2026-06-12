from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from .harness import WORKER_PHASES
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


COMMON_CONTEXT = [
    "AGENTS.md",
    "agents/TEAM.md",
    "agents/protocols/conductor-runtime.md",
    "agents/protocols/conversation-delegation.md",
    "agents/tooling-matrix.md",
    "agents/workflows/agentic-site-delivery.md",
]

COMMON_DENIED_SCOPE = [
    "secret values in files or chat",
    "unapproved gate-status changes",
    "unassigned production implementation",
]

ROUTES: dict[str, dict[str, object]] = {
    "first-run-intake": {
        "phase": "first-run-intake",
        "lead_roles": ["Product Strategist"],
        "supporting_roles": ["Conductor"],
        "requires_delegation": True,
        "required_context": [
            "START_HERE.md",
            "SITE_INTAKE.md",
            "PRODUCT.md",
            "DESIGN.md",
            "STACK.md",
            *COMMON_CONTEXT,
            "agents/roles/product-strategist.md",
        ],
        "source_scope": [
            "user-provided answers and existing project decisions",
            "no external research unless separately delegated",
        ],
        "denied_scope": [
            "site implementation",
            "stack selection without explicit user approval",
            "reference approval without user approval",
            *COMMON_DENIED_SCOPE,
        ],
        "code_permission": "docs-only",
        "verification": "python tools/llm_wiki.py site intake --json",
    },
    "brief-contracts": {
        "phase": "brief-contracts",
        "lead_roles": ["Product Strategist"],
        "supporting_roles": ["UX/Product Design", "Frontend Architecture", "Conductor"],
        "requires_delegation": True,
        "required_context": [
            "SITE_INTAKE.md",
            "PRODUCT.md",
            "DESIGN.md",
            "STACK.md",
            *COMMON_CONTEXT,
            "agents/roles/product-strategist.md",
            "agents/roles/ux-product-design.md",
            "agents/roles/frontend-architecture.md",
        ],
        "source_scope": [
            "approved intake answers and recorded product/design decisions",
            "current stack profiles only through HARNESS_88 stack files",
        ],
        "denied_scope": [
            "site implementation",
            "reference-analysis evidence fabrication",
            *COMMON_DENIED_SCOPE,
        ],
        "code_permission": "docs-only",
        "verification": "python tools/llm_wiki.py task readiness --json",
    },
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
            "SITE_INTAKE.md",
            "SITE_REFERENCES.md",
            *COMMON_CONTEXT,
            "agents/protocols/design-resources.md",
            "agents/roles/reference-research.md",
            "agents/roles/ux-product-design.md",
            "agents/roles/visual-design.md",
            "agents/roles/design-artifact.md",
            "agents/roles/qa-accessibility.md",
        ],
        "source_scope": [
            "approved reference URLs and required discovery sources",
            "https://dribbble.com/",
            "https://www.behance.net/",
            "https://www.awwwards.com/",
            "bounded same-origin public pages only",
        ],
        "denied_scope": [
            "checkout/cart flows unless explicitly approved",
            "private/login/account/admin pages",
            "form-submission or destructive flows",
            "production frontend implementation",
            "credential or secret collection",
        ],
        "code_permission": "docs-only",
        "verification": "python tools/llm_wiki.py site references --json",
    },
    "sitemap-content": {
        "phase": "sitemap-content",
        "lead_roles": ["IA & Content"],
        "supporting_roles": ["Product Strategist", "UX/Product Design", "Conductor"],
        "requires_delegation": True,
        "required_context": [
            "PRODUCT.md",
            "DESIGN.md",
            "SITE_INTAKE.md",
            "SITE_REFERENCES.md",
            *COMMON_CONTEXT,
            "agents/roles/ia-content.md",
        ],
        "source_scope": ["approved product/design/reference decisions and provided content sources"],
        "denied_scope": ["frontend/backend production implementation", *COMMON_DENIED_SCOPE],
        "code_permission": "docs-only",
        "verification": "python tools/llm_wiki.py task validate --strict",
    },
    "frontend-architecture": {
        "phase": "frontend-architecture",
        "lead_roles": ["Frontend Architecture"],
        "supporting_roles": ["UX/Product Design", "Visual Design", "Conductor"],
        "requires_delegation": True,
        "required_context": [
            "PRODUCT.md",
            "DESIGN.md",
            "STACK.md",
            "SITE_INTAKE.md",
            "SITE_REFERENCES.md",
            *COMMON_CONTEXT,
            "agents/roles/frontend-architecture.md",
        ],
        "source_scope": ["approved stack, briefs, references, and task ownership only"],
        "denied_scope": ["production page/component implementation", "backend/data mutations", *COMMON_DENIED_SCOPE],
        "code_permission": "docs/config only if delegated",
        "verification": "python tools/llm_wiki.py task validate --strict",
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
            *COMMON_CONTEXT,
            "agents/roles/frontend-implementation.md",
        ],
        "source_scope": ["approved briefs, selected stack, reference evidence, and assigned task files"],
        "denied_scope": ["backend/data mutations", "publish/deploy actions", "unapproved reference or design changes"],
        "code_permission": "assigned files only",
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
            *COMMON_CONTEXT,
            "agents/workflows/secret-broker.md",
            "agents/roles/backend-data.md",
        ],
        "source_scope": ["approved backend/data/auth/admin/integration decisions and assigned task files"],
        "denied_scope": ["secret values in files or chat", "database mutations without explicit delegation"],
        "code_permission": "assigned files only",
        "verification": "python tools/llm_wiki.py quality",
    },
    "catalog-ingest": {
        "phase": "catalog-ingest",
        "lead_roles": ["Backend/Data"],
        "supporting_roles": ["IA & Content", "Frontend Implementation", "Conductor"],
        "requires_delegation": True,
        "required_context": [
            "PRODUCT.md",
            "SITE_INTAKE.md",
            "STACK.md",
            *COMMON_CONTEXT,
            "agents/roles/backend-data.md",
            "agents/roles/ia-content.md",
        ],
        "source_scope": ["user-approved product/catalog documents and assigned data-mapping files"],
        "denied_scope": ["raw/ mutation without explicit ingest approval", "secret values", *COMMON_DENIED_SCOPE],
        "code_permission": "assigned files only",
        "verification": "python tools/llm_wiki.py task validate --strict",
    },
    "total-audit": {
        "phase": "total-audit",
        "lead_roles": ["QA & Accessibility", "Performance/SEO", "Backend/Data", "DevOps/Release"],
        "supporting_roles": ["Conductor"],
        "requires_delegation": True,
        "required_context": [
            "SITE_GATES.md",
            "PRODUCT.md",
            "DESIGN.md",
            "STACK.md",
            *COMMON_CONTEXT,
            "agents/roles/qa-accessibility.md",
            "agents/roles/performance-seo.md",
            "agents/roles/backend-data.md",
            "agents/roles/devops-release.md",
        ],
        "source_scope": ["local preview, assigned implementation evidence, and approved task artifacts"],
        "denied_scope": ["external writes", "secret collection", "release/publish actions", *COMMON_DENIED_SCOPE],
        "code_permission": "test files only if delegated",
        "verification": "python tools/llm_wiki.py site gates --json",
    },
    "remediation": {
        "phase": "remediation",
        "lead_roles": [
            "Frontend Implementation",
            "Backend/Data",
            "QA & Accessibility",
            "Performance/SEO",
            "DevOps/Release",
        ],
        "supporting_roles": ["Conductor"],
        "requires_delegation": True,
        "required_context": [
            "SITE_GATES.md",
            *COMMON_CONTEXT,
            "agents/roles/frontend-implementation.md",
            "agents/roles/backend-data.md",
            "agents/roles/qa-accessibility.md",
            "agents/roles/performance-seo.md",
            "agents/roles/devops-release.md",
        ],
        "source_scope": ["recorded audit findings and assigned remediation task files"],
        "denied_scope": ["unassigned files", "unapproved residual-risk closure", *COMMON_DENIED_SCOPE],
        "code_permission": "assigned files only",
        "verification": "python tools/llm_wiki.py site gates --json",
    },
    "final-approval": {
        "phase": "final-approval",
        "lead_roles": ["Frontend Implementation", "QA & Accessibility", "UX/Product Design"],
        "supporting_roles": ["Conductor"],
        "requires_delegation": True,
        "required_context": [
            "SITE_GATES.md",
            "PRODUCT.md",
            "DESIGN.md",
            *COMMON_CONTEXT,
            "agents/roles/frontend-implementation.md",
            "agents/roles/qa-accessibility.md",
            "agents/roles/ux-product-design.md",
        ],
        "source_scope": ["local final preview, user feedback, and assigned verification artifacts"],
        "denied_scope": ["treating silence as approval", "publish instructions before approval", *COMMON_DENIED_SCOPE],
        "code_permission": "assigned files only",
        "verification": "python tools/llm_wiki.py site gates --json",
    },
    "publish-operate": {
        "phase": "publish-operate",
        "lead_roles": ["DevOps/Release"],
        "supporting_roles": ["Conductor"],
        "requires_delegation": True,
        "required_context": [
            "SITE_GATES.md",
            "STACK.md",
            *COMMON_CONTEXT,
            "agents/workflows/secret-broker.md",
            "agents/roles/devops-release.md",
        ],
        "source_scope": ["approved deployment target, selected stack, and non-secret environment variable names"],
        "denied_scope": ["secret values", "production publish without explicit approval", "GitHub/release writes unless requested"],
        "code_permission": "infra/config/docs only if delegated",
        "verification": "python tools/llm_wiki.py site gates --json",
    },
    "knowledge-closeout": {
        "phase": "knowledge-closeout",
        "lead_roles": ["Knowledge Steward"],
        "supporting_roles": ["Conductor"],
        "requires_delegation": True,
        "required_context": [
            "wiki/index.md",
            "wiki/log.md",
            *COMMON_CONTEXT,
            "agents/roles/knowledge-steward.md",
        ],
        "source_scope": ["durable approved decisions, completed task evidence, and unresolved follow-ups"],
        "denied_scope": ["large narrative logs", "generated SQLite mutation", "temporary audit noise"],
        "code_permission": "wiki/docs only",
        "verification": "python tools/llm_wiki.py lint --strict",
    },
}

assert set(ROUTES) == WORKER_PHASES


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
    verification_command: str | None,
    created: str | None = None,
) -> ConductorDelegateResult:
    route = route_packet(phase)
    owner = owner.strip()
    if not owner:
        raise ValueError("Delegated worker phase requires a non-empty role owner.")
    if owner.casefold() == "conductor":
        raise ValueError(f"Worker phase {phase} cannot be owned by Conductor. Use a role agent or declared fallback.")
    allowed_owners = {
        str(role)
        for role in [*route.get("lead_roles", []), *route.get("supporting_roles", [])]
        if str(role).casefold() != "conductor"
    }
    if owner not in allowed_owners:
        allowed = ", ".join(sorted(allowed_owners))
        raise ValueError(f"Invalid owner for phase {phase}: {owner}. Allowed: {allowed}.")
    verification = (verification_command or str(route["verification"])).strip()
    task_result = create_task(
        root,
        title=title,
        objective=objective,
        role_owner=owner,
        status="planned",
        owned_files=owned_files,
        do_not_edit=do_not_edit,
        verification_command=verification,
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
            verification_command=verification,
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
    source_scope = "\n".join(f"- {item}" for item in route.get("source_scope", [])) or "- not applicable"
    denied_scope = "\n".join(f"- {item}" for item in route["denied_scope"])
    code_permission = str(route.get("code_permission", "assigned files only"))
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
{source_scope}

Denied scope:
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
{code_permission}

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
                verification_command=args.verification or None,
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
