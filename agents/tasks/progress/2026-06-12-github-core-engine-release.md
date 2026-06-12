# Progress: GitHub Core Engine Release

Linked task: `agents/tasks/2026-06-12-github-core-engine-release.md`
Current status: verified

## Completed Steps

- Confirmed `core_harness88_improvement_prompt.txt` was untracked and not referenced by repo files.
- Deleted `core_harness88_improvement_prompt.txt` after user approval because it did not affect core HARNESS_88 behavior.
- Ran real `npm audit --json` in the former `frontend/` with network approval and documented the original Next/PostCSS blocker.
- Removed the bundled `frontend/` starter from the HARNESS_88 core release scope through the no-bundled-frontend task.
- Updated release notes to describe HARNESS_88 as stack-neutral core engine/template infrastructure, not a completed site.
- Recorded that no frontend app is bundled or preselected.
- Added stack recommendation and VPS/VDS vs hosting recommendation guidance.
- Closed the old frontend audit blocker in `wiki/review.md`.

## Verification Run

- `python -m unittest discover -s tests` exited 0 with 146 tests.
- `python tools/llm_wiki.py quality --skip-frontend` exited 0: Python tests, wiki rebuild, and strict lint passed.
- `python tools/llm_wiki.py security audit --json --no-record --blocking` exited 0 with `status: "skipped"` and `unresolved_count: 0` because no `frontend/package.json` exists.
- `python tools/llm_wiki.py task validate --strict` exited 0 with no validation issues.

## Residual Risk

- None for the core release blocker. Future scaffolded frontend/backend projects must run their own dependency audits after stack approval.

## Next Action

- Run `python tools/llm_wiki.py task evidence --json` after this evidence update.
- If task evidence is clean, commit and push the verified release-preparation branch.
- Merge/tag/GitHub release publication remains a separate release execution step.

## Files Changed

- Updated `RELEASE_NOTES.md`.
- Updated this release task bundle.
- Updated `wiki/review.md`.
- Updated `wiki/log.md`.

## Review Evidence

- Stack remains unselected.
- Site intake, site references, product, design, and site gates were not moved to approved.
- Frontend/site implementation was not started.
- No secret values were requested, displayed, written, or stored.
