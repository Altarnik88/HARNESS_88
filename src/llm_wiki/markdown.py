from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any


WIKILINK_RE = re.compile(r"\[\[([^\]\n#|]+)(?:[#|][^\]\n]+)?\]\]")
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class WikiLink:
    target: str
    line: int
    context: str


@dataclass(frozen=True)
class FrontmatterResult:
    metadata: dict[str, Any]
    warnings: list[str]


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[str, str]:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return "", normalized
    end = normalized.find("\n---\n", 4)
    if end == -1:
        return "", normalized
    return normalized[4:end], normalized[end + 5 :]


def parse_frontmatter(text: str) -> dict[str, Any]:
    return parse_frontmatter_result(text).metadata


def parse_frontmatter_result(text: str) -> FrontmatterResult:
    raw, _ = split_frontmatter(text)
    if not raw:
        return FrontmatterResult({}, [])
    yaml_result = parse_frontmatter_yaml(raw)
    if yaml_result is not None:
        return yaml_result
    return FrontmatterResult(parse_frontmatter_simple(raw), [])


def parse_frontmatter_yaml(raw: str) -> FrontmatterResult | None:
    try:
        import yaml
    except ImportError:
        return None

    try:
        loaded = yaml.safe_load(raw)
    except Exception as exc:
        return FrontmatterResult(parse_frontmatter_simple(raw), [f"YAML frontmatter parse failed: {exc}"])
    if loaded is None:
        return FrontmatterResult({}, [])
    if not isinstance(loaded, dict):
        return FrontmatterResult(
            parse_frontmatter_simple(raw),
            [f"YAML frontmatter must be a mapping, got {type(loaded).__name__}."],
        )
    return FrontmatterResult(dict(loaded), [])


def parse_frontmatter_simple(raw: str) -> dict[str, Any]:
    if not raw:
        return {}

    lines = raw.splitlines()
    result: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            i += 1
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            result[key] = parse_scalar(value)
            i += 1
            continue

        items: list[Any] = []
        i += 1
        while i < len(lines) and lines[i].startswith("  - "):
            items.append(parse_scalar(lines[i][4:].strip()))
            i += 1
        result[key] = items
    return result


def parse_scalar(value: str) -> Any:
    if value in {"[]", ""}:
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value


def title_from_markdown(path: Path, text: str, frontmatter: dict[str, Any] | None = None) -> str:
    metadata = frontmatter if frontmatter is not None else parse_frontmatter(text)
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    match = HEADING_RE.search(text)
    if match:
        return match.group(1).strip()
    return path.stem.replace("-", " ").replace("_", " ").strip().title()


def summary_from_markdown(text: str, frontmatter: dict[str, Any] | None = None) -> str:
    metadata = frontmatter if frontmatter is not None else parse_frontmatter(text)
    summary = metadata.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary.strip()

    _, body = split_frontmatter(text)
    paragraphs = []
    for block in re.split(r"\n\s*\n", body):
        stripped = block.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        paragraphs.append(re.sub(r"\s+", " ", stripped))
    return paragraphs[0][:280] if paragraphs else ""


def list_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped == "[]":
            return []
        return [stripped]
    return [str(value).strip()]


def extract_wikilinks(text: str) -> list[WikiLink]:
    links: list[WikiLink] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in WIKILINK_RE.finditer(line):
            target = match.group(1).strip()
            if target:
                links.append(WikiLink(target=target, line=line_no, context=line.strip()[:240]))
    return links


def normalize_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.replace("_", " ").replace("-", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip().casefold()
    return normalized


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    pieces: list[str] = []
    last_dash = False
    for char in normalized:
        if char.isalnum():
            pieces.append(char)
            last_dash = False
        elif not last_dash:
            pieces.append("-")
            last_dash = True
    slug = "".join(pieces).strip("-")
    return slug or "untitled"


def frontmatter_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "\n" + "\n".join(f"  - {item}" for item in items)
