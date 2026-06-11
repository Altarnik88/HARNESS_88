from __future__ import annotations

import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_wiki.db import (
    collect_lint_issues,
    complete_ingest_job,
    connect,
    create_page,
    enqueue_ingest_jobs,
    ensure_project,
    list_events,
    next_ingest_job,
    rebuild_index,
    search,
)
from llm_wiki.extractors import extract_text
from llm_wiki.markdown import parse_frontmatter, parse_frontmatter_result


class LlmWikiCoreTests(unittest.TestCase):
    def test_rebuild_indexes_pages_sources_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            (root / "raw" / "sources" / "source.md").write_text(
                "# Source\n\nThis source discusses knowledge graphs.", encoding="utf-8"
            )
            (root / "wiki" / "concepts" / "knowledge-graph.md").write_text(
                """---
title: Knowledge Graph
type: concept
status: draft
confidence: medium
sources:
  - raw/sources/source.md
tags:
  - graph
created: 2026-06-11
updated: 2026-06-11
summary: A graph of connected knowledge.
---

# Knowledge Graph

Links to [[Overview]].
""",
                encoding="utf-8",
            )
            (root / "wiki" / "overview.md").write_text(
                """---
title: Overview
type: overview
status: draft
confidence: medium
sources: []
tags: []
created: 2026-06-11
updated: 2026-06-11
summary: Overview page.
---

# Overview
""",
                encoding="utf-8",
            )

            stats = rebuild_index(root)
            self.assertEqual(stats.sources, 1)
            self.assertEqual(stats.pages, 2)
            self.assertEqual(stats.links, 1)

            results = search(root, "knowledge", limit=5)
            self.assertTrue(any(row["path"].endswith("knowledge-graph.md") for row in results))

    def test_lint_reports_dead_wikilinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            (root / "wiki" / "concepts" / "dangling.md").write_text(
                """---
title: Dangling
type: concept
status: draft
confidence: medium
sources: []
tags: []
created: 2026-06-11
updated: 2026-06-11
summary: Has a dead link.
---

# Dangling

See [[Missing Page]].
""",
                encoding="utf-8",
            )
            issues = collect_lint_issues(root)
            self.assertTrue(any("Dead wikilink" in issue.message for issue in issues))

    def test_create_page_uses_expected_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = create_page(root, "concept", "Flexible Database")
            self.assertEqual(page.parent, root / "wiki" / "concepts")
            self.assertTrue(page.exists())

    def test_text_extraction_reads_plain_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.txt"
            path.write_text("plain extraction needle", encoding="utf-8")
            extracted = extract_text(path)
            self.assertEqual(extracted.extractor, "text")
            self.assertIn("needle", extracted.text)
            self.assertEqual(extracted.warnings, [])

    def test_missing_pdf_dependency_warns_without_crashing_lint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            (root / "raw" / "sources" / "paper.pdf").write_bytes(b"%PDF-1.4\nnot a real pdf")
            with patch("llm_wiki.extractors.importlib.util.find_spec", return_value=None):
                issues = collect_lint_issues(root)
            self.assertTrue(any("pypdf" in issue.message for issue in issues))

    def test_log_events_sync_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            (root / "wiki" / "log.md").write_text(
                "# Wiki Log\n\n## [2026-06-11] ingest | Added source\n\n- Path: `raw/sources/a.md`\n",
                encoding="utf-8",
            )
            rebuild_index(root)
            rebuild_index(root)
            events = list_events(root, limit=10)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["kind"], "ingest")
            self.assertEqual(events[0]["object_path"], "raw/sources/a.md")

    def test_ingest_queue_next_and_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            (root / "raw" / "sources" / "source.md").write_text(
                "# Source\n\nQueue state machine text.", encoding="utf-8"
            )
            result = enqueue_ingest_jobs(root, [], all_new=True)
            self.assertEqual(len(result["queued"]), 1)
            job_id = result["queued"][0]["job_id"]

            package = next_ingest_job(root)
            self.assertIsNotNone(package)
            assert package is not None
            self.assertEqual(package["job_id"], job_id)
            self.assertEqual(package["status"], "in_progress")
            self.assertIn("Queue state machine", package["extraction"]["text_preview"])

            completed = complete_ingest_job(root, job_id, ["wiki/sources/source.md"], "done")
            self.assertEqual(completed["status"], "completed")
            conn = connect(root)
            try:
                status = conn.execute("SELECT status FROM ingest_jobs WHERE id = ?", (job_id,)).fetchone()[0]
            finally:
                conn.close()
            self.assertEqual(status, "completed")

    def test_fts_search_finds_extracted_source_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            (root / "raw" / "sources" / "source.md").write_text(
                "# Source\n\nUniqueExtractedNeedle appears only in raw source text.", encoding="utf-8"
            )
            rebuild_index(root)
            results = search(root, "UniqueExtractedNeedle", limit=5)
            self.assertTrue(any(row["kind"] == "source" for row in results))

    def test_rebuild_indexes_task_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            task_dir = root / "agents" / "tasks"
            task_dir.mkdir(parents=True, exist_ok=True)
            (task_dir / "2026-06-11-index-me.md").write_text(
                """# Task: Index Me

Status: ready
Role owner: Conductor
Created: 2026-06-11

## Objective

Make task records queryable.

## Context Files

- AGENTS.md

## Ownership

- Owned files: agents/tasks/2026-06-11-index-me.md
- Do not edit: raw/

## Allowed Tooling

- LLM Wiki CLI only.

## Acceptance Checklist

- Scope is respected.

## Verification

Command:

```powershell
python tools/llm_wiki.py task validate --strict
```

Expected result:

- exits 0.

## Progress

- No work has started.
""",
                encoding="utf-8",
            )

            rebuild_index(root)
            conn = connect(root)
            try:
                row = conn.execute("SELECT title, status FROM task_records WHERE path = ?", ("agents/tasks/2026-06-11-index-me.md",)).fetchone()
            finally:
                conn.close()

            self.assertIsNotNone(row)
            assert row is not None
            self.assertEqual(row["title"], "Index Me")
            self.assertEqual(row["status"], "ready")

    @unittest.skipUnless(__import__("importlib").util.find_spec("yaml") is not None, "PyYAML not installed")
    def test_yaml_frontmatter_supports_nested_fields_when_available(self) -> None:
        metadata = parse_frontmatter(
            """---
title: YAML Page
type: concept
aliases:
  - Alpha
  - Beta
nested:
  owner: Team
---

# YAML Page
"""
        )
        self.assertEqual(metadata["aliases"], ["Alpha", "Beta"])
        self.assertEqual(metadata["nested"]["owner"], "Team")

    def test_invalid_yaml_frontmatter_warns_and_falls_back(self) -> None:
        result = parse_frontmatter_result(
            """---
title: Broken YAML
aliases: [unterminated
---

# Broken YAML
"""
        )
        self.assertEqual(result.metadata["title"], "Broken YAML")
        self.assertTrue(result.warnings)


if __name__ == "__main__":
    unittest.main()
