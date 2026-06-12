# START HERE

Use this file after a fresh clone of HARNESS_88. It is a practical first-chat script for turning the repository into a site project through agents, approval gates, audit, remediation, and release handoff.

## First Chat

Open Codex or another coding-agent chat in the root of this repository and start with something like:

```text
Read START_HERE.md, AGENTS.md, SITE_INTAKE.md, SITE_GATES.md, PRODUCT.md, DESIGN.md, STACK.md, agents/harness/stack-options.md, and agents/workflows/agentic-site-delivery.md.
Check local tools/skills/plugins, intake, gates, and readiness with python tools/llm_wiki.py tools audit --json, python tools/llm_wiki.py site intake --json, python tools/llm_wiki.py site gates --json, and python tools/llm_wiki.py task readiness --json.
The stack is not selected yet. Run a first-run intake for my site, asking questions in my language, including country, site language, site type, style, ecommerce/catalog/payment/request mode, references, and content sources. Record accepted answers in SITE_INTAKE.md. Then recommend a stack/fullstack profile, update PRODUCT.md, DESIGN.md, and STACK.md, create the first task, and begin the site through the autonomous harness only after approvals are recorded.
```

If you are not sure, ask the agent to run the intake before recommending a stack.

## Required Intake Topics

Before implementation, the agent must collect or explicitly mark unknown:

- site goal, audience, country/market, language, and launch constraints;
- site type: landing, multi-page, catalog, ecommerce, web app, or custom;
- commerce mode: no commerce, catalog only, online payment, offline payment, request to manager, or mixed;
- desired design style, visual constraints, and references;
- required pages, forms, integrations, content sources, analytics/SEO needs, deployment expectations, backend/data/auth/admin/integration needs, and product/catalog document status.

If the user has no reference sites or cannot choose them, the Conductor delegates Reference Research to propose relevant examples based on the intake. Agent-proposed searches must include `https://dribbble.com/`, `https://www.behance.net/`, and `https://www.awwwards.com/`, then wait for approval before serious frontend implementation.

Record machine-checkable intake state in `SITE_INTAKE.md`. `references_status: approved` is required before serious frontend implementation.

## First-Run Checklist

```powershell
python tools/llm_wiki.py tools audit --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor
```

After selecting a profile, update `PRODUCT.md`, `DESIGN.md`, and `STACK.md`, create the first task, and begin development from that task.

Follow `agents/workflows/agentic-site-delivery.md` for reference approval, frontend preview approval, backend/data work, optional product ingest, total audit, remediation, final user approval, and VPS publish/maintenance handoff. Record the machine-checkable delivery state in `SITE_GATES.md`.

Secrets must never be pasted into chat or project files. Use `agents/workflows/secret-broker.md` as the contract for future backend/deployment secret handling.

## Tooling Onboarding

After downloading HARNESS_88, run `python tools/llm_wiki.py tools audit` before serious work. The audit reports available and missing local tools, Codex skills, plugins, and MCP-related capabilities. It asks permission before installing local tools, downloading skills from GitHub, or connecting Codex plugins.
