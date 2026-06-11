# Autonomous Site Starter

This project is a clean generated site workspace. It includes:

- a Next.js frontend in `frontend/`;
- Codex agent roles and harness templates in `agents/`;
- durable product and design briefs in `PRODUCT.md` and `DESIGN.md`;
- a local Markdown + SQLite LLM Wiki toolchain under `src/llm_wiki/`.

## First Run

```powershell
python tools/llm_wiki.py task readiness
python -m unittest discover -s tests
cd frontend
npm install
npm run lint
```

## Development Flow

1. Fill in `PRODUCT.md` with the website goal, audience, scope, and acceptance criteria.
2. Fill in `DESIGN.md` with the visual direction, UX constraints, and component rules.
3. Create atomic task files with `python tools/llm_wiki.py task create ...`.
4. Implement only from approved briefs and task ownership.
5. Run `python tools/llm_wiki.py quality` before handoff.

SQLite files under `data/` are generated state. Delete and rebuild them with `python tools/llm_wiki.py rebuild` whenever needed.
