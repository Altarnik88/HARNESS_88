from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT_FILES = [
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "AGENT_SITE_TOOLING.md",
    "DESIGN.md",
    "LICENSE",
    "NOTICE/THIRD_PARTY.md",
    "PRODUCT.md",
    "README.md",
    "SITE_GATES.md",
    "SITE_INTAKE.md",
    "STACK.md",
    "START_HERE.md",
    "llms.txt",
    "purpose.md",
    "pyproject.toml",
    "schema.md",
]

COPY_PATHS = [
    ".github/workflows/quality.yml",
    "agents/TEAM.md",
    "agents/conductor.md",
    "agents/harness",
    "agents/protocols",
    "agents/resources",
    "agents/roles",
    "agents/templates",
    "agents/tooling-matrix.md",
    "agents/workflows",
    "frontend",
    "src/llm_wiki",
    "tests",
    "tools/llm_wiki.py",
]

EXCLUDED_DIR_NAMES = {
    "__pycache__",
    ".next",
    ".pytest_cache",
    ".turbo",
    "build",
    "dist",
    "node_modules",
}

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

SITE_STARTER_TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates" / "site_starter"


@dataclass(frozen=True)
class SiteProjectCreateResult:
    target: Path
    copied_files: int


def create_site_project(source_root: Path, target: Path) -> SiteProjectCreateResult:
    source_root = source_root.resolve()
    target = target.resolve()
    prepare_target(target)

    copied = 0
    for raw_path in ROOT_FILES:
        copied += copy_path(source_root, target, Path(raw_path))
    for raw_path in COPY_PATHS:
        copied += copy_path(source_root, target, Path(raw_path))

    reset_clean_state(target)
    sanitize_text_files(target, source_root)
    return SiteProjectCreateResult(target=target, copied_files=copied)


def prepare_target(target: Path) -> None:
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"Target directory is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)


def copy_path(source_root: Path, target_root: Path, rel_path: Path) -> int:
    source = source_root / rel_path
    if not source.exists():
        return 0
    target = target_root / rel_path
    if source.is_dir():
        return copy_directory(source, target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return 1


def copy_directory(source: Path, target: Path) -> int:
    copied = 0
    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        if any(part in EXCLUDED_DIR_NAMES for part in path.relative_to(source).parts):
            continue
        rel = path.relative_to(source)
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        copied += 1
    return copied


def reset_clean_state(target: Path) -> None:
    remove_path(target / "agents" / "tasks")
    remove_path(target / "raw")
    remove_path(target / "wiki")

    write_text(target / "raw" / "sources" / ".gitkeep", "")
    write_text(target / "raw" / "assets" / ".gitkeep", "")
    for rel in [
        "comparisons/.gitkeep",
        "concepts/.gitkeep",
        "entities/.gitkeep",
        "queries/.gitkeep",
        "sources/.gitkeep",
        "synthesis/.gitkeep",
    ]:
        write_text(target / "wiki" / rel, "")

    copy_template_tree(target)

    remove_path(target / "data")
    remove_path(target / ".agents")
    remove_path(target / ".codex")
    remove_path(target / "docs" / "presentations")
    remove_path(target / "skills-lock.json")


def copy_template_tree(target: Path) -> int:
    copied = 0
    for path in sorted(SITE_STARTER_TEMPLATE_ROOT.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(SITE_STARTER_TEMPLATE_ROOT)
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        copied += 1
    return copied


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def sanitize_text_files(root: Path, source_root: Path) -> None:
    source_variants = {
        str(source_root),
        source_root.as_posix(),
        str(source_root).replace("\\", "\\\\"),
    }
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = text
        for value in source_variants:
            updated = updated.replace(value, "<project-root>")
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
