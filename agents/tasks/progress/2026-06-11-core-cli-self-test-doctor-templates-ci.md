# Progress: Core CLI Self Test Doctor Templates CI

Linked task: `agents/tasks/2026-06-11-core-cli-self-test-doctor-templates-ci.md`
Current status: verified

## Completed Steps

- Created the core improvement task bundle.
- Added regression tests for generated starter self-test, template drift, data-driven stack profiles, explicit brief statuses, doctor, security audit, task validation, and split CI.
- Implemented `site init --self-test`, `site self-test`, `site doctor`, and `security audit`.
- Moved starter overlay files to `src/llm_wiki/templates/site_starter/`.
- Moved stack profile metadata to `agents/harness/stack-profiles.json`.
- Strengthened task validation for linked support files, status transitions, ownership conflicts, and verification evidence.
- Split core CI from optional frontend CI.
- Updated root docs, harness docs, generated starter templates, and wiki log.

## Current Blocker

- None.

## Next Action

- Ready for handoff.

## Files Changed

- Core CLI, generator, stack, readiness, doctor, security, harness validation, tests, docs, templates, CI, and task/wiki records changed.

## Verification Run

- Verification evidence: `python -m unittest discover -s tests` exited 0 with 74 tests OK.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.
- Verification evidence: `python tools/llm_wiki.py site self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py site init C:\tmp\harness88-selftest-20260611-impl --self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py site doctor --json --skip-self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py security audit --json --no-record` exited 0; sandboxed run was unavailable, escalated network run reported 2 unresolved optional frontend audit items non-blockingly.
- Verification evidence: `npm run lint` in `frontend/` exited 0.
- Verification evidence: `npm run build` in `frontend/` exited 0.

## Clean-Context Handoff Notes

- Read the linked task, this progress file, and the matching checkpoint before continuing.
