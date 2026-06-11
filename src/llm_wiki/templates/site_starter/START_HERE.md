# START HERE

Use this file after a fresh clone of HARNESS_88. It is a practical first-chat script for turning the repository into a site project through agents, approval gates, audit, remediation, and release handoff.

## First Chat

Open Codex or another coding-agent chat in the root of this repository and start with something like:

```text
Read START_HERE.md, AGENTS.md, SITE_INTAKE.md, PRODUCT.md, DESIGN.md, STACK.md, agents/harness/stack-options.md, and agents/workflows/agentic-site-delivery.md.
Check intake and readiness with python tools/llm_wiki.py site intake --json and python tools/llm_wiki.py task readiness --json.
The stack is not selected yet. Run a first-run intake for my site, including country, language, site type, style, ecommerce/catalog/payment/request mode, references, and content sources. Record accepted answers in SITE_INTAKE.md. Then recommend a stack/fullstack profile, update PRODUCT.md, DESIGN.md, and STACK.md, create the first task, and begin the site through the autonomous harness only after approvals are recorded.
```

If you are not sure, ask the agent to run the intake before recommending a stack.

## Required Intake Topics

Before implementation, the agent must collect or explicitly mark unknown:

- site goal, audience, country/market, language, and launch constraints;
- site type: landing, multi-page, catalog, ecommerce, web app, or custom;
- commerce mode: no commerce, catalog only, online payment, offline payment, request to manager, or mixed;
- desired design style, visual constraints, and references;
- required pages, forms, integrations, content sources, analytics/SEO needs, deployment expectations, backend/data/auth/admin/integration needs, and product/catalog document status.

If the user has no reference sites, the agent should propose relevant examples based on the intake and wait for approval before serious frontend implementation.

Record machine-checkable intake state in `SITE_INTAKE.md`. `references_status: approved` is required before serious frontend implementation.

## First-Run Checklist

```powershell
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor
```

After selecting a profile, update `PRODUCT.md`, `DESIGN.md`, and `STACK.md`, create the first task, and begin development from that task.

Follow `agents/workflows/agentic-site-delivery.md` for reference approval, frontend preview approval, backend/data work, optional product ingest, total audit, remediation, final user approval, and VPS publish/maintenance handoff.

Secrets must never be pasted into chat or project files. Use `agents/workflows/secret-broker.md` as the contract for future backend/deployment secret handling.
