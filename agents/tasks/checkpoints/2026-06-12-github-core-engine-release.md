# Checkpoint: GitHub Core Engine Release

Linked task: `agents/tasks/2026-06-12-github-core-engine-release.md`

## Preflight Checks

- Confirmed the release target is HARNESS_88 as a stack-neutral site-development engine, not a completed site.
- Confirmed stack, product, design, intake, reference, and delivery approval states must not be advanced for the core release.
- Confirmed the former full-repo blocker came from the bundled Next.js frontend starter, not the HARNESS_88 core engine.

## Implementation Evidence

- Removed the bundled `frontend/` starter through the no-bundled-frontend stack-selection task.
- Updated release notes for `v0.1.0` as release-ready core infrastructure.
- Updated stack/deployment guidance so agents recommend stacks through dialogue and ask about VPS/VDS vs hosting before publish planning.
- Updated the review queue to close the old Next/PostCSS item for the core release.
- Did not select a stack or approve site/product/design gates.
- Did not install tools, skills, plugins, or dependencies.

## Verification Evidence

- `python -m unittest discover -s tests` exited 0 with 146 tests.
- `python tools/llm_wiki.py quality --skip-frontend` exited 0: Python tests, wiki rebuild, and strict lint passed.
- `python tools/llm_wiki.py security audit --json --no-record --blocking` exited 0 with `status: "skipped"` and `unresolved_count: 0` because no `frontend/package.json` exists.
- `python tools/llm_wiki.py task validate --strict` exited 0 with no validation issues.

## Review Evidence

- `STACK.md` was not edited and remains unselected.
- `PRODUCT.md`, `SITE_INTAKE.md`, `SITE_REFERENCES.md`, and `SITE_GATES.md` were not moved to approved.
- `DESIGN.md` remains `Status: draft`; only wording was updated to remove the obsolete bundled frontend reference.
- No frontend/site implementation was started.
- No `raw/` files or `data/wiki.sqlite` were edited directly.
- No secrets were requested or stored.

## Wiki and Log Updates

- Updated `wiki/review.md` with the closed frontend audit blocker and stack/deployment selection decision.
- Added a `wiki/log.md` decision entry for removing the bundled frontend starter and requiring approved stack/deployment selection.

## Residual Risk

- None for the core release blocker.
- Future scaffolded frontend/backend projects must run their own dependency audits after stack approval.
