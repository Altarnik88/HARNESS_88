# HARNESS_88 Release Notes

## v0.1.0 - Stack-neutral core release

Status: published and verified.

HARNESS_88 v0.1.0 publishes the project as a stack-neutral core engine and template infrastructure for building sites from scratch. It is not a completed site, does not bundle a frontend app, does not select Next.js or any other stack by default, does not approve a product brief, does not approve a design brief, and does not begin frontend/site implementation.

This release is the operating layer for agent-driven site delivery. It gives a new project a controlled path from vague request to approved implementation: intake, stack recommendation, product/design contracts, reference analysis, task ownership, quality checks, remediation, final approval, and publish/operate handoff.

### Problems addressed

- Agents starting frontend work before the site goal, stack, references, product, and design are approved.
- Lost decisions after context resets or agent handoffs.
- Unclear stack and hosting choices that get treated as defaults instead of user-approved decisions.
- Weak reference work without bounded evidence, screenshots, UX/visual analysis, or Figma handoff.
- Large site work without explicit task ownership, progress tracking, review evidence, and remediation loops.
- Publish instructions being provided before audit evidence and final user approval.
- Secret values being copied into project files or agent configuration.

### Release contents

- Core HARNESS_88 workflow, task, wiki, gate, and diagnostics tooling.
- Stack-neutral onboarding and approval gates for new site projects.
- Dialog-driven stack recommendation metadata with languages, frameworks, services, pros, cons, scaffold policy, and selection questions.
- Deployment recommendation guidance that asks the client about VPS/VDS vs hosting, explains pros and cons, and recommends a publication target from the client's answers.
- Generated site starters that contain no prebuilt frontend app and no preselected stack.
- Secret handling guidance that records variable names and provider metadata only; no secret values are requested, stored, or committed.

### What intentionally did not ship

- No finished website.
- No bundled frontend application.
- No preselected Next.js, fullstack, backend, database, CMS, payment, or hosting provider.
- No automatic dependency installation, plugin connection, MCP setup, or GitHub-backed resource download.
- No approval state changes for `STACK.md`, `PRODUCT.md`, `DESIGN.md`, `SITE_INTAKE.md`, `SITE_REFERENCES.md`, or `SITE_GATES.md`.
- No stored secrets.

### New project flow

1. Start from `START_HERE.md`.
2. Run the read-only tools/skills/plugins audit so the agent can report available capabilities and ask before installing or connecting anything.
3. Complete site intake: goal, audience, country, language, site type, content sources, catalog/ecommerce/payment/request needs, backend/data/admin/integration needs, and launch constraints.
4. Review 2-4 recommended stack/fullstack options with pros, cons, operational complexity, scaffold policy, and best-fit use cases.
5. Approve one stack profile or explicitly provide a custom stack before `STACK.md` is updated.
6. Approve the product and design direction before `PRODUCT.md` and `DESIGN.md` become implementation contracts.
7. Approve reference sites or let Reference Research propose options from Dribbble, Behance, Awwwards, competitors, and market examples.
8. Complete `SITE_REFERENCES.md` with bounded crawl evidence, desktop/mobile screenshots, UX/visual analysis, Figma reference artifact, and explicit user approval.
9. Discuss VPS/VDS versus managed hosting, explain tradeoffs, and record the recommended deployment direction from the user's answers.
10. Create tracked task files and build only from approved intake, approved briefs, selected stack state, approved reference analysis, selected deployment direction, and task ownership.
11. Run previews, total audit, remediation tasks, final user approval, and publish/operate handoff before release instructions for the finished site.

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
