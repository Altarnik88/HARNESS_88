# Checkpoint: No Bundled Frontend Stack Selection

Linked task: `agents/tasks/2026-06-12-no-bundled-frontend-stack-selection.md`

## Preflight Checks

- Worktree state checked before implementation.
- Confirmed root branch `task-evidence-summaries`.
- Confirmed no existing uncommitted changes before task execution.
- Read the approved design spec and implementation plan.

## Implementation Evidence

- Removed the root bundled `frontend/` Next.js starter and generated starter frontend overlay.
- Updated `src/llm_wiki/site_generator.py` so generated projects no longer copy a prebuilt frontend app.
- Extended `StackProfile` metadata with languages, frameworks, services, best-fit cases, pros, cons, scaffold policy, selection questions, and deployment options.
- Updated `python tools/llm_wiki.py stack list` output to show stack pros, cons, and deployment comparison guidance.
- Updated first-run docs so agents recommend 2-4 stack options, wait for user approval, ask about VPS/VDS vs hosting, explain pros and cons, and recommend a publication target from client answers.
- Preserved approval gates: stack, product, intake, references, and delivery approval states were not advanced.

## Verification Evidence

- RED: `python -m unittest tests.test_site_generator tests.test_stack_neutral` failed before implementation because generated projects still contained `frontend/` and docs still mentioned the bundled starter.
- RED: `python -m unittest tests.test_stack_cli` failed before implementation because stack profiles lacked tradeoff/deployment metadata and CLI output lacked pros/cons.
- GREEN: `python -m unittest tests.test_site_generator tests.test_stack_neutral` exited 0 after implementation.
- GREEN: `python -m unittest tests.test_stack_cli tests.test_quality tests.test_security` exited 0 after implementation.
- `python -m unittest discover -s tests` exited 0 with 146 tests.
- `python tools/llm_wiki.py quality --skip-frontend` exited 0: Python tests, wiki rebuild, and strict lint passed.
- `python tools/llm_wiki.py security audit --json --no-record --blocking` exited 0 with `status: "skipped"` and `unresolved_count: 0`.
- `python tools/llm_wiki.py task validate --strict` exited 0 with no validation issues.

## Review Evidence

- `Test-Path frontend` returned `False`.
- `Test-Path src/llm_wiki/templates/site_starter/frontend` returned `False`.
- Search for old bundled-frontend wording returned no matches outside intentional historical task evidence before release/task updates.
- `STACK.md` remains unselected.
- `PRODUCT.md`, `SITE_INTAKE.md`, `SITE_REFERENCES.md`, and `SITE_GATES.md` were not edited.
- `DESIGN.md` remains `Status: draft`; no approval state changed.
- No secrets were requested, displayed, written, or stored.

## Wiki and Log Updates

- Updated `wiki/review.md` to close the old frontend audit blocker for the core release.
- Added a `wiki/log.md` decision entry for removing the bundled frontend and requiring stack/deployment selection before scaffolding.

## Residual Risk

- None for the core repository.
- Future scaffolded frontend/backend projects must run dependency audit, lint, build, and deployment checks after stack approval.
