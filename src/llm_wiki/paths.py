from __future__ import annotations

from pathlib import Path


DB_PATH = Path("data") / "wiki.sqlite"

WIKI_DIRS = [
    Path("raw") / "sources",
    Path("raw") / "assets",
    Path("wiki") / "entities",
    Path("wiki") / "concepts",
    Path("wiki") / "sources",
    Path("wiki") / "queries",
    Path("wiki") / "synthesis",
    Path("wiki") / "comparisons",
    Path("wiki") / "templates",
    Path("data"),
]

TEXT_EXTENSIONS = {
    ".csv",
    ".htm",
    ".html",
    ".json",
    ".log",
    ".md",
    ".py",
    ".rst",
    ".sql",
    ".tsv",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

PAGE_TYPE_BY_DIR = {
    "entities": "entity",
    "concepts": "concept",
    "sources": "source",
    "queries": "query",
    "synthesis": "synthesis",
    "comparisons": "comparison",
}

PAGE_DIR_BY_TYPE = {
    "entity": Path("wiki") / "entities",
    "concept": Path("wiki") / "concepts",
    "source": Path("wiki") / "sources",
    "query": Path("wiki") / "queries",
    "synthesis": Path("wiki") / "synthesis",
    "comparison": Path("wiki") / "comparisons",
    "overview": Path("wiki"),
}

KNOWLEDGE_PAGE_TYPES = set(PAGE_DIR_BY_TYPE)


def resolve_root(root: str | Path | None = None) -> Path:
    return Path(root or ".").resolve()


def relative_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS
