# Durable Task Queue

This directory starts empty except for `_template.md`.

Use one task file per atomic implementation, QA, docs, release, or knowledge-stewardship unit.

```powershell
python tools/llm_wiki.py task create --title "Write Product Brief" --objective "Capture approved product decisions."
python tools/llm_wiki.py task list
python tools/llm_wiki.py task next
python tools/llm_wiki.py task evidence --json
python tools/llm_wiki.py task validate --strict
```

Use `task evidence --json` for a read-only machine-checkable summary of task,
progress, and checkpoint evidence before updating audit, remediation, final
approval, or publish gates. It reports counts and paths only; it must not expose
raw evidence logs or secret values.
