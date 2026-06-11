# START HERE

Use this file after a fresh clone of HARNESS_88. It is a practical first-chat script for turning the repository into a site project.

## First Chat

Open Codex or another coding-agent chat in the root of this repository and start with something like:

```text
Read START_HERE.md, AGENTS.md, PRODUCT.md, DESIGN.md, STACK.md, and agents/harness/stack-options.md.
Check readiness with python tools/llm_wiki.py task readiness --json.
The stack is not selected yet. Help me choose a stack/fullstack profile, then update PRODUCT.md, DESIGN.md, and STACK.md, create the first task, and begin the site through the autonomous harness.
```

If you already know the stack profile, say it directly:

```text
Select stack profile next-static for this site. Then update PRODUCT.md, DESIGN.md, and STACK.md, create the first task, and begin implementation through the harness.
```

If you are not sure, ask the agent to ask 3-5 short questions:

```text
I am not sure which stack/fullstack profile fits. Ask me 3-5 short questions about the site, recommend a profile, then update PRODUCT.md, DESIGN.md, and STACK.md before implementation starts.
```

## First-Run Checklist

1. Check the core harness:

   ```powershell
   python tools/llm_wiki.py task readiness --json
   python tools/llm_wiki.py stack status
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

   - `PRODUCT.md`: product goal, audience, scope, user jobs, acceptance criteria.
   - `DESIGN.md`: visual direction, UX constraints, accessibility, component rules.
   - `STACK.md`: selected stack/fullstack profile and any stack notes.

5. Create the first task:

   ```powershell
   python tools/llm_wiki.py task create --title "First Implementation Slice" --objective "Build the first approved site slice from PRODUCT.md, DESIGN.md, and STACK.md."
   ```

6. Start development from that task, keeping progress and checkpoint files updated.

## Important Rule

HARNESS_88 does not choose Next.js or fullstack by default. The `frontend/` directory is an optional bundled Next.js starter/template. Production implementation starts only after a stack profile is selected or the user explicitly confirms a custom approach.
