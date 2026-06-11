from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import date
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
    (target / "agents" / "tasks").mkdir(parents=True, exist_ok=True)
    write_text(target / "agents" / "tasks" / "README.md", TASKS_README)
    write_text(target / "agents" / "tasks" / "_template.md", TASK_TEMPLATE)

    remove_path(target / "raw")
    write_text(target / "raw" / "sources" / ".gitkeep", "")
    write_text(target / "raw" / "assets" / ".gitkeep", "")

    remove_path(target / "wiki")
    for rel in [
        "comparisons/.gitkeep",
        "concepts/.gitkeep",
        "entities/.gitkeep",
        "queries/.gitkeep",
        "sources/.gitkeep",
        "synthesis/.gitkeep",
    ]:
        write_text(target / "wiki" / rel, "")
    write_text(target / "wiki" / "index.md", WIKI_INDEX)
    write_text(target / "wiki" / "log.md", WIKI_LOG)
    write_text(target / "wiki" / "review.md", WIKI_REVIEW)
    write_text(target / "wiki" / "templates" / "page.md", WIKI_PAGE_TEMPLATE)

    write_text(target / "README.md", STARTER_README)
    write_text(target / "AGENT_SITE_TOOLING.md", STARTER_TOOLING)
    write_text(target / "frontend" / "README.md", FRONTEND_README)
    write_text(target / "frontend" / "src" / "app" / "page.tsx", FRONTEND_PAGE)
    write_text(target / "frontend" / "src" / "app" / "layout.tsx", FRONTEND_LAYOUT)

    remove_path(target / "data")
    remove_path(target / ".agents")
    remove_path(target / ".codex")
    remove_path(target / "docs" / "presentations")
    remove_path(target / "skills-lock.json")


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


STARTER_README = """# Autonomous Site Starter

This project is a clean generated site workspace. It includes:

- a Next.js frontend in `frontend/`;
- Codex agent roles and harness templates in `agents/`;
- durable product and design briefs in `PRODUCT.md` and `DESIGN.md`;
- a local Markdown + SQLite LLM Wiki toolchain under `src/llm_wiki/`.

## First Run

```powershell
python tools/llm_wiki.py task readiness
python -m unittest discover -s tests
cd frontend
npm install
npm run lint
```

## Development Flow

1. Fill in `PRODUCT.md` with the website goal, audience, scope, and acceptance criteria.
2. Fill in `DESIGN.md` with the visual direction, UX constraints, and component rules.
3. Create atomic task files with `python tools/llm_wiki.py task create ...`.
4. Implement only from approved briefs and task ownership.
5. Run `python tools/llm_wiki.py quality` before handoff.

SQLite files under `data/` are generated state. Delete and rebuild them with `python tools/llm_wiki.py rebuild` whenever needed.
"""

STARTER_TOOLING = """# Agent Site Tooling

This clean project starts with the portable site-development harness only.

## Current Project State

- Workspace: `<project-root>`
- Frontend app: `frontend/`
- Frontend stack: Next.js App Router, TypeScript, Tailwind CSS, GSAP-ready package slots.
- Canonical LLM Wiki: `wiki/`
- Generated SQLite state: `data/wiki.sqlite`

## Hard Rules

- Do not begin website implementation until `PRODUCT.md`, `DESIGN.md`, or equivalent approved wiki decisions define the product and design direction.
- Keep secrets in environment variables only.
- Treat `data/wiki.sqlite` as generated state.
- Preserve files under `raw/` during ingest.
- For multi-agent website work, read `agents/TEAM.md` before delegation.
- Real implementation requires a concrete task file in `agents/tasks/` or an equivalent approved plan.

## Optional Resources

Project-local design and AI skill packs are intentionally not bundled in this generated starter. Install or copy them only when a task explicitly needs them, then record the decision in the wiki.

## Default Checks

```powershell
python -m unittest discover -s tests
python tools/llm_wiki.py task readiness
python tools/llm_wiki.py quality
```
"""

FRONTEND_README = """# Frontend

This is the generated Next.js app for the site workspace.

```powershell
npm install
npm run dev
npm run lint
npm run build
```

Start implementation only after `PRODUCT.md` and `DESIGN.md` are approved.
"""

FRONTEND_PAGE = """export default function Home() {
  return (
    <main className="min-h-screen bg-background px-6 py-16 text-foreground sm:px-10">
      <section className="mx-auto flex max-w-3xl flex-col gap-8">
        <div className="space-y-4">
          <p className="text-sm font-medium uppercase tracking-wide text-zinc-500">
            Autonomous Site Starter
          </p>
          <h1 className="text-4xl font-semibold tracking-normal text-balance sm:text-5xl">
            Project ready
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-zinc-600">
            Fill in PRODUCT.md and DESIGN.md, create the first task, then start
            building the site from approved scope.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {["Define product", "Choose direction", "Create task"].map((item) => (
            <div key={item} className="rounded-lg border border-zinc-200 bg-white p-5">
              <p className="text-sm font-medium text-zinc-900">{item}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
"""

FRONTEND_LAYOUT = """import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Autonomous Site Starter",
  description: "A clean generated site workspace for autonomous development.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
"""

TASKS_README = """# Durable Task Queue

This directory starts empty except for `_template.md`.

Use one task file per atomic implementation, QA, docs, release, or knowledge-stewardship unit.

```powershell
python tools/llm_wiki.py task create --title "Write Product Brief" --objective "Capture approved product decisions."
python tools/llm_wiki.py task list
python tools/llm_wiki.py task next
python tools/llm_wiki.py task validate --strict
```
"""

TASK_TEMPLATE = """# Task: Short Action-Oriented Name

Status: planned
Role owner: Conductor
Created: {today}

## Objective

Describe one atomic outcome.

## Context Files

- AGENTS.md
- agents/TEAM.md
- agents/tooling-matrix.md

## Ownership

- Owned files: none assigned yet
- Do not edit: raw/, data/wiki.sqlite

## Allowed Tooling

- Use only tooling granted by agents/tooling-matrix.md and this task file.

## Acceptance Checklist

- Scope is respected.
- Verification command is run.
- Completion evidence is recorded.

## Verification

Command:

```powershell
python tools/llm_wiki.py task validate --strict
```

Expected result:

```text
No task validation issues found.
```

## Progress

- No work has started.
""".format(today=date.today().isoformat())

WIKI_INDEX = """# Wiki Index

This clean wiki starts empty. Add durable decisions, source summaries, concepts, and synthesis pages as the project develops.

## Core Pages

- [[Review]]
"""

WIKI_LOG = """# Operation Log

Append durable project events using:

```markdown
## [YYYY-MM-DD] kind | Summary
- Path: `path/to/file`
```
"""

WIKI_REVIEW = """---
title: Review
type: overview
status: draft
confidence: medium
sources: []
tags: []
summary: Human-in-the-loop decisions and unresolved review items.
---

# Review

No review items recorded yet.
"""

WIKI_PAGE_TEMPLATE = """---
title: Page Title
type: concept
status: draft
confidence: medium
sources: []
tags: []
summary: One sentence summary.
---

# Page Title

## Summary

Write the durable synthesis here.

## Evidence

- Source: raw/sources/example.md

## Links

- Add relevant wikilinks here.

## Open Questions

- What still needs source-backed clarification?
"""
