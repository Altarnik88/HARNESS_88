# START HERE

Use this file after a fresh clone of HARNESS_88. It is a practical first-chat script for turning the repository into a site project.

## First Chat

Open Codex or another coding-agent chat in the root of this repository and start with something like:

```text
Read START_HERE.md, AGENTS.md, PRODUCT.md, DESIGN.md, STACK.md, and agents/harness/stack-options.md.
Check readiness with python tools/llm_wiki.py task readiness --json.
The stack is not selected yet. Help me choose a stack/fullstack profile, then update PRODUCT.md, DESIGN.md, and STACK.md, create the first task, and begin the site through the autonomous harness.
```

If you are not sure, ask the agent to ask 3-5 short questions and recommend a profile.

## First-Run Checklist

```powershell
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor
```

After selecting a profile, update `PRODUCT.md`, `DESIGN.md`, and `STACK.md`, create the first task, and begin development from that task.
