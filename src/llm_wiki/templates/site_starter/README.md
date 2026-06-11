# Autonomous Site Starter

This project is a clean generated site workspace built from the HARNESS_88 autonomous core. It includes:

- stack-neutral first-run guidance in `START_HERE.md`;
- stack selection state in `STACK.md`;
- Codex agent roles and harness templates in `agents/`;
- durable product and design briefs in `PRODUCT.md` and `DESIGN.md`;
- a local Markdown + SQLite LLM Wiki toolchain under `src/llm_wiki/`.
- an optional bundled Next.js starter/template in `frontend/`.

## First Run

```powershell
python -m unittest discover -s tests
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor
python tools/llm_wiki.py quality --skip-frontend
```

## Development Flow

1. Start with `START_HERE.md`.
2. Choose a stack/fullstack profile and record it in `STACK.md`.
3. Fill in `PRODUCT.md` with the website goal, audience, scope, and acceptance criteria, then set `Status: approved`.
4. Fill in `DESIGN.md` with the visual direction, UX constraints, and component rules, then set `Status: approved`.
5. Create atomic task files with `python tools/llm_wiki.py task create ...`.
6. Implement only from approved briefs, selected stack state, and task ownership.
7. Run core checks with `python tools/llm_wiki.py quality --skip-frontend`.

SQLite files under `data/` are generated state. Delete and rebuild them with `python tools/llm_wiki.py rebuild` whenever needed.
