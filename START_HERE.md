# START HERE

Use this file after a fresh clone of HARNESS_88. It is a practical first-chat script for turning the repository into a site project through agents, approval gates, audit, remediation, and release handoff.

## First Chat

Open Codex or another coding-agent chat in the root of this repository and start with something like:

```text
Read START_HERE.md, AGENTS.md, SITE_INTAKE.md, PRODUCT.md, DESIGN.md, STACK.md, agents/harness/stack-options.md, and agents/workflows/agentic-site-delivery.md.
Check intake and readiness with python tools/llm_wiki.py site intake --json and python tools/llm_wiki.py task readiness --json.
The stack is not selected yet. Run a first-run intake for my site, including country, language, site type, style, ecommerce/catalog/payment/request mode, references, and content sources. Record accepted answers in SITE_INTAKE.md. Then recommend a stack/fullstack profile, update PRODUCT.md, DESIGN.md, and STACK.md, create the first task, and begin the site through the autonomous harness only after approvals are recorded.
```

If you already know the stack profile, say it directly:

```text
Select stack profile next-static for this site. Then update PRODUCT.md, DESIGN.md, and STACK.md, create the first task, and begin implementation through the harness.
```

If you are not sure, ask the agent to run the intake before recommending a stack:

```text
I am not sure which stack/fullstack profile fits. Ask me focused questions about the site goal, country, language, design style, landing vs multi-page scope, ecommerce/catalog needs, online/offline payment, manager-request flow, references, content sources, and launch constraints. Recommend a profile only after that.
```

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

1. Check the core harness:

   ```powershell
   python tools/llm_wiki.py site intake --json
   python tools/llm_wiki.py task readiness --json
   python tools/llm_wiki.py stack status
   python tools/llm_wiki.py site doctor --skip-self-test
   ```

2. Review available profiles:

   ```powershell
   python tools/llm_wiki.py stack list
   ```

3. Select one profile when the project direction is clear:

   ```powershell
   python tools/llm_wiki.py stack select next-static
   ```

4. Fill or update the durable briefs:

   - `PRODUCT.md`: product goal, audience, scope, user jobs, acceptance criteria, and explicit `Status: approved` when accepted.
   - `DESIGN.md`: visual direction, UX constraints, accessibility, component rules, and explicit `Status: approved` when accepted.
   - `STACK.md`: selected stack/fullstack profile and any stack notes.
   - `SITE_INTAKE.md`: required intake fields, `Status: approved`, and `references_status: approved`.

5. Create the first task:

   ```powershell
   python tools/llm_wiki.py task create --title "First Implementation Slice" --objective "Build the first approved site slice from PRODUCT.md, DESIGN.md, and STACK.md."
   ```

6. Start development from that task, keeping progress and checkpoint files updated.

7. Follow the site delivery gates in `agents/workflows/agentic-site-delivery.md`:

   - approve references before serious frontend work;
   - build and show frontend previews before backend expansion when possible;
   - implement backend/data/payment/request flows according to the approved commerce mode;
   - request a product/catalog document before product ingest;
   - run a total agent audit after implementation;
   - fix audit findings through tracked tasks;
   - show the final site for user approval, repeat corrections until accepted;
   - provide VPS publish, update, backup, rollback, and maintenance instructions after final approval.

## Important Rule

HARNESS_88 does not choose Next.js or fullstack by default. The `frontend/` directory is an optional bundled Next.js starter/template. Production implementation starts only after a stack profile is selected or the user explicitly confirms a custom approach.

Use `python tools/llm_wiki.py site doctor` for a unified readiness, wiki, task, frontend, security, and generated-starter self-test report.

Secrets must never be pasted into chat or project files. Use `agents/workflows/secret-broker.md` as the contract for future backend/deployment secret handling.
