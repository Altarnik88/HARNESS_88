# START HERE

Use this file after a fresh clone of HARNESS_88. It is a practical first-chat script for turning the repository into a site project through agents, approval gates, audit, remediation, and release handoff.

## First Chat

Open Codex or another coding-agent chat in the root of this repository and start with something like:

```text
Start as HARNESS_88 Conductor. Run python tools/llm_wiki.py conductor start and begin your first response with "Conductor online".
Read START_HERE.md, AGENTS.md, SITE_INTAKE.md, SITE_REFERENCES.md, SITE_GATES.md, PRODUCT.md, DESIGN.md, STACK.md, agents/protocols/conductor-runtime.md, agents/protocols/tooling-onboarding.md, agents/harness/stack-options.md, and agents/workflows/agentic-site-delivery.md.
Check local tools/skills/plugins, intake, reference analysis, gates, and readiness with python tools/llm_wiki.py tools audit --json, python tools/llm_wiki.py site intake --json, python tools/llm_wiki.py site references --json, python tools/llm_wiki.py site gates --json, python tools/llm_wiki.py task readiness --json, and python tools/llm_wiki.py conductor route --phase reference-analysis --json.
The stack is not selected yet. Run a first-run intake for my site, asking questions in my language, including country, site language, site type, style, ecommerce/catalog/payment/request mode, references, content sources, backend/data/admin/integration needs, and deployment expectations. Record accepted answers in SITE_INTAKE.md. Then recommend 2-4 stack/fullstack options with languages, frameworks, services, pros, cons, operational complexity, and best-fit use cases. Ask whether publication should use VPS/VDS vs hosting, explain pros and cons of each, and recommend the better option from my answers. Wait for my approval before updating PRODUCT.md, DESIGN.md, and STACK.md, creating the first task, or beginning the site through the autonomous harness.
```

If you are not sure, ask the agent to run the intake before recommending a stack.

## Required Intake Topics

Before implementation, the agent must collect or explicitly mark unknown:

- site goal, audience, country/market, language, and launch constraints;
- site type: landing, multi-page, catalog, ecommerce, web app, or custom;
- commerce mode: no commerce, catalog only, online payment, offline payment, request to manager, or mixed;
- desired design style, visual constraints, and references;
- required pages, forms, integrations, content sources, analytics/SEO needs, deployment expectations, backend/data/auth/admin/integration needs, product/catalog document status, and VPS/VDS vs hosting preference.

When recommending deployment, explain these tradeoffs in plain language:

- VPS/VDS: more control over runtime, logs, backups, reverse proxy rules, colocated services, and custom server setup; more responsibility for updates, security patches, monitoring, backups, incidents, and server administration.
- Managed hosting: faster setup, previews, CDN/HTTPS, rollback, and lower maintenance; less low-level control, provider/runtime limits, possible vendor lock-in, and pricing constraints.

Recommend one option after asking about budget, expected traffic, technical maintenance owner, backend/runtime needs, uptime expectations, backups, and whether the client wants server control or simpler operations.

If the user has no reference sites or cannot choose them, the Conductor delegates Reference Research to propose relevant examples based on the intake. Agent-proposed searches must include `https://dribbble.com/`, `https://www.behance.net/`, and `https://www.awwwards.com/`, then wait for approval before serious frontend implementation.

Record machine-checkable intake state in `SITE_INTAKE.md`. `references_status: approved` and complete `SITE_REFERENCES.md` evidence are required before serious frontend implementation.

## First-Run Checklist

```powershell
python tools/llm_wiki.py conductor start
python tools/llm_wiki.py tools audit --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py conductor route --phase reference-analysis
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor --skip-self-test
```

Reserve `python tools/llm_wiki.py site self-test` for generator changes.

After selecting a profile, update `PRODUCT.md`, `DESIGN.md`, and `STACK.md`, create the first task, and begin development from that task.

Before selecting a profile, recommend 2-4 stack options with languages, frameworks, services, pros, cons, operational complexity, and best-fit use cases. Wait for the user to approve one option or propose a custom stack before running `python tools/llm_wiki.py stack select next-static` or the approved profile name.

Ask about VPS/VDS vs hosting, explain pros and cons, then recommend the better publication target from the user's answers.

Follow `agents/workflows/agentic-site-delivery.md` and `agents/protocols/conductor-runtime.md` for reference approval, strict reference analysis, frontend preview approval, backend/data work, optional product ingest, total audit, remediation, final user approval, and approved VPS/VDS or managed hosting publish/maintenance handoff. Create `agents/delegations/` packets before worker phases. Record machine-checkable reference analysis in `SITE_REFERENCES.md` and delivery state in `SITE_GATES.md`.

Secrets must never be pasted into chat or project files. Use `agents/workflows/secret-broker.md` as the contract for future backend/deployment secret handling.

## Tooling Onboarding

After downloading HARNESS_88, run `python tools/llm_wiki.py tools audit` before serious work. The audit reports available and missing local tools, Codex skills, plugins, and MCP-related capabilities. It asks permission before installing local tools, downloading skills from GitHub, or connecting Codex plugins.

Follow `agents/protocols/tooling-onboarding.md` for the exact permission flow from `tools audit --json` `next_actions` to user approval.

GitHub-backed resource links are recorded in `agents/resources/tooling-sources.json`. Before any GitHub download, the exact repository URL must be present there and approved by the user. If the URL is blank or missing, the agent asks the user for the correct link first.
