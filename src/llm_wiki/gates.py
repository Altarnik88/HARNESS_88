from __future__ import annotations

from pathlib import Path

from .status_fields import missing_required_fields as shared_missing_required_fields
from .status_fields import parse_fields as shared_parse_fields
from .status_fields import parse_status, value_is_unknown as shared_value_is_unknown


GATES_PATH = Path("SITE_GATES.md")
ALLOWED_GATE_STATUSES = {"approved", "draft", "needs-review"}
UNKNOWN_VALUES = {"", "unknown", "tbd", "todo", "not selected", "unselected"}

GATE_READY_VALUES = {
    "frontend_preview_approval": {"approved"},
    "backend_data_readiness": {"complete", "not-required"},
    "total_audit": {"complete"},
    "remediation": {"complete", "not-required", "residual-risk-accepted"},
    "final_user_approval": {"approved"},
    "publish_operate_handoff": {"complete"},
}
DELIVERY_GATE_FIELDS = [
    "frontend_preview_approval",
    "backend_data_readiness",
    "total_audit",
    "remediation",
    "final_user_approval",
]
REQUIRED_FIELDS = DELIVERY_GATE_FIELDS + ["publish_operate_handoff"]

def gates_status(root: Path) -> dict[str, object]:
    path = root / GATES_PATH
    if not path.exists():
        return missing_gates_status()

    text = path.read_text(encoding="utf-8", errors="replace")
    status = parse_status(text)
    fields = parse_fields(text)
    missing_fields = missing_required_fields(fields)
    status_approved = status == "approved"
    pending_delivery_gates = pending_gates(fields)
    delivery_gates_ready = status_approved and not missing_fields and delivery_fields_ready(fields)
    publish_ready = delivery_gates_ready and gate_is_ready("publish_operate_handoff", fields)
    blockers = gate_blockers(
        exists=True,
        status=status,
        missing_fields=missing_fields,
        pending_delivery_gates=pending_delivery_gates,
    )

    return {
        "path": GATES_PATH.as_posix(),
        "exists": True,
        "status": status or "missing",
        "approved": status_approved,
        "allowed_statuses": sorted(ALLOWED_GATE_STATUSES),
        "fields": fields,
        "required_fields": REQUIRED_FIELDS,
        "missing_fields": missing_fields,
        "pending_delivery_gates": pending_delivery_gates,
        "delivery_gates_ready": delivery_gates_ready,
        "publish_ready": publish_ready,
        "blockers": blockers,
        "publish_blockers": [] if publish_ready else blockers,
        "message": "SITE_GATES.md is publish-ready." if publish_ready else "SITE_GATES.md has pending delivery gates.",
    }


def missing_gates_status() -> dict[str, object]:
    blockers = gate_blockers(
        exists=False,
        status="missing",
        missing_fields=REQUIRED_FIELDS,
        pending_delivery_gates=[GATES_PATH.as_posix()],
    )
    return {
        "path": GATES_PATH.as_posix(),
        "exists": False,
        "status": "missing",
        "approved": False,
        "allowed_statuses": sorted(ALLOWED_GATE_STATUSES),
        "fields": {},
        "required_fields": REQUIRED_FIELDS,
        "missing_fields": REQUIRED_FIELDS,
        "pending_delivery_gates": [GATES_PATH.as_posix()],
        "delivery_gates_ready": False,
        "publish_ready": False,
        "blockers": blockers,
        "publish_blockers": blockers,
        "message": "SITE_GATES.md is missing.",
    }


def parse_fields(text: str) -> dict[str, str]:
    return shared_parse_fields(text, normalize_values=True)


def missing_required_fields(fields: dict[str, str]) -> list[str]:
    return shared_missing_required_fields(fields, REQUIRED_FIELDS, unknown_values=UNKNOWN_VALUES)


def pending_gates(fields: dict[str, str]) -> list[str]:
    return [field for field in REQUIRED_FIELDS if not gate_is_ready(field, fields)]


def delivery_fields_ready(fields: dict[str, str]) -> bool:
    return all(gate_is_ready(field, fields) for field in DELIVERY_GATE_FIELDS)


def gate_is_ready(field: str, fields: dict[str, str]) -> bool:
    return fields.get(field, "") in GATE_READY_VALUES[field]


def gate_blockers(
    *,
    exists: bool,
    status: str,
    missing_fields: list[str],
    pending_delivery_gates: list[str],
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    if not exists:
        blockers.append(
            {
                "area": "delivery-gates",
                "path": GATES_PATH.as_posix(),
                "message": "SITE_GATES.md is missing.",
                "next_command": "Create SITE_GATES.md from agents/harness/site-gates-template.md.",
            }
        )
    elif status not in ALLOWED_GATE_STATUSES:
        blockers.append(
            {
                "area": "delivery-gates",
                "path": GATES_PATH.as_posix(),
                "message": "SITE_GATES.md must declare Status: draft, approved, or needs-review.",
                "next_command": "Edit SITE_GATES.md and set a valid Status line.",
            }
        )
    elif status != "approved":
        blockers.append(
            {
                "area": "delivery-gates",
                "path": GATES_PATH.as_posix(),
                "message": f"SITE_GATES.md is {status}; set Status: approved after delivery gate evidence is accepted.",
                "next_command": "Edit SITE_GATES.md, then set Status: approved when accepted.",
            }
        )
    if missing_fields:
        blockers.append(
            {
                "area": "delivery-gates",
                "path": GATES_PATH.as_posix(),
                "message": "Missing required delivery gate fields: " + ", ".join(missing_fields) + ".",
                "next_command": "Fill required SITE_GATES.md fields from delivery gate evidence.",
            }
        )
    for field in pending_delivery_gates:
        blockers.append(
            {
                "area": "delivery-gates",
                "path": GATES_PATH.as_posix(),
                "message": f"Delivery gate is not ready: {field}.",
                "next_command": "Update SITE_GATES.md after the gate is complete or explicitly not required.",
            }
        )
    return blockers


def value_is_unknown(value: str) -> bool:
    return shared_value_is_unknown(value, unknown_values=UNKNOWN_VALUES)
