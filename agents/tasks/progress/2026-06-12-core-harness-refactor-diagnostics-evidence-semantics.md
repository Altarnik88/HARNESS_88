# Progress: Core Harness Refactor Diagnostics Evidence Semantics

Linked task: `agents/tasks/2026-06-12-core-harness-refactor-diagnostics-evidence-semantics.md`
Current status: verified

## Completed Steps

- Created the core-only task bundle and confirmed the worktree was clean.
- Added shared status/field parsing helpers and migrated intake, references, and delivery gates to use them.
- Updated task evidence semantics so `residual_risk` reports active unresolved risk, with separate residual risk states for none, deferred, accepted, and unresolved.
- Improved compact human diagnostics for readiness, doctor, and tooling audit output while preserving JSON output.
- Reported MCP capabilities as host-managed when the local CLI cannot detect host-managed availability.
- Improved npm audit reporting to distinguish network-unavailable audit runs from malformed audit output and real vulnerability findings.

## Current Blocker

- None.

## Next Action

- None; task is verified.

## Files Changed

- `src/llm_wiki/status_fields.py`
- `src/llm_wiki/intake.py`
- `src/llm_wiki/references.py`
- `src/llm_wiki/gates.py`
- `src/llm_wiki/evidence.py`
- `src/llm_wiki/capabilities.py`
- `src/llm_wiki/security.py`
- `src/llm_wiki/cli.py`
- `tests/test_status_fields.py`
- `tests/test_task_evidence.py`
- `tests/test_capabilities.py`
- `tests/test_security.py`
- `tests/test_doctor.py`
- `tests/test_task_cli.py`
- task progress/checkpoint files and `wiki/log.md`

## Verification Run

- Verification evidence: `python -m unittest tests.test_status_fields tests.test_intake tests.test_references tests.test_gates` exited 0 with 21 tests OK.
- Verification evidence: `python -m unittest tests.test_task_evidence` exited 0 with 7 tests OK.
- Verification evidence: `python -m unittest tests.test_capabilities tests.test_doctor tests.test_task_cli` exited 0 with 21 tests OK.
- Verification evidence: `python -m unittest tests.test_security` exited 0 with 5 tests OK.
- Verification evidence: `python -m unittest tests.test_status_fields tests.test_intake tests.test_references tests.test_gates tests.test_task_evidence tests.test_capabilities tests.test_security tests.test_doctor tests.test_task_cli` exited 0 with 54 tests OK.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0 with 131 tests OK, wiki rebuild OK, and strict lint OK.
- Verification evidence: `python tools/llm_wiki.py site self-test` exited 0 with generated project self-test passed.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.
- Verification evidence: `python tools/llm_wiki.py task evidence --json` exited 0 with 6 task bundles, no evidence issues, 4 deferred risk states, and 2 unresolved known frontend audit risk states.
- Verification evidence: sandbox `python tools/llm_wiki.py security audit --json --no-record` exited 0 and reported `network-unavailable`.
- Verification evidence: escalated network `python tools/llm_wiki.py security audit --json --no-record` exited 0 and reported 2 unresolved moderate optional frontend npm audit findings for `next` and `postcss`.
- Verification evidence: `npm run lint` in `frontend/` exited 0.
- Verification evidence: `npm run build` in `frontend/` exited 0.

## Clean-Context Handoff Notes

- Read the linked task, this progress file, and the matching checkpoint before continuing.
