# Purpose

This wiki is a flexible database for a new project. Its first job is to accumulate source-backed knowledge in a durable, inspectable form before the project has a fixed product shape.

## Goals

- Preserve raw sources without mutating them.
- Turn sources into an evolving network of Markdown pages.
- Keep page claims traceable to sources.
- Make the knowledge base useful to both humans and LLM agents.
- Keep the storage layer simple enough to rebuild and migrate.

## Current Scope

- General project research and planning.
- Source summaries, concepts, entities, comparisons, and synthesis pages.
- Local SQLite index for search, link graph, events, review items, and future extensions.

## Open Decisions

- Whether this becomes a CLI-only system, desktop app, web app, MCP server, or hybrid.
- Whether vector search is needed after the Markdown/SQLite baseline grows.
- Which domain-specific page types should be added after the first real sources are ingested.
