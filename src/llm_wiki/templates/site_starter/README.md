# Autonomous Site Starter

This project is a clean generated site workspace built from the HARNESS_88 autonomous core. It includes:

- stack-neutral first-run guidance in `START_HERE.md`;
- machine-checkable first-run intake in `SITE_INTAKE.md`;
- machine-checkable delivery gates in `SITE_GATES.md`;
- stack selection state in `STACK.md`;
- Codex agent roles and harness templates in `agents/`;
- the canonical site delivery workflow in `agents/workflows/agentic-site-delivery.md`;
- the secret-safe backend/deployment contract in `agents/workflows/secret-broker.md`;
- durable product and design briefs in `PRODUCT.md` and `DESIGN.md`;
- a local Markdown + SQLite LLM Wiki toolchain under `src/llm_wiki/`.
- an optional bundled Next.js starter/template in `frontend/`.

## First Run

```powershell
python -m unittest discover -s tests
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor
python tools/llm_wiki.py quality --skip-frontend
```

## Development Flow

1. Start with `START_HERE.md`.
2. Run the first-run intake and record accepted answers in `SITE_INTAKE.md`.
3. Choose a stack/fullstack profile and record it in `STACK.md`.
4. Fill in `PRODUCT.md` with the website goal, audience, scope, and acceptance criteria, then set `Status: approved`.
5. Include commerce mode in the brief: no commerce, catalog only, online payment, offline payment, request to manager, or mixed.
6. Fill in `DESIGN.md` with the visual direction, UX constraints, reference expectations, and component rules, then set `Status: approved`.
7. Approve user-provided or agent-proposed reference sites and set `references_status: approved` in `SITE_INTAKE.md` before serious frontend implementation; agent-proposed reference searches include Dribbble, Behance, and Awwwards.
8. Create atomic task files with `python tools/llm_wiki.py task create ...`.
9. Implement only from approved intake, approved briefs, selected stack state, approved references, and task ownership.
10. Show frontend previews for approval, then implement backend/data/payment/request flows as approved.
11. Run total agent audit, fix findings through tracked tasks, and show the final site for user approval before publish instructions.
12. Record delivery gate evidence in `SITE_GATES.md` and check it with `python tools/llm_wiki.py site gates --json`.
13. Run core checks with `python tools/llm_wiki.py quality --skip-frontend`.

SQLite files under `data/` are generated state. Delete and rebuild them with `python tools/llm_wiki.py rebuild` whenever needed.
