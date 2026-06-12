from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .paths import relative_posix


REFERENCES_PATH = Path("SITE_REFERENCES.md")
ALLOWED_REFERENCE_STATUSES = {"approved", "draft", "needs-review"}
UNKNOWN_VALUES = {"", "unknown", "tbd", "todo", "not selected", "unselected", "pending"}
FIGMA_DESIGN_RE = re.compile(r"^https://(?:www\.)?figma\.com/design/[^/\s]+/.+", re.IGNORECASE)
HTTP_URL_RE = re.compile(r"^https?://", re.IGNORECASE)

REQUIRED_FIELDS = [
    "reference_analysis_status",
    "crawl_policy",
    "page_inventory",
    "screenshot_manifest",
    "figma_policy",
    "figma_reference",
    "ux_visual_analysis",
    "user_reference_approval",
]

FIELD_READY_VALUES = {
    "reference_analysis_status": {"complete"},
    "crawl_policy": {"bounded-crawl"},
    "page_inventory": {"complete"},
    "figma_policy": {"create-file", "existing-file"},
    "ux_visual_analysis": {"complete"},
    "user_reference_approval": {"approved"},
}

STATUS_RE = re.compile(r"^Status:\s*(?P<status>[A-Za-z0-9_-]+)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*):\s*(?P<value>.*?)\s*$", re.MULTILINE)


def reference_status(root: Path) -> dict[str, object]:
    path = root / REFERENCES_PATH
    if not path.exists():
        return missing_reference_status()

    text = path.read_text(encoding="utf-8", errors="replace")
    status = parse_status(text)
    fields = parse_fields(text)
    missing_fields = missing_required_fields(fields)
    manifest = manifest_status(root, fields.get("screenshot_manifest", ""))
    pending_reference_gates = pending_gates(fields, manifest)
    status_approved = status == "approved"
    reference_analysis_ready = status_approved and not missing_fields and not pending_reference_gates
    blockers = reference_blockers(
        exists=True,
        status=status,
        missing_fields=missing_fields,
        pending_reference_gates=pending_reference_gates,
        manifest=manifest,
    )

    return {
        "path": REFERENCES_PATH.as_posix(),
        "exists": True,
        "status": status or "missing",
        "approved": status_approved,
        "allowed_statuses": sorted(ALLOWED_REFERENCE_STATUSES),
        "fields": fields,
        "required_fields": REQUIRED_FIELDS,
        "missing_fields": missing_fields,
        "pending_reference_gates": pending_reference_gates,
        "reference_analysis_ready": reference_analysis_ready,
        "manifest": manifest,
        "blockers": blockers,
        "message": (
            "SITE_REFERENCES.md is approved."
            if reference_analysis_ready
            else "SITE_REFERENCES.md has pending reference analysis evidence."
        ),
    }


def missing_reference_status() -> dict[str, object]:
    manifest = empty_manifest_status()
    blockers = reference_blockers(
        exists=False,
        status="missing",
        missing_fields=REQUIRED_FIELDS,
        pending_reference_gates=REQUIRED_FIELDS,
        manifest=manifest,
    )
    return {
        "path": REFERENCES_PATH.as_posix(),
        "exists": False,
        "status": "missing",
        "approved": False,
        "allowed_statuses": sorted(ALLOWED_REFERENCE_STATUSES),
        "fields": {},
        "required_fields": REQUIRED_FIELDS,
        "missing_fields": REQUIRED_FIELDS,
        "pending_reference_gates": REQUIRED_FIELDS,
        "reference_analysis_ready": False,
        "manifest": manifest,
        "blockers": blockers,
        "message": "SITE_REFERENCES.md is missing.",
    }


def parse_status(text: str) -> str:
    match = STATUS_RE.search(text)
    if match is None:
        return "missing"
    return match.group("status").strip().casefold()


def parse_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in FIELD_RE.finditer(text):
        key = match.group("key").strip().replace("-", "_").casefold()
        if key == "status":
            continue
        fields[key] = match.group("value").strip()
    return fields


def missing_required_fields(fields: dict[str, str]) -> list[str]:
    return [field for field in REQUIRED_FIELDS if value_is_unknown(fields.get(field, ""))]


def pending_gates(fields: dict[str, str], manifest: dict[str, object]) -> list[str]:
    pending: list[str] = []
    for field, ready_values in FIELD_READY_VALUES.items():
        if normalize(fields.get(field, "")) not in ready_values:
            pending.append(field)
    if not valid_figma_design_url(fields.get("figma_reference", "")):
        pending.append("figma_reference")
    if not manifest.get("valid", False):
        pending.append("screenshot_manifest")
    return [field for field in REQUIRED_FIELDS if field in set(pending)]


def manifest_status(root: Path, raw_manifest_path: str) -> dict[str, object]:
    if value_is_unknown(raw_manifest_path):
        return empty_manifest_status()

    manifest_path, path_issue = resolve_manifest_path(root, raw_manifest_path)
    if path_issue:
        return manifest_summary(raw_manifest_path, False, [path_issue])
    assert manifest_path is not None
    rel_path = relative_posix(manifest_path, root)
    if not manifest_path.exists():
        return manifest_summary(rel_path, False, [f"Manifest file does not exist: {rel_path}"])

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return manifest_summary(rel_path, True, [f"Manifest JSON is invalid: {exc}"])

    issues, counts = validate_manifest_payload(root, payload)
    return {
        "path": rel_path,
        "exists": True,
        "valid": not issues,
        "issues": issues,
        **counts,
    }


def resolve_manifest_path(root: Path, raw_manifest_path: str) -> tuple[Path | None, str]:
    candidate = Path(raw_manifest_path)
    if candidate.is_absolute():
        return None, "screenshot_manifest must be a project-relative path."
    absolute = (root / candidate).resolve()
    resolved_root = root.resolve()
    try:
        rel = absolute.relative_to(resolved_root)
    except ValueError:
        return None, "screenshot_manifest must stay inside the project root."
    if rel.as_posix() != "raw/assets/references/manifest.json":
        return None, "screenshot_manifest must be raw/assets/references/manifest.json."
    return absolute, ""


def validate_manifest_payload(root: Path, payload: Any) -> tuple[list[str], dict[str, object]]:
    issues: list[str] = []
    reference_count = 0
    captured_page_count = 0
    skipped_url_count = 0
    blocker_count = 0
    figma_file = ""

    if not isinstance(payload, dict):
        return ["Manifest root must be a JSON object."], manifest_counts(0, 0, 0, 0, "")

    figma_file = str(payload.get("figma_file", "")).strip()
    if not valid_figma_design_url(figma_file):
        issues.append("Manifest figma_file must be a Figma design URL.")

    references = payload.get("references")
    if not isinstance(references, list) or not references:
        issues.append("Manifest references must be a non-empty list.")
        return issues, manifest_counts(0, 0, 0, 0, figma_file)

    reference_count = len(references)
    for index, reference in enumerate(references):
        if not isinstance(reference, dict):
            issues.append(f"Reference {index + 1} must be an object.")
            continue
        reference_url = str(reference.get("url", "")).strip()
        if not valid_http_url(reference_url):
            issues.append(f"Reference {index + 1} must include an http(s) url.")
        if normalize(str(reference.get("crawl_policy", ""))) != "bounded-crawl":
            issues.append(f"Reference {index + 1} must record crawl_policy as bounded-crawl.")

        pages = reference.get("pages")
        if not isinstance(pages, list) or not pages:
            issues.append(f"Reference {index + 1} must include at least one captured page.")
        else:
            for page_index, page in enumerate(pages):
                captured_page_count += 1
                issues.extend(validate_manifest_page(root, index, page_index, page))

        skipped_urls = reference.get("skipped_urls", [])
        if isinstance(skipped_urls, list):
            skipped_url_count += len(skipped_urls)
            for skipped_index, skipped in enumerate(skipped_urls):
                if not isinstance(skipped, dict) or value_is_unknown(str(skipped.get("reason", ""))):
                    issues.append(
                        f"Reference {index + 1} skipped URL {skipped_index + 1} must include a reason."
                    )
        else:
            issues.append(f"Reference {index + 1} skipped_urls must be a list.")

        blockers = reference.get("blockers", [])
        if isinstance(blockers, list):
            blocker_count += len(blockers)
            if blockers:
                issues.append(f"Reference {index + 1} has unresolved blockers.")
        else:
            issues.append(f"Reference {index + 1} blockers must be a list.")

    return issues, manifest_counts(reference_count, captured_page_count, skipped_url_count, blocker_count, figma_file)


def validate_manifest_page(root: Path, reference_index: int, page_index: int, page: Any) -> list[str]:
    label = f"Reference {reference_index + 1} page {page_index + 1}"
    if not isinstance(page, dict):
        return [f"{label} must be an object."]

    issues: list[str] = []
    if not valid_http_url(str(page.get("url", "")).strip()):
        issues.append(f"{label} must include an http(s) url.")
    if not valid_figma_design_url(str(page.get("figma_node", "")).strip()):
        issues.append(f"{label} must include a Figma design node URL.")
    for field in ["desktop_screenshot", "mobile_screenshot"]:
        raw_path = str(page.get(field, "")).strip()
        issue = screenshot_path_issue(root, raw_path, field, label)
        if issue:
            issues.append(issue)
    return issues


def screenshot_path_issue(root: Path, raw_path: str, field: str, label: str) -> str:
    if value_is_unknown(raw_path):
        return f"{label} must include {field}."
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return f"{label} {field} must be project-relative."
    absolute = (root / candidate).resolve()
    resolved_root = root.resolve()
    try:
        rel = absolute.relative_to(resolved_root)
    except ValueError:
        return f"{label} {field} must stay inside the project root."
    if not rel.as_posix().startswith("raw/assets/references/"):
        return f"{label} {field} must live under raw/assets/references/."
    if not absolute.exists():
        return f"{label} {field} file does not exist: {rel.as_posix()}"
    return ""


def manifest_counts(
    reference_count: int,
    captured_page_count: int,
    skipped_url_count: int,
    blocker_count: int,
    figma_file: str,
) -> dict[str, object]:
    return {
        "reference_count": reference_count,
        "captured_page_count": captured_page_count,
        "skipped_url_count": skipped_url_count,
        "blocker_count": blocker_count,
        "figma_file": figma_file,
    }


def manifest_summary(path: str, exists: bool, issues: list[str]) -> dict[str, object]:
    return {
        "path": path,
        "exists": exists,
        "valid": False,
        "issues": issues,
        **manifest_counts(0, 0, 0, 0, ""),
    }


def empty_manifest_status() -> dict[str, object]:
    return manifest_summary("raw/assets/references/manifest.json", False, ["screenshot_manifest is not recorded."])


def reference_blockers(
    *,
    exists: bool,
    status: str,
    missing_fields: list[str],
    pending_reference_gates: list[str],
    manifest: dict[str, object],
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    if not exists:
        blockers.append(
            {
                "area": "references",
                "path": REFERENCES_PATH.as_posix(),
                "message": "SITE_REFERENCES.md is missing.",
                "next_command": "Create SITE_REFERENCES.md from agents/harness/site-references-template.md.",
            }
        )
    elif status not in ALLOWED_REFERENCE_STATUSES:
        blockers.append(
            {
                "area": "references",
                "path": REFERENCES_PATH.as_posix(),
                "message": "SITE_REFERENCES.md must declare Status: draft, approved, or needs-review.",
                "next_command": "Edit SITE_REFERENCES.md and set a valid Status line.",
            }
        )
    elif status != "approved":
        blockers.append(
            {
                "area": "references",
                "path": REFERENCES_PATH.as_posix(),
                "message": f"SITE_REFERENCES.md is {status}; set Status: approved after reference analysis is accepted.",
                "next_command": "Edit SITE_REFERENCES.md, then set Status: approved when accepted.",
            }
        )
    if missing_fields:
        blockers.append(
            {
                "area": "references",
                "path": REFERENCES_PATH.as_posix(),
                "message": "Missing required reference fields: " + ", ".join(missing_fields) + ".",
                "next_command": "Fill required SITE_REFERENCES.md fields from reference analysis evidence.",
            }
        )
    for field in pending_reference_gates:
        blockers.append(
            {
                "area": "references",
                "path": REFERENCES_PATH.as_posix(),
                "message": f"Reference analysis gate is not ready: {field}.",
                "next_command": "Update SITE_REFERENCES.md and raw/assets/references/manifest.json after evidence is complete.",
            }
        )
    for issue in manifest.get("issues", []):
        blockers.append(
            {
                "area": "references",
                "path": str(manifest.get("path", "raw/assets/references/manifest.json")),
                "message": str(issue),
                "next_command": "Repair raw/assets/references/manifest.json or its referenced screenshots.",
            }
        )
    return blockers


def valid_http_url(value: str) -> bool:
    return bool(HTTP_URL_RE.search(value.strip()))


def valid_figma_design_url(value: str) -> bool:
    return bool(FIGMA_DESIGN_RE.search(value.strip()))


def normalize(value: str) -> str:
    return value.strip().casefold().replace(" ", "-").replace("_", "-")


def value_is_unknown(value: str) -> bool:
    return normalize(value) in UNKNOWN_VALUES
