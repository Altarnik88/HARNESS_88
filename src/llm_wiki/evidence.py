from __future__ import annotations

import re
from pathlib import Path

from .harness import has_verification_evidence
from .tasks import TaskRecord, list_tasks, task_metrics


EVIDENCE_KEYS = [
    "implementation",
    "verification",
    "review",
    "wiki_log",
    "residual_risk",
]
RESIDUAL_RISK_STATES = ["none", "deferred", "accepted", "unresolved"]

SECTION_RE_TEMPLATE = r"^##\s+{title}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)"

PLACEHOLDER_TEXT = {
    "implementation": {"no implementation evidence recorded yet"},
    "review": {"no review evidence recorded yet"},
    "wiki_log": {"no wiki or log updates recorded yet"},
    "residual_risk": {"no residual risk recorded yet"},
}


def evidence_report(root: Path) -> dict[str, object]:
    records = list_tasks(root)
    rows: list[dict[str, object]] = []
    issues: list[dict[str, str]] = []
    missing_support_paths: list[str] = []
    verified_without_verification: list[str] = []
    evidence_paths: dict[str, list[str]] = {key: [] for key in EVIDENCE_KEYS}
    residual_risk_paths: dict[str, list[str]] = {state: [] for state in RESIDUAL_RISK_STATES}

    for record in records:
        row = task_evidence_row(root, record)
        rows.append(row)
        risk_state = str(row["residual_risk_state"])
        residual_risk_paths.setdefault(risk_state, []).append(record.path)

        support_files = row["support_files"]
        assert isinstance(support_files, dict)
        for label in ["progress", "checkpoint"]:
            support = support_files[label]
            assert isinstance(support, dict)
            if not support["exists"]:
                path = str(support["path"])
                missing_support_paths.append(path)
                issues.append(
                    {
                        "severity": "warning",
                        "path": record.path,
                        "message": f"Missing linked {label} file: {path}",
                    }
                )

        evidence = row["evidence"]
        assert isinstance(evidence, dict)
        for key in EVIDENCE_KEYS:
            if evidence[key]:
                evidence_paths[key].append(record.path)

        if record.status in {"verified", "done"} and not evidence["verification"]:
            verified_without_verification.append(record.path)
            issues.append(
                {
                    "severity": "warning",
                    "path": record.path,
                    "message": "Verified task lacks verification evidence.",
                }
            )

    return {
        "task_metrics": task_metrics(root),
        "summary": {
            "missing_support_files": evidence_bucket(missing_support_paths),
            "verified_without_verification": evidence_bucket(verified_without_verification),
            "implementation_evidence": evidence_bucket(evidence_paths["implementation"]),
            "verification_evidence": evidence_bucket(evidence_paths["verification"]),
            "review_evidence": evidence_bucket(evidence_paths["review"]),
            "wiki_log_evidence": evidence_bucket(evidence_paths["wiki_log"]),
            "residual_risk": evidence_bucket(evidence_paths["residual_risk"]),
            "residual_risk_states": {
                state: evidence_bucket(residual_risk_paths.get(state, []))
                for state in RESIDUAL_RISK_STATES
            },
        },
        "tasks": rows,
        "issues": issues,
    }


def task_evidence_row(root: Path, record: TaskRecord) -> dict[str, object]:
    task_path = root / record.path
    progress_rel = Path("agents") / "tasks" / "progress" / Path(record.path).name
    checkpoint_rel = Path("agents") / "tasks" / "checkpoints" / Path(record.path).name
    progress_path = root / progress_rel
    checkpoint_path = root / checkpoint_rel

    task_text = read_text(task_path)
    progress_text = read_text(progress_path)
    checkpoint_text = read_text(checkpoint_path)
    combined_text = "\n".join([task_text, progress_text, checkpoint_text])
    residual_risk = classify_residual_risk(section_body(checkpoint_text, "Residual Risk"))

    evidence = {
        "implementation": section_has_evidence(checkpoint_text, "Implementation Evidence", "implementation"),
        "verification": has_verification_evidence(combined_text),
        "review": section_has_evidence(checkpoint_text, "Review Evidence", "review"),
        "wiki_log": section_has_evidence(checkpoint_text, "Wiki and Log Updates", "wiki_log"),
        "residual_risk": residual_risk == "unresolved",
    }

    return {
        "path": record.path,
        "title": record.title,
        "status": record.status,
        "progress_path": progress_rel.as_posix(),
        "checkpoint_path": checkpoint_rel.as_posix(),
        "support_files": {
            "progress": {"path": progress_rel.as_posix(), "exists": progress_path.exists()},
            "checkpoint": {"path": checkpoint_rel.as_posix(), "exists": checkpoint_path.exists()},
        },
        "evidence": evidence,
        "residual_risk_state": residual_risk,
    }


def evidence_bucket(paths: list[str]) -> dict[str, object]:
    return {"count": len(paths), "paths": paths}


def section_has_evidence(text: str, title: str, key: str) -> bool:
    body = section_body(text, title)
    if body is None:
        return False
    normalized = normalize_text(body)
    if not normalized:
        return False
    return normalized not in PLACEHOLDER_TEXT[key]


def classify_residual_risk(body: str | None) -> str:
    if body is None:
        return "none"
    normalized = normalize_text(body)
    if not normalized or normalized in PLACEHOLDER_TEXT["residual_risk"]:
        return "none"
    if contains_any(
        normalized,
        [
            "no residual risk",
            "no known residual risk",
            "no unresolved risk",
            "none",
            "none recorded",
        ],
    ):
        return "none"
    if contains_any(normalized, ["accepted", "allowlist", "allowlisted", "allowed"]):
        return "accepted"
    if contains_any(
        normalized,
        [
            "unresolved",
            "blocking",
            "open security",
            "open issue",
            "finding remains",
            "findings remain",
            "vulnerability",
            "vulnerabilities",
            "npm audit finding",
            "npm audit item",
        ],
    ):
        return "unresolved"
    if contains_any(
        normalized,
        [
            "deferred",
            "future work",
            "future task",
            "separate task",
            "separate approved task",
            "not implemented in this task",
            "requires a separate",
            "after provider",
            "after platform",
        ],
    ):
        return "deferred"
    return "unresolved"


def section_body(text: str, title: str) -> str | None:
    pattern = re.compile(SECTION_RE_TEMPLATE.format(title=re.escape(title)), re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if match is None:
        return None
    return match.group("body").strip()


def normalize_text(text: str) -> str:
    stripped_lines = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("-"):
            line = line[1:].strip()
        if line:
            stripped_lines.append(line)
    return re.sub(r"\s+", " ", " ".join(stripped_lines).casefold()).strip().rstrip(".")


def contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")
