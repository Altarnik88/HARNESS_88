# Progress: No Bundled Frontend Stack Selection

Linked task: `agents/tasks/2026-06-12-no-bundled-frontend-stack-selection.md`
Current status: verified

## Completed Steps

- Wrote RED tests requiring generated projects to omit `frontend/`.
- Wrote RED tests requiring stack profiles to expose languages, frameworks, services, pros, cons, scaffold policy, selection questions, and deployment options.
- Wrote RED tests requiring first-run docs to include VPS/VDS vs hosting guidance with pros and cons.
- Removed root `frontend/` and `src/llm_wiki/templates/site_starter/frontend/`.
- Removed `frontend` from generated project copy paths.
- Deleted obsolete frontend starter tests.
- Updated stack profile metadata, CLI JSON output, and human `stack list` output.
- Updated root and generated-starter docs to say no frontend app is bundled and stack/deployment are selected through dialogue.
- Added VPS/VDS vs managed hosting tradeoffs and recommendation prompts.
- Updated release notes, review queue, and wiki log.

## Current Blocker

- None.

## Next Action

- Run final task evidence after this evidence update.
- Commit and push the verified branch if all gates remain clean.

## Files Changed

- Removed `frontend/`.
- Removed `src/llm_wiki/templates/site_starter/frontend/`.
- Updated `src/llm_wiki/site_generator.py`, `src/llm_wiki/stack.py`, and `src/llm_wiki/cli.py`.
- Updated stack metadata, root docs, generated-starter templates, release notes, task evidence, and wiki review/log files.
- Updated tests for generator, stack neutrality, stack CLI, quality, and security behavior.

## Verification Run

- RED: `python -m unittest tests.test_site_generator tests.test_stack_neutral` failed before implementation because generated projects still contained `frontend/` and docs still mentioned the bundled starter.
- RED: `python -m unittest tests.test_stack_cli` failed before implementation because stack profiles lacked tradeoff/deployment metadata and CLI output lacked pros/cons.
- GREEN: `python -m unittest tests.test_site_generator tests.test_stack_neutral` exited 0 after implementation.
- GREEN: `python -m unittest tests.test_stack_cli tests.test_quality tests.test_security` exited 0 after implementation.
- `python -m unittest discover -s tests` exited 0 with 146 tests.
- `python tools/llm_wiki.py quality --skip-frontend` exited 0: Python tests, wiki rebuild, and strict lint passed.
- `python tools/llm_wiki.py security audit --json --no-record --blocking` exited 0 with `status: "skipped"` and `unresolved_count: 0` because no `frontend/package.json` exists.
- `python tools/llm_wiki.py task validate --strict` exited 0 with no validation issues.

## Clean-Context Handoff Notes

- `STACK.md` remains unselected.
- `PRODUCT.md`, `SITE_INTAKE.md`, `SITE_REFERENCES.md`, and `SITE_GATES.md` were not edited.
- `DESIGN.md` remains `Status: draft`; wording was updated only to remove the obsolete bundled frontend reference.
- Future scaffolded frontends/backends must run their own dependency audit after stack approval.
