# Checkpoint: Core Maintainability Security Tooling DB Delivery Adapters

Linked task: `agents/tasks/2026-06-12-core-maintainability-security-tooling-db-delivery-adapters.md`

## Preflight Checks

- Worktree state checked.
- Owned files and do-not-edit files confirmed.
- Required context reviewed.
- Baseline dirty worktree recorded before implementation; existing changes in `src/llm_wiki/`, `tests/`, `wiki/log.md`, and one prior untracked task bundle were treated as pre-existing and preserved.
- Confirmed current branch is `task-evidence-summaries`, not `main` or `master`.
- Confirmed project constraints: no stack selection, no site approval changes, no frontend/site implementation, no `raw/` edits, and no direct `data/wiki.sqlite` edits.

## Implementation Evidence

- Created active core-only task bundle for maintainability/security/tooling/DB/deploy-adapter work.
- Priority 1 CLI maintainability:
  - Added additive smoke tests for `task readiness --json`, `site doctor --json --skip-self-test`, and `tools audit --json` top-level contracts.
  - Extracted CLI support helpers and task/site/tools/security command handlers into focused modules.
  - Reduced `src/llm_wiki/cli.py` to parser/dispatcher plus unchanged core/db handlers; no command names, flags, exit codes, or JSON shapes intentionally changed.
- Priority 2 security dry-run:
  - Added `security secret-plan` as an executable dry-run contract for non-secret provider/variable/operation metadata.
  - Added redacted rejection behavior for secret-looking values and `VAR=value` input.
  - Updated the secret broker protocol to document the dry-run command and explicitly deny value capture, `.env` writes, secret-store access, and MCP secret arguments.
- Priority 3 tooling readiness:
  - Added grouped `tools audit --json` guidance under `next_action_groups`.
  - Kept existing flat `next_actions` intact and only added metadata fields to each action.
  - Added blocked state for missing GitHub URLs, plugin URI connect permission kinds, and no-install host-managed MCP guidance.
- Priority 4 DB boundaries:
  - Extracted read-only search/event SQL helpers into `src/llm_wiki/db_search.py`.
  - Kept public `db.search()` and `db.list_events()` wrappers backward-compatible.
  - Did not change SQLite schema, migrations, generated DB files, or ingest/rebuild ownership.
- Priority 5 deploy handoff templates:
  - Added inactive stack-neutral deploy handoff template with sections for `next-static`, `next-fullstack`, `astro-content`, `sveltekit`, and `custom`.
  - Added read-only `stack deploy-template <profile>` helper returning JSON handoff metadata without editing `STACK.md`.
  - Included secret-plan handoff guidance with variable names only, not values.

## Verification Evidence

- Baseline `python tools/llm_wiki.py quality --json --skip-frontend`: passed; 131 Python tests OK, wiki rebuild OK, strict lint OK.
- Baseline `python tools/llm_wiki.py task readiness --json`: core development ready, site implementation locked by draft/unselected gates.
- Baseline `python tools/llm_wiki.py task evidence --json`: no evidence issues; pre-existing unresolved residual risk remains on two older verified tasks.
- Baseline `python tools/llm_wiki.py tools audit --json`: `needs-setup`, no required missing tools, missing setup remains permission-gated.
- Baseline `python tools/llm_wiki.py security audit --json --no-record`: `network-unavailable` due sandbox npm registry access denial.
- Baseline `python tools/llm_wiki.py site doctor --json --skip-self-test`: top-level `status: ok`; generated starter self-test skipped by requested flag.
- Priority 1 RED: `python -m unittest tests.test_cli_contracts.CliContractTests.test_cli_command_handlers_are_extractable -v` failed before module extraction with `ModuleNotFoundError`.
- Priority 1 GREEN: `python -m unittest tests.test_cli_contracts tests.test_task_cli tests.test_capabilities tests.test_doctor tests.test_security tests.test_intake tests.test_references tests.test_gates -v` passed, 49 tests OK.
- Priority 2 RED: focused secret-plan tests failed before the subcommand existed; protocol test failed before doc update.
- Priority 2 GREEN: `python -m unittest tests.test_security -v` passed, 8 tests OK.
- Priority 3 RED: focused tooling tests failed before grouped fields existed.
- Priority 3 GREEN: `python -m unittest tests.test_capabilities -v` passed, 14 tests OK.
- Priority 4 RED: focused DB extraction test failed before `llm_wiki.db_search` existed.
- Priority 4 GREEN: `python -m unittest tests.test_core -v` passed, 12 tests OK.
- Priority 5 RED: focused deploy-template tests failed before subcommand/template existed.
- Priority 5 GREEN: `python -m unittest tests.test_stack_cli -v` passed, 9 tests OK.
- Final `python tools/llm_wiki.py quality --skip-frontend`: passed; 147 Python tests OK, wiki rebuild OK, strict lint OK.
- Final `python tools/llm_wiki.py site self-test`: passed; generated starter self-test OK.
- Final `python tools/llm_wiki.py task validate --strict`: passed with no task validation issues.
- Final `python tools/llm_wiki.py task evidence --json`: passed before final review/wiki evidence recording; active task had implementation and verification evidence recorded.
- Final `python tools/llm_wiki.py tools audit --json`: returned `needs-setup`, no required missing tools, additive grouped guidance present.
- Final `python tools/llm_wiki.py security audit --json --no-record`: returned `network-unavailable` because sandbox blocked npm registry access; no review item recorded.
- Final `python tools/llm_wiki.py task readiness --json`: preserved existing top-level keys and kept `site_implementation_ready: false`.
- Final `python tools/llm_wiki.py site doctor --json --skip-self-test`: preserved existing top-level sections and returned `status: ok`.
- Final `python tools/llm_wiki.py stack deploy-template next-static --json`: returned `status: inactive-until-stack-approved` and `selects_stack: false`.
- Final `python tools/llm_wiki.py security secret-plan --provider supabase --vars SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY --operation "configure deployment env" --json`: returned `status: dry-run` and `secret_values_visible: false`.
- Final `cd frontend; npm run lint`: passed.
- Final `cd frontend; npm run build`: passed.
- Review RED: `python -m unittest tests.test_security.SecurityAuditTests.test_secret_plan_rejects_uppercase_token_without_echoing_it -v` failed before long uppercase token-shaped values were rejected.
- Review GREEN: `python -m unittest tests.test_security -v` passed, 9 tests OK.

## Review Evidence

- Self-review confirmed the strict scope was respected.
- No stack was selected and `STACK.md` was not edited.
- `PRODUCT.md`, `DESIGN.md`, `SITE_INTAKE.md`, `SITE_REFERENCES.md`, and `SITE_GATES.md` were not moved to approved.
- No frontend/site implementation was started.
- No `raw/` files or `data/wiki.sqlite` were edited.
- No tools, skills, plugins, or MCP resources were installed or connected automatically.
- No secret values were requested, displayed, written, or stored.
- Local review found and fixed a secret-plan edge case where a long all-uppercase token-shaped value could be accepted as a variable name.

## Wiki and Log Updates

- `wiki/log.md` was updated with a 2026-06-12 maintenance entry for this core-only task.

## Residual Risk

- Security audit could not reach npm registry in sandbox (`network-unavailable`); do not claim the dependency audit is clean.
- Pre-existing dirty workspace changes were preserved and not reverted.
