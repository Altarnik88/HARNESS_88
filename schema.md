# LLM Wiki Schema

The Markdown wiki is the canonical knowledge layer. SQLite is a rebuildable index that makes the wiki searchable and easier to inspect programmatically.

## Directory Layout

```text
raw/
  sources/      Immutable source files.
  assets/       Local images, screenshots, attachments.
wiki/
  index.md      Content catalog.
  log.md        Append-only operation log.
  overview.md   Rolling synthesis.
  review.md     Human judgment queue.
  entities/     People, organizations, products, places.
  concepts/     Ideas, methods, patterns, technologies.
  sources/      One summary page per ingested source.
  queries/      Saved answers that should compound into the wiki.
  synthesis/    Cross-source arguments and evolving theses.
  comparisons/  Side-by-side analyses.
  templates/    Page templates; not indexed as knowledge pages.
data/
  wiki.sqlite   Generated index; safe to rebuild.
```

## Page Frontmatter

Every knowledge page should start with YAML frontmatter. If PyYAML is installed, nested YAML is supported; otherwise the CLI falls back to a simple parser for scalar fields and flat lists.

```yaml
---
title: Page Title
type: concept
status: draft
confidence: medium
sources:
  - raw/sources/example.md
tags:
  - example
created: 2026-06-11
updated: 2026-06-11
summary: One sentence summary.
---
```

Required fields for knowledge pages:

- `title`: Human-readable title and default wikilink target.
- `type`: `entity`, `concept`, `source`, `query`, `synthesis`, `comparison`, or `overview`.
- `status`: `draft`, `active`, `stale`, `contradicted`, or `archived`.
- `confidence`: `low`, `medium`, or `high`.
- `sources`: Raw source paths that support the page.
- `summary`: One-sentence page summary for index/search.

## Links

- Use Obsidian-style `[[Page Title]]` links for wiki-to-wiki references.
- Prefer linking on first meaningful mention in each section.
- Do not create duplicate pages for spelling variants; rename or add aliases in frontmatter later if needed.

## Claims and Citations

- Important claims should be backed by source paths in frontmatter and, when useful, inline notes like `Source: raw/sources/file.md`.
- If a source contradicts an existing page, mark the affected page `status: contradicted` or add a review item.
- Do not bury uncertainty. Use explicit sections such as `## Open Questions`, `## Contradictions`, or `## Evidence`.

## Operation Log

Append entries to `wiki/log.md` with this exact heading shape:

```markdown
## [YYYY-MM-DD] ingest | Source title
```

Kinds: `init`, `ingest`, `query`, `lint`, `migration`, `maintenance`, `review`.

During rebuild, parseable log headings are synced into the SQLite `events` table with stable event keys.

## Agent-Assisted Ingest Queue

The ingest queue is local and agent-assisted. It does not call an LLM API by itself.

```powershell
python tools/llm_wiki.py ingest enqueue --all-new
python tools/llm_wiki.py ingest next
python tools/llm_wiki.py ingest complete JOB_ID --pages wiki/sources/source.md --notes "done"
python tools/llm_wiki.py ingest fail JOB_ID --reason "blocked reason"
```

`ingest next` marks one job `in_progress` and prints the source path, extracted text preview, extraction warnings, relevant pages, and the required output contract.

## SQLite Index

`data/wiki.sqlite` is rebuilt from files by:

```powershell
python tools/llm_wiki.py rebuild
```

It stores:

- Sources with hashes and availability.
- Extracted source text and extractor warnings.
- Pages with frontmatter, summaries, status, and content hashes.
- Page-source relationships.
- Wikilinks and resolved graph edges.
- Claims, tags, review items, ingest jobs, and log-synced events.
- FTS search tables when SQLite FTS5 is available.

Markdown remains the portable source of truth.
