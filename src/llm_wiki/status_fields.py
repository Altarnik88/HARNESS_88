from __future__ import annotations

import re
from collections.abc import Iterable


DEFAULT_UNKNOWN_VALUES = {"", "unknown", "tbd", "todo", "not selected", "unselected"}
STATUS_RE = re.compile(r"^Status:\s*(?P<status>[A-Za-z0-9_-]+)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*):\s*(?P<value>.*?)\s*$", re.MULTILINE)


def parse_status(text: str) -> str:
    match = STATUS_RE.search(text)
    if match is None:
        return "missing"
    return match.group("status").strip().casefold()


def parse_fields(text: str, *, normalize_values: bool = False) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in FIELD_RE.finditer(text):
        key = normalize_key(match.group("key"))
        if key == "status":
            continue
        value = match.group("value").strip()
        fields[key] = normalize(value) if normalize_values else value
    return fields


def missing_required_fields(
    fields: dict[str, str],
    required_fields: Iterable[str],
    *,
    unknown_values: set[str] | None = None,
) -> list[str]:
    return [field for field in required_fields if value_is_unknown(fields.get(field, ""), unknown_values=unknown_values)]


def value_is_unknown(value: str, *, unknown_values: set[str] | None = None) -> bool:
    values = unknown_values or DEFAULT_UNKNOWN_VALUES
    return normalize(value) in {normalize(item) for item in values}


def normalize(value: str) -> str:
    return value.strip().casefold().replace(" ", "-").replace("_", "-")


def normalize_key(value: str) -> str:
    return value.strip().replace("-", "_").casefold()
