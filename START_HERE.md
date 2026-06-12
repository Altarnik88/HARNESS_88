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
- required pages, forms, integrations, content sources, analytics/SEO needs, deployment expectations, backend/data/auth/admin/integration needs, product/catalog document status, and VPS/VDS vs hosting preference.

When recommending deployment, explain these tradeoffs in plain language:

- VPS/VDS: more control over runtime, logs, backups, reverse proxy rules, colocated services, and custom server setup; more responsibility for updates, security patches, monitoring, backups, incidents, and server administration.
- Managed hosting: faster setup, previews, CDN/HTTPS, rollback, and lower maintenance; less low-level control, provider/runtime limits, possible vendor lock-in, and pricing constraints.

Recommend one option after asking about budget, expected traffic, technical maintenance owner, backend/runtime needs, uptime expectations, backups, and whether the client wants server control or simpler operations.

If the user has no reference sites or cannot choose them, the Conductor delegates Reference Research to propose relevant examples based on the intake. Agent-proposed searches must include `https://dribbble.com/`, `https://www.behance.net/`, and `https://www.awwwards.com/`, then wait for approval before serious frontend implementation.

Record machine-checkable intake state in `SITE_INTAKE.md`. `references_status: approved` and complete `SITE_REFERENCES.md` evidence are required before serious frontend implementation.

## First-Run Checklist

1. Check the core harness:

   ```powershell
   python tools/llm_wiki.py conductor start
   python tools/llm_wiki.py tools audit --json
   python tools/llm_wiki.py site intake --json
   python tools/llm_wiki.py site references --json
   python tools/llm_wiki.py site gates --json
   python tools/llm_wiki.py task readiness --json
   python tools/llm_wiki.py stack status
   python tools/llm_wiki.py conductor route --phase reference-analysis
   python tools/llm_wiki.py site doctor --skip-self-test
   ```

2. Review available profiles:

   ```powershell
   python tools/llm_wiki.py stack list
   ```

3. Recommend stack and deployment options when the project direction is clear:

   ```text
   Recommend 2-4 stack options with languages, frameworks, services, pros, cons, operational complexity, and best-fit use cases. Wait for the user to approve one option or propose a custom stack before running `python tools/llm_wiki.py stack select next-static` or the approved profile name.
   Ask about VPS/VDS vs hosting, explain pros and cons, then recommend the better publication target from the user's answers.
   ```

4. Select one profile after explicit approval:

   ```powershell
   python tools/llm_wiki.py stack select next-static
   ```

5. Fill or update the durable briefs:

   - `PRODUCT.md`: product goal, audience, scope, user jobs, acceptance criteria, and explicit `Status: approved` when accepted.
   - `DESIGN.md`: visual direction, UX constraints, accessibility, component rules, and explicit `Status: approved` when accepted.
   - `STACK.md`: selected stack/fullstack profile and any stack notes.
   - `SITE_INTAKE.md`: required intake fields, `Status: approved`, and `references_status: approved`.
   - `SITE_REFERENCES.md`: bounded crawl, screenshot manifest, Figma reference artifact, UX/visual analysis, and user approval.

6. Create the first task:

   ```powershell
   python tools/llm_wiki.py task create --title "First Implementation Slice" --objective "Build the first approved site slice from PRODUCT.md, DESIGN.md, and STACK.md."
   ```

7. Start development from that task, keeping progress and checkpoint files updated.

8. Follow the site delivery gates in `agents/workflows/agentic-site-delivery.md`:

   - keep the main chat in Conductor mode with `python tools/llm_wiki.py conductor start`;
   - create delegation packets with `python tools/llm_wiki.py conductor delegate` before worker phases;
   - approve references and complete the strict reference-analysis gate before serious frontend work;
   - build and show frontend previews before backend expansion when possible;
   - implement backend/data/payment/request flows according to the approved commerce mode;
   - request a product/catalog document before product ingest;
   - run a total agent audit after implementation;
   - fix audit findings through tracked tasks;
   - show the final site for user approval, repeat corrections until accepted;
   - record reference evidence in `SITE_REFERENCES.md` and check it with `python tools/llm_wiki.py site references --json`;
   - record delivery gate evidence in `SITE_GATES.md` and check it with `python tools/llm_wiki.py site gates --json`;
   - provide approved VPS/VDS or managed hosting publish, update, backup, rollback, and maintenance instructions after final approval.

## Important Rule

HARNESS_88 does not choose Next.js, fullstack, VPS/VDS, or hosting by default. No frontend app is bundled. Stack is selected through dialogue, and production implementation starts only after a stack profile is selected or the user explicitly confirms a custom approach.

Use `python tools/llm_wiki.py site doctor --skip-self-test` for fast unified readiness, wiki, task, frontend, security, and tooling diagnostics. Reserve `python tools/llm_wiki.py site self-test` for generator or starter-template changes.

Secrets must never be pasted into chat or project files. Use `agents/workflows/secret-broker.md` as the contract for future backend/deployment secret handling.

## Tooling Onboarding

After downloading HARNESS_88, run `python tools/llm_wiki.py tools audit --json` before serious work. The audit is read-only and reports available and missing local tools, Codex skills, plugins, MCP-related capabilities, and `next_actions`. The agent must ask permission before installing local tools, downloading GitHub-backed skills/resources, connecting Codex plugins/MCP, or adding frontend dependencies.

Follow `agents/protocols/tooling-onboarding.md` for the exact permission flow from `tools audit --json` `next_actions` to user approval.

GitHub-backed resource links are recorded in `agents/resources/tooling-sources.json`. Before any GitHub download, the exact repository URL must be present there and approved by the user. If the URL is blank or missing, the agent asks the user for the correct link first.
