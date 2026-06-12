# HARNESS_88 Release Notes

## v0.1.0 - Release ready

Status: verified for release preparation.

HARNESS_88 v0.1.0 publishes the project as a stack-neutral core engine and template infrastructure for building sites from scratch. It is not a completed site, does not select a stack, does not approve a product brief, does not approve a design brief, and does not begin frontend/site implementation.

### Release contents

- Core HARNESS_88 workflow, task, wiki, gate, and diagnostics tooling.
- Stack-neutral onboarding and approval gates for new site projects.
- Dialog-driven stack recommendation metadata with languages, frameworks, services, pros, cons, scaffold policy, and selection questions.
- Deployment recommendation guidance that asks the client about VPS/VDS vs hosting, explains pros and cons, and recommends a publication target from the client's answers.
- Generated site starters that contain no prebuilt frontend app and no preselected stack.
- Secret handling guidance that records variable names and provider metadata only; no secret values are requested, stored, or committed.

### New project flow

- New projects start with intake, stack recommendation, explicit stack approval, references, product/design approvals, and tracked tasks.
- Stack-specific frontend/backend files are scaffolded only after the user approves a stack profile or custom stack and an approved task records the target directory and commands.
- Publication planning waits until VPS/VDS or managed hosting is discussed, tradeoffs are explained, a target is recommended, and final delivery gates are recorded.

### Verification

- `python -m unittest discover -s tests` passed with 146 tests.
- `python tools/llm_wiki.py quality --skip-frontend` passed: Python tests, wiki rebuild, and strict lint all succeeded.
- `python tools/llm_wiki.py security audit --json --no-record --blocking` exited 0 with `status: "skipped"` and `unresolved_count: 0` because no `frontend/package.json` exists in the core repository.
- `python tools/llm_wiki.py task validate --strict` passed.

### Security and secrets

- No frontend app is bundled or preselected.
- No npm dependency audit target remains in the core repository until a stack-specific project is scaffolded by an approved task.
- Future scaffolded frontends or backends must run their own dependency audit after stack approval.
- No secrets are included or requested.
