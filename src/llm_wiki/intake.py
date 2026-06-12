from __future__ import annotations

from pathlib import Path

from .status_fields import missing_required_fields as shared_missing_required_fields
from .status_fields import normalize, parse_fields, parse_status, value_is_unknown as shared_value_is_unknown


INTAKE_PATH = Path("SITE_INTAKE.md")
ALLOWED_INTAKE_STATUSES = {"approved", "draft", "needs-review"}
READY_REFERENCE_STATUSES = {"approved"}
UNKNOWN_VALUES = {"", "unknown", "tbd", "todo", "not selected", "unselected"}
CATALOG_SITE_TYPES = {"catalog", "ecommerce"}
NO_CATALOG_MODES = {"none", "no", "no-commerce", "not-required"}
PRODUCT_DOCUMENT_READY_VALUES = {"needed", "provided"}

REQUIRED_FIELDS = [
    "goal",
    "audience",
    "country",
    "language",
    "site_type",
    "catalog_mode",
    "payment_request_mode",
    "design_style",
    "reference_mode",
    "references_status",
    "content_sources",
    "stack_expectations",
    "deploy_expectations",
    "backend",
    "data",
    "auth",
    "admin",
    "integrations",
    "product_catalog_document",
]

def intake_status(root: Path) -> dict[str, object]:
    path = root / INTAKE_PATH
    if not path.exists():
        return missing_intake_status()

    text = path.read_text(encoding="utf-8", errors="replace")
    status = parse_status(text)
    fields = parse_fields(text)
    missing_fields = missing_required_fields(fields)
    product_catalog_document_required = catalog_document_is_required(fields)
    product_document_ready = product_catalog_document_is_ready(fields, product_catalog_document_required)
    references_ready = normalize(fields.get("references_status", "")) in READY_REFERENCE_STATUSES
    status_approved = status == "approved"
    intake_ready = status_approved and not missing_fields and product_document_ready
    blockers = intake_blockers(
        exists=True,
        status=status,
        missing_fields=missing_fields,
        intake_ready=intake_ready,
        references_ready=references_ready,
        product_catalog_document_required=product_catalog_document_required,
        product_document_ready=product_document_ready,
    )

    return {
        "path": INTAKE_PATH.as_posix(),
        "exists": True,
        "status": status or "missing",
        "approved": status_approved,
        "allowed_statuses": sorted(ALLOWED_INTAKE_STATUSES),
        "fields": fields,
        "required_fields": REQUIRED_FIELDS,
        "missing_fields": missing_fields,
        "intake_ready": intake_ready,
        "references_ready": references_ready,
        "product_catalog_document_required": product_catalog_document_required,
        "blockers": blockers,
        "message": "SITE_INTAKE.md is approved." if intake_ready else "SITE_INTAKE.md has pending intake decisions.",
    }


def missing_intake_status() -> dict[str, object]:
    return {
        "path": INTAKE_PATH.as_posix(),
        "exists": False,
        "status": "missing",
        "approved": False,
        "allowed_statuses": sorted(ALLOWED_INTAKE_STATUSES),
        "fields": {},
        "required_fields": REQUIRED_FIELDS,
        "missing_fields": REQUIRED_FIELDS,
        "intake_ready": False,
        "references_ready": False,
        "product_catalog_document_required": False,
        "blockers": intake_blockers(
            exists=False,
            status="missing",
            missing_fields=REQUIRED_FIELDS,
            intake_ready=False,
            references_ready=False,
            product_catalog_document_required=False,
            product_document_ready=False,
        ),
        "message": "SITE_INTAKE.md is missing.",
    }


def missing_required_fields(fields: dict[str, str]) -> list[str]:
    return shared_missing_required_fields(fields, REQUIRED_FIELDS, unknown_values=UNKNOWN_VALUES)


def catalog_document_is_required(fields: dict[str, str]) -> bool:
    site_type = normalize(fields.get("site_type", ""))
    catalog_mode = normalize(fields.get("catalog_mode", ""))
    return site_type in CATALOG_SITE_TYPES or (catalog_mode not in UNKNOWN_VALUES and catalog_mode not in NO_CATALOG_MODES)


def product_catalog_document_is_ready(fields: dict[str, str], required: bool) -> bool:
    value = normalize(fields.get("product_catalog_document", ""))
    if value_is_unknown(value):
        return False
    if not required:
        return True
    return value in PRODUCT_DOCUMENT_READY_VALUES


def intake_blockers(
    *,
    exists: bool,
    status: str,
    missing_fields: list[str],
    intake_ready: bool,
    references_ready: bool,
    product_catalog_document_required: bool,
    product_document_ready: bool,
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    if not exists:
        blockers.append(
            {
                "area": "intake",
                "path": INTAKE_PATH.as_posix(),
                "message": "SITE_INTAKE.md is missing.",
                "next_command": "Create SITE_INTAKE.md from agents/harness/site-intake-template.md.",
            }
        )
    elif status not in ALLOWED_INTAKE_STATUSES:
        blockers.append(
            {
                "area": "intake",
                "path": INTAKE_PATH.as_posix(),
                "message": "SITE_INTAKE.md must declare Status: draft, approved, or needs-review.",
                "next_command": "Edit SITE_INTAKE.md and set a valid Status line.",
            }
        )
    elif status != "approved":
        blockers.append(
            {
                "area": "intake",
                "path": INTAKE_PATH.as_posix(),
                "message": f"SITE_INTAKE.md is {status}; set Status: approved after required decisions are accepted.",
                "next_command": "Edit SITE_INTAKE.md, then set Status: approved when accepted.",
            }
        )
    if missing_fields:
        blockers.append(
            {
                "area": "intake",
                "path": INTAKE_PATH.as_posix(),
                "message": "Missing required intake fields: " + ", ".join(missing_fields) + ".",
                "next_command": "Fill required SITE_INTAKE.md fields from the first-run intake.",
            }
        )
    if product_catalog_document_required and not product_document_ready:
        blockers.append(
            {
                "area": "intake",
                "path": INTAKE_PATH.as_posix(),
                "message": "Catalog/ecommerce intake must record product_catalog_document as needed or provided.",
                "next_command": "Update product_catalog_document in SITE_INTAKE.md.",
            }
        )
    if not references_ready:
        blockers.append(
            {
                "area": "references",
                "path": INTAKE_PATH.as_posix(),
                "message": "Reference sites or agent-suggested references are not approved.",
                "next_command": "Approve references and set references_status: approved in SITE_INTAKE.md.",
            }
        )
    if intake_ready and references_ready:
        return []
    return blockers


def value_is_unknown(value: str) -> bool:
    return shared_value_is_unknown(value, unknown_values=UNKNOWN_VALUES)
