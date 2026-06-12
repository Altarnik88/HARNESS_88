# Checkpoint: Core Harness Refactor Diagnostics Evidence Semantics

Linked task: `agents/tasks/2026-06-12-core-harness-refactor-diagnostics-evidence-semantics.md`

## Preflight Checks

- Worktree state checked.
- Owned files and do-not-edit files confirmed.
- Required context reviewed.

## Implementation Evidence

- Created a core-only task bundle for this refactor.
- Added `llm_wiki.status_fields` for shared `Status:` parsing, key/value parsing, normalization, unknown-value checks, and required-field detection.
- Refactored intake, references, and delivery gates to use the shared helper while preserving existing JSON fields.
- Updated task evidence so `residual_risk` counts only active unresolved risk and each task reports `residual_risk_state`.
- Added compact human diagnostics for `site doctor`, `task readiness`, and `tools audit`; JSON output remains the detailed contract.
- Updated tooling audit to report MCP capabilities as `host-managed` when local detection is not reliable.
- Updated security audit results with `network-unavailable` and `availability_reason` for npm registry/network failures.

## Verification Evidence

- Verification evidence: RED run `python -m unittest tests.test_status_fields` failed because `llm_wiki.status_fields` did not exist.
- Verification evidence: GREEN run `python -m unittest tests.test_status_fields tests.test_intake tests.test_references tests.test_gates` exited 0 with 21 tests OK.
- Verification evidence: RED run `python -m unittest tests.test_task_evidence` failed because residual risk states and breakdowns did not exist.
- Verification evidence: GREEN run `python -m unittest tests.test_task_evidence` exited 0 with 7 tests OK.
- Verification evidence: RED run `python -m unittest tests.test_doctor tests.test_task_cli tests.test_capabilities` failed because compact human diagnostics did not exist.
- Verification evidence: GREEN run `python -m unittest tests.test_capabilities tests.test_doctor tests.test_task_cli` exited 0 with 21 tests OK.
- Verification evidence: RED run `python -m unittest tests.test_security` failed because network-unavailable and availability reason were not reported.
- Verification evidence: GREEN run `python -m unittest tests.test_security` exited 0 with 5 tests OK.
- Verification evidence: focused integration run `python -m unittest tests.test_status_fields tests.test_intake tests.test_references tests.test_gates tests.test_task_evidence tests.test_capabilities tests.test_security tests.test_doctor tests.test_task_cli` exited 0 with 54 tests OK.
- Verification evidence: final `python tools/llm_wiki.py quality --skip-frontend` exited 0 with 131 tests OK, wiki rebuild OK, and strict lint OK.
- Verification evidence: final `python tools/llm_wiki.py site self-test` exited 0 with generated project self-test passed.
- Verification evidence: final `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.
- Verification evidence: final `python tools/llm_wiki.py task evidence --json` exited 0 with 6 task bundles, no evidence issues, 4 deferred risk states, and 2 unresolved known frontend audit risk states.
- Verification evidence: final sandbox `python tools/llm_wiki.py security audit --json --no-record` exited 0 and reported `network-unavailable`.
- Verification evidence: final escalated network `python tools/llm_wiki.py security audit --json --no-record` exited 0 and reported 2 unresolved moderate optional frontend npm audit findings for `next` and `postcss`.
- Verification evidence: final `npm run lint` in `frontend/` exited 0.
- Verification evidence: final `npm run build` in `frontend/` exited 0.

## Review Evidence

- Confirmed changes stayed core-only and did not select stack, fill site briefs, or start site/frontend implementation.
- Preserved existing JSON fields and added only compatible fields for clearer semantics.
- Kept known optional frontend npm audit findings as reporting scope only; no dependency updates or site implementation were attempted.

## Wiki and Log Updates

- Added a durable `wiki/log.md` maintenance entry for the core refactor.

## Residual Risk

- Known optional frontend npm audit findings remain unresolved; this task improves reporting only and does not update frontend dependencies.
