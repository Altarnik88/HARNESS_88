# Autonomous Site Starter

This project is a clean generated site workspace built from the HARNESS_88 autonomous core. It includes:

- stack-neutral first-run guidance in `START_HERE.md`;
- machine-checkable first-run intake in `SITE_INTAKE.md`;
- strict machine-checkable reference analysis in `SITE_REFERENCES.md`;
- machine-checkable delivery gates in `SITE_GATES.md`;
- stack selection state in `STACK.md`;
- Codex agent roles and harness templates in `agents/`;
- the canonical site delivery workflow in `agents/workflows/agentic-site-delivery.md`;
- executable Conductor runtime routing with `python tools/llm_wiki.py conductor start/route/delegate`;
- the secret-safe backend/deployment contract in `agents/workflows/secret-broker.md`;
- durable product and design briefs in `PRODUCT.md` and `DESIGN.md`;
- a local Markdown + SQLite LLM Wiki toolchain under `src/llm_wiki/`.

No frontend app is bundled. Stack is selected through dialogue from the user's goals, site type, content model, backend/data needs, integrations, deployment expectations, and maintenance constraints.

## First Run

```powershell
python -m unittest discover -s tests
python tools/llm_wiki.py conductor start
python tools/llm_wiki.py tools audit --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py conductor route --phase reference-analysis
python tools/llm_wiki.py site doctor
python tools/llm_wiki.py quality --skip-frontend
```

## Development Flow

1. Start with `START_HERE.md`.
2. Run the first-run intake and record accepted answers in `SITE_INTAKE.md`.
3. Recommend 2-4 stack/fullstack options with languages, frameworks, services, pros, cons, operational complexity, and best-fit use cases; wait for user approval or a custom stack before recording the choice in `STACK.md`.
4. Fill in `PRODUCT.md` with the website goal, audience, scope, and acceptance criteria, then set `Status: approved`.
5. Include commerce mode in the brief: no commerce, catalog only, online payment, offline payment, request to manager, or mixed.
6. Fill in `DESIGN.md` with the visual direction, UX constraints, reference expectations, and component rules, then set `Status: approved`.
7. Approve user-provided or agent-proposed reference sites and set `references_status: approved` in `SITE_INTAKE.md`; agent-proposed reference searches include Dribbble, Behance, and Awwwards.
8. Complete `SITE_REFERENCES.md` before serious frontend implementation: bounded crawl, desktop/mobile screenshots, Figma reference artifact, UX/visual analysis, and user approval. Use `python tools/llm_wiki.py conductor delegate --phase reference-analysis ...` before assigning the worker task.
9. Ask whether publication should target VPS/VDS or managed hosting, explain pros and cons of each, and recommend the better option from the user's operational, budget, traffic, backend, and maintenance answers.
10. Create atomic task files with `python tools/llm_wiki.py task create ...`.
11. Scaffold and implement only from approved intake, approved briefs, selected stack state, approved reference analysis, selected deployment direction, and task ownership.
12. Show frontend previews for approval, then implement backend/data/payment/request flows as approved.
13. Run total agent audit, fix findings through tracked tasks, and show the final site for user approval before publish instructions.
14. Record delivery gate evidence in `SITE_GATES.md` and check it with `python tools/llm_wiki.py site gates --json`.
15. Run core checks with `python tools/llm_wiki.py quality --skip-frontend`.

SQLite files under `data/` are generated state. Delete and rebuild them with `python tools/llm_wiki.py rebuild` whenever needed.

Run `python tools/llm_wiki.py tools audit` after download or environment changes. It reports available and missing local tools, Codex skills, plugins, and MCP-related capabilities, then asks permission before any install, GitHub skill download, or Codex plugin connection.

GitHub-backed source links are tracked in `agents/resources/tooling-sources.json`. If a required resource has no recorded URL, the agent must ask the user to provide or approve the exact repository before downloading it.

Site design resources are defined in `agents/protocols/design-resources.md`, including huashu-design, impeccable, ui-ux-pro-max, GSAP, and Canva.
