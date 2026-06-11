# Acceptance Checklists

Use these task-type checklists in task files, delegation briefs, and checkpoints. Every task also inherits default-deny tooling, assigned-file scope, and secret-handling rules from `agents/tooling-matrix.md`.

## Docs and Wiki

- Scope is respected.
- Assigned files only are changed.
- Relevant documentation links and wiki links resolve.
- `wiki/index.md` is updated when pages are added, moved, renamed, archived, or substantially changed.
- `wiki/log.md` records durable maintenance, ingest, query, lint, review, or migration work.
- `python tools/llm_wiki.py rebuild` runs after wiki edits.
- `python tools/llm_wiki.py lint` runs after wiki edits.
- No secrets are stored.
- Durable decisions are logged when needed.

## Frontend UI

- Scope is respected.
- Assigned files only are changed.
- Approved product and design direction exists before implementation.
- Approved `SITE_INTAKE.md`, selected stack state, and approved references exist before implementation.
- Layout is responsive across target viewports.
- Text fits its containers and does not overlap adjacent content.
- Keyboard and screen-reader basics are preserved.
- Repo-specific lint, test, or build command is run.
- Browser or Playwright check is run for visible UI changes.
- No secrets are stored.
- Durable decisions are logged when needed.

## Motion

- Scope is respected.
- Assigned files only are changed.
- Motion supports meaning, sequencing, feedback, or comprehension.
- `prefers-reduced-motion` is respected.
- Animations favor transform and opacity over layout properties.
- Relevant UI verification is run in a browser.
- No secrets are stored.
- Durable decisions are logged when needed.

## Backend and Data

- Scope is respected.
- Assigned files only are changed.
- Data contracts, migrations, and derived state are documented.
- Database and external-service mutations have explicit authorization.
- Relevant unit, integration, CLI, or inspection checks are run.
- Sensitive values remain in environment variables.
- No secrets are stored.
- Durable decisions are logged when needed.

## QA and Accessibility

- Scope is respected.
- Assigned files only are changed.
- Test coverage matches the user-facing risk of the change.
- Accessibility findings include reproduction steps and impact.
- Browser, Playwright, lint, build, or task-specific checks are run.
- Findings are tracked in the task, checkpoint, wiki, or review queue.
- No secrets are stored.
- Durable decisions are logged when needed.

## Performance and SEO

- Scope is respected.
- Assigned files only are changed.
- Metadata, structured content, and page intent are consistent with approved scope.
- Performance-sensitive assets, scripts, and animations are reviewed.
- Relevant build, audit, or browser checks are run.
- No secrets are stored.
- Durable decisions are logged when needed.

## DevOps and Release

- Scope is respected.
- Assigned files only are changed.
- CI, deploy, environment, and rollback implications are documented.
- GitHub or release writes have explicit user authorization.
- Relevant build, CI, or release checks are run.
- No secrets are stored.
- Durable decisions are logged when needed.
