# Agent Site Tooling

This clean project starts with the portable, stack-neutral site-development harness only.

## Current Project State

- Workspace: `<project-root>`
- Stack state: `STACK.md` starts unselected and must be updated before production implementation.
- Intake state: `SITE_INTAKE.md` starts draft and must record accepted first-run intake decisions before production implementation.
- Reference analysis state: `SITE_REFERENCES.md` starts draft and must record bounded crawl, screenshots, Figma, UX/visual analysis, and user approval before serious frontend implementation.
- Delivery gate state: `SITE_GATES.md` starts draft and must record preview approval, backend/data readiness, audit, remediation, final approval, and publish handoff before release.
- No frontend app is bundled. Stack is selected through dialogue from the user's goals, site type, content model, backend/data needs, integrations, deployment expectations, and maintenance constraints.
- Canonical LLM Wiki: `wiki/`
- Generated SQLite state: `data/wiki.sqlite`

## Hard Rules

- Do not begin website implementation until `STACK.md` has a selected profile or the user explicitly confirms a custom approach.
- Before stack selection, recommend 2-4 stack options with languages, frameworks, services, pros, cons, operational complexity, and best-fit use cases; wait for user approval.
- Before publish/operate planning, ask whether the site should publish to VPS/VDS or managed hosting, explain pros and cons of each, and recommend the better option from the user's operations, budget, traffic, backend, and maintenance answers.
- Do not begin website implementation until `SITE_INTAKE.md` has `Status: approved`.
- Do not begin website implementation until `PRODUCT.md` and `DESIGN.md` have `Status: approved`, or equivalent approved wiki decisions define the product and design direction.
- Do not begin serious frontend implementation until `references_status: approved` is set in `SITE_INTAKE.md`, `SITE_REFERENCES.md` is `Status: approved`, and `python tools/llm_wiki.py site references --json` reports complete reference analysis.
- Reference analysis uses bounded crawl by default: same-origin public sitemap/nav/footer pages, max 50 normalized pages per reference, with login/private/admin/cart/account/form-submit flows excluded unless explicitly approved.
- Reference evidence must include desktop/mobile screenshots in `raw/assets/references/manifest.json`, UX/visual analysis, and a Figma design reference artifact.
- The main chat must start site-delivery work through `python tools/llm_wiki.py conductor start` and visibly state `Conductor online`.
- Conductor cannot self-assign worker phases. Use `python tools/llm_wiki.py conductor route --phase <phase>` and `python tools/llm_wiki.py conductor delegate ...` before reference, design, frontend, backend, QA, release, or wiki closeout worker work.
- Open worker-phase tasks require a non-Conductor role owner and `Delegation packet: agents/delegations/<task>.md`; `python tools/llm_wiki.py task validate --strict` enforces this.
- Ask questions in the user's language from the latest user message; `SITE_INTAKE.md` `language` records the site language, not necessarily the conversation language.
- If references are missing or the user cannot choose them, delegate Reference Research and include `https://dribbble.com/`, `https://www.behance.net/`, and `https://www.awwwards.com/` in the source scope.
- For site design work, use `agents/protocols/design-resources.md` to grant huashu-design, impeccable, ui-ux-pro-max, GSAP, Canva, or Creative Production only when the role and task need them.
- Use agent-first delegation for substantial research, design, implementation, QA, release, and wiki closeout. If no suitable role or tooling grant exists, update the role/tooling contract before delegating.
- Do not publish or provide final deployment instructions until `SITE_GATES.md` records completed audit/remediation/final approval gates and publish/operate handoff is complete.
- Keep secrets in environment variables only.
- Never ask the user to paste secrets into chat. Follow `agents/workflows/secret-broker.md` for secret-backed backend/deployment setup.
- Treat `data/wiki.sqlite` as generated state.
- Preserve files under `raw/` during ingest.
- For multi-agent website work, read `agents/TEAM.md` before delegation.
- Real implementation requires a concrete task file in `agents/tasks/` or an equivalent approved plan.
- Follow `agents/protocols/tooling-onboarding.md` for first-run tools/skills/plugins audit and permission prompts.
- Run `python tools/llm_wiki.py tools audit` after download or environment changes. The audit reports missing tools/skills/plugins and asks permission before installing local tools, downloading skills from GitHub, or connecting Codex plugins.
- Before downloading any GitHub-backed tool, skill, or MCP resource, confirm its exact URL is recorded in `agents/resources/tooling-sources.json` and approved by the user. If the URL is blank or missing, ask for the correct repository link first.

## Optional Resources

Project-local design and AI skill packs are intentionally not bundled in this generated starter. Install or copy them only when a task explicitly needs them, then record the decision in the wiki.

Use `agents/resources/tooling-sources.json` as the registry for external source links. A blank GitHub URL means no download is allowed until the user approves the exact repository.

## Stack Scaffolding

HARNESS_88 does not include a prebuilt frontend. After intake and stack recommendation, scaffold stack-specific files only in an approved task for the selected profile or custom stack.

The deployment discussion must explicitly compare VPS/VDS vs hosting:

- VPS/VDS: more control over runtime, logs, backups, reverse proxy, and custom services; more server administration, patching, monitoring, and incident response.
- Managed hosting: faster setup, previews, CDN/HTTPS, and lower maintenance; less low-level control, provider limits, and possible vendor lock-in.

## Default Checks

```powershell
python -m unittest discover -s tests
python tools/llm_wiki.py conductor start
python tools/llm_wiki.py tools audit --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py stack status
python tools/llm_wiki.py conductor route --phase reference-analysis
python tools/llm_wiki.py site doctor --skip-self-test
python tools/llm_wiki.py quality --skip-frontend
```
