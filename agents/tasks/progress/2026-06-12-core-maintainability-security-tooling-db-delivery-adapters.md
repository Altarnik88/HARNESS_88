# Progress: Core Maintainability Security Tooling DB Delivery Adapters

Linked task: `agents/tasks/2026-06-12-core-maintainability-security-tooling-db-delivery-adapters.md`
Current status: verified

## Completed Steps

- Created the core-only task and confirmed owned/do-not-edit scope.
- Ran baseline checks before implementation:
  - `git status --short`
  - `python tools/llm_wiki.py quality --json --skip-frontend`
  - `python tools/llm_wiki.py task readiness --json`
  - `python tools/llm_wiki.py task evidence --json`
  - `python tools/llm_wiki.py tools audit --json`
  - `python tools/llm_wiki.py security audit --json --no-record`
  - `python tools/llm_wiki.py site doctor --json --skip-self-test`
- Priority 1 RED/GREEN complete:
  - Added CLI JSON smoke contract tests.
  - Extracted CLI support helpers into `src/llm_wiki/cli_support.py`.
  - Extracted command handlers into `src/llm_wiki/cli_tasks.py`, `src/llm_wiki/cli_site.py`, `src/llm_wiki/cli_tools.py`, and `src/llm_wiki/cli_security.py`.
  - Kept `src/llm_wiki/cli.py` as parser/dispatcher plus existing core/db commands; current file length is 418 lines.
- Priority 2 RED/GREEN complete:
  - Added `python tools/llm_wiki.py security secret-plan ... --json`.
  - The command returns a redacted dry-run receipt and rejects `VAR=value` or secret-looking metadata without echoing secret values.
  - Updated `agents/workflows/secret-broker.md` to document the dry-run command and its non-secret boundary.
- Priority 3 RED/GREEN complete:
  - Added additive `next_action_groups` to `tools audit --json`.
  - Added `group`, `permission_kind`, and `blocked` metadata to flat `next_actions` while preserving the flat list.
  - Blank GitHub URLs are blocked until an exact user-approved URL is recorded.
  - Plugin URIs produce connect permission prompts, and host-managed MCP entries appear only as non-install grouped guidance.
- Priority 4 RED/GREEN complete:
  - Added `src/llm_wiki/db_search.py` for read-side `fts_query`, `search_rows`, and `list_event_rows`.
  - Kept `src/llm_wiki/db.py` public wrappers and schema/rebuild behavior intact.
  - No SQLite schema migration or direct `data/wiki.sqlite` edit was introduced.
- Priority 5 RED/GREEN complete:
  - Added inactive, profile-aware `agents/harness/deploy-handoff-template.md`.
  - Added read-only `python tools/llm_wiki.py stack deploy-template <profile> --json`.
  - The helper returns deploy handoff metadata without selecting a stack or editing `STACK.md`.

## Residual Risk

- `security audit --json --no-record` returned `network-unavailable` because npm registry access is blocked in the sandbox (`connect EACCES`). Do not bypass network without user approval.
- The workspace had pre-existing dirty files before this task started; unrelated user/previous changes were preserved.

## Next Action

- None; task is verified. Future work should start from a new task.

## Files Changed

- Added this task, progress, and checkpoint file.
- Added `tests/test_cli_contracts.py`.
- Added `src/llm_wiki/cli_support.py`, `src/llm_wiki/cli_tasks.py`, `src/llm_wiki/cli_site.py`, `src/llm_wiki/cli_tools.py`, and `src/llm_wiki/cli_security.py`.
- Updated `src/llm_wiki/cli.py` to import extracted handlers.
- Updated `src/llm_wiki/security.py`, `src/llm_wiki/cli_security.py`, `tests/test_security.py`, and `agents/workflows/secret-broker.md`.
- Updated `src/llm_wiki/capabilities.py` and `tests/test_capabilities.py`.
- Updated `src/llm_wiki/db.py`, added `src/llm_wiki/db_search.py`, and updated `tests/test_core.py`.
- Updated `src/llm_wiki/stack.py`, `src/llm_wiki/cli.py`, `tests/test_stack_cli.py`, and added `agents/harness/deploy-handoff-template.md`.

## Verification Run

- `python tools/llm_wiki.py quality --json --skip-frontend` passed: 131 tests OK, wiki rebuild OK, strict lint OK.
- `python tools/llm_wiki.py task readiness --json` preserved site implementation lock: product/design/stack/intake/references pending.
- `python tools/llm_wiki.py task evidence --json` reported no task evidence issues; two pre-existing verified tasks still have unresolved residual risk.
- `python tools/llm_wiki.py tools audit --json` returned `needs-setup` with no required missing tools.
- `python tools/llm_wiki.py security audit --json --no-record` returned `network-unavailable`; no review item recorded.
- `python tools/llm_wiki.py site doctor --json --skip-self-test` returned top-level `status: ok`.
- RED: `python -m unittest tests.test_cli_contracts.CliContractTests.test_cli_command_handlers_are_extractable -v` failed with `ModuleNotFoundError` before handler modules were created.
- GREEN: `python -m unittest tests.test_cli_contracts tests.test_task_cli tests.test_capabilities tests.test_doctor tests.test_security tests.test_intake tests.test_references tests.test_gates -v` passed, 49 tests OK.
- RED: focused secret-plan tests failed before the `security secret-plan` subcommand existed; doc-alignment test failed before protocol update.
- GREEN: `python -m unittest tests.test_security -v` passed, 8 tests OK.
- RED: focused tooling grouping tests failed on missing `next_action_groups`, `permission_kind`, and `blocked` fields.
- GREEN: `python -m unittest tests.test_capabilities -v` passed, 14 tests OK.
- RED: `python -m unittest tests.test_core.LlmWikiCoreTests.test_db_search_helpers_are_extractable_read_side_helpers -v` failed with `ModuleNotFoundError` before extraction.
- GREEN: `python -m unittest tests.test_core -v` passed, 12 tests OK.
- RED: focused deploy-template tests failed before the CLI subcommand and template existed.
- GREEN: `python -m unittest tests.test_stack_cli -v` passed, 9 tests OK.
- Final `python tools/llm_wiki.py quality --skip-frontend` passed: 147 Python tests OK, wiki rebuild OK, strict lint OK.
- Final `python tools/llm_wiki.py site self-test` passed: generated project self-test OK plus quality checks OK.
- Final `python tools/llm_wiki.py task validate --strict` passed with no validation issues.
- Final `python tools/llm_wiki.py task evidence --json` passed with no task evidence issues before final review/wiki evidence recording.
- Final `python tools/llm_wiki.py tools audit --json` preserved `status: needs-setup`, no required missing tools, and additive grouped guidance.
- Final `python tools/llm_wiki.py security audit --json --no-record` returned `network-unavailable`; no review item recorded and no network bypass attempted.
- Contract smoke checks confirmed `task readiness --json`, `site doctor --json --skip-self-test`, `stack deploy-template next-static --json`, and `security secret-plan ... --json`.
- `cd frontend; npm run lint` passed.
- `cd frontend; npm run build` passed.
- Review RED: `python -m unittest tests.test_security.SecurityAuditTests.test_secret_plan_rejects_uppercase_token_without_echoing_it -v` failed before long uppercase token-shaped values were rejected.
- Review GREEN: `python -m unittest tests.test_security -v` passed, 9 tests OK, after tightening secret-plan token detection.

## Review Evidence

- Self-review confirmed no forbidden files were intentionally edited: `STACK.md`, `PRODUCT.md`, `DESIGN.md`, `SITE_INTAKE.md`, `SITE_REFERENCES.md`, `SITE_GATES.md`, `raw/`, `data/wiki.sqlite`, and `frontend/` source files were not changed.
- Stack remains unselected, site approval docs remain unapproved, frontend/site implementation was not started, and no secret values were requested or stored.
- Local code review found and fixed one secret-plan hardening gap: long uppercase token-shaped values are now rejected without echoing them.

## Wiki and Log Updates

- Appended a concise maintenance entry to `wiki/log.md` for CLI split, secret-plan, tooling grouping, DB read helper extraction, and inactive deploy handoff templates.

## Clean-Context Handoff Notes

- Read the linked task, this progress file, and the matching checkpoint before continuing.
