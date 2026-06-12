# No Bundled Frontend Stack Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the prebuilt Next.js `frontend/` starter and make stack selection a dialog-driven recommendation flow with explicit user approval before scaffolding.

**Architecture:** HARNESS_88 remains a Python CLI and Markdown-template core. Stack profiles become recommendation/scaffolding metadata, generated projects contain no frontend app, and quality/security tooling treats missing `frontend/package.json` as normal core state.

**Tech Stack:** Python 3.11+, `unittest`, Markdown project contracts, JSON stack metadata, local `tools/llm_wiki.py` CLI.

---

## File Structure

- Delete: `frontend/`
- Delete: `src/llm_wiki/templates/site_starter/frontend/`
- Delete: `tests/test_frontend_build_config.py`
- Modify: `src/llm_wiki/site_generator.py`
- Modify: `src/llm_wiki/stack.py`
- Modify: `src/llm_wiki/cli.py`
- Modify: `agents/harness/stack-profiles.json`
- Modify: `agents/harness/stack-options.md`
- Modify: root docs and matching generated-starter templates that mention a bundled frontend: `README.md`, `AGENTS.md`, `AGENT_SITE_TOOLING.md`, `START_HERE.md`, `DESIGN.md`, `llms.txt`, `agents/conductor.md`, `agents/harness/README.md`, `agents/harness/deploy-handoff-template.md`, and matching files under `src/llm_wiki/templates/site_starter/`
- Modify tests: `tests/test_site_generator.py`, `tests/test_stack_neutral.py`, `tests/test_stack_cli.py`, `tests/test_security.py`, `tests/test_quality.py` only where expectations need the no-bundled-frontend contract.
- Update release evidence after verification: `RELEASE_NOTES.md`, `agents/tasks/2026-06-12-github-core-engine-release.md`, matching progress/checkpoint files, `wiki/review.md`, and `wiki/log.md`.

## Task 1: Create Concrete Harness Task Bundle

**Files:**
- Create: `agents/tasks/2026-06-12-no-bundled-frontend-stack-selection.md`
- Create: `agents/tasks/progress/2026-06-12-no-bundled-frontend-stack-selection.md`
- Create: `agents/tasks/checkpoints/2026-06-12-no-bundled-frontend-stack-selection.md`

- [ ] **Step 1: Create the task bundle**

Run:

```powershell
python tools/llm_wiki.py task create --title "No Bundled Frontend Stack Selection" --objective "Remove bundled frontend starters and make stack selection dialog-driven before stack-specific scaffolding." --owner "Conductor" --status "planned" --owned frontend/ src/llm_wiki/templates/site_starter/frontend/ src/llm_wiki/site_generator.py src/llm_wiki/stack.py src/llm_wiki/cli.py agents/harness/stack-profiles.json agents/harness/stack-options.md README.md AGENTS.md AGENT_SITE_TOOLING.md START_HERE.md DESIGN.md llms.txt agents/conductor.md agents/harness/README.md agents/harness/deploy-handoff-template.md src/llm_wiki/templates/site_starter/ tests/test_site_generator.py tests/test_stack_neutral.py tests/test_stack_cli.py tests/test_frontend_build_config.py RELEASE_NOTES.md wiki/review.md wiki/log.md --do-not-edit raw/ data/wiki.sqlite PRODUCT.md SITE_INTAKE.md SITE_REFERENCES.md SITE_GATES.md STACK.md --verification "python tools/llm_wiki.py quality --skip-frontend" --created 2026-06-12
```

Expected: exits 0 and reports created task/progress/checkpoint paths.

- [ ] **Step 2: Confirm the task graph still validates**

Run:

```powershell
python tools/llm_wiki.py task validate --strict
```

Expected: exits 0 with `No task validation issues found.`

- [ ] **Step 3: Commit the task bundle**

Run:

```powershell
git add agents/tasks/2026-06-12-no-bundled-frontend-stack-selection.md agents/tasks/progress/2026-06-12-no-bundled-frontend-stack-selection.md agents/tasks/checkpoints/2026-06-12-no-bundled-frontend-stack-selection.md
git commit -m "Track no bundled frontend stack selection task"
```

Expected: commit succeeds and contains only the new task bundle.

## Task 2: Write RED Tests For No Bundled Frontend

**Files:**
- Modify: `tests/test_site_generator.py`
- Modify: `tests/test_stack_neutral.py`
- Delete: `tests/test_frontend_build_config.py`

- [ ] **Step 1: Update generated project expectations**

In `tests/test_site_generator.py`, change `test_create_site_project_omits_local_only_state` so it asserts the generated project does not contain `frontend/`:

```python
self.assertFalse((target / "frontend").exists())
```

Remove the current assertion:

```python
self.assertTrue((target / "frontend" / "src" / "app" / "page.tsx").exists())
```

- [ ] **Step 2: Update generated copy assertions**

In `test_create_site_project_removes_absolute_local_paths_and_demo_copy`, replace the old bundled frontend assertions with:

```python
self.assertNotIn("optional bundled Next.js starter", (target / "README.md").read_text(encoding="utf-8"))
self.assertIn("No frontend app is bundled", (target / "README.md").read_text(encoding="utf-8"))
self.assertIn("status: unselected", (target / "STACK.md").read_text(encoding="utf-8"))
self.assertFalse((target / "frontend").exists())
```

- [ ] **Step 3: Update root stack-neutral docs test**

In `tests/test_stack_neutral.py`, change `test_root_docs_are_stack_neutral` so the combined docs assert:

```python
self.assertIn("no frontend app is bundled", combined)
self.assertIn("stack is selected through dialogue", combined)
self.assertNotIn("optional bundled next.js starter", combined)
self.assertNotIn("frontend/`: optional bundled", combined)
self.assertNotIn("a next.js frontend in `frontend/`", combined)
```

- [ ] **Step 4: Delete obsolete frontend starter tests**

Delete `tests/test_frontend_build_config.py`. These tests checked root `frontend/src/app/layout.tsx` and `frontend/src/app/page.tsx`; those files must no longer exist.

- [ ] **Step 5: Run the focused tests and confirm RED**

Run:

```powershell
python -m unittest tests.test_site_generator tests.test_stack_neutral
```

Expected: fails because `frontend/` still exists in generated projects and docs still mention the optional bundled starter.

## Task 3: Remove Bundled Frontend From Source And Generator

**Files:**
- Delete: `frontend/`
- Delete: `src/llm_wiki/templates/site_starter/frontend/`
- Modify: `src/llm_wiki/site_generator.py`

- [ ] **Step 1: Remove frontend from generator copy paths**

In `src/llm_wiki/site_generator.py`, remove `"frontend",` from `COPY_PATHS`.

The list should still include:

```python
COPY_PATHS = [
    ".github/workflows/quality.yml",
    "agents/TEAM.md",
    "agents/conductor.md",
    "agents/harness",
    "agents/protocols",
    "agents/resources",
    "agents/roles",
    "agents/templates",
    "agents/tooling-matrix.md",
    "agents/workflows",
    "src/llm_wiki",
    "tests",
    "tools/llm_wiki.py",
]
```

- [ ] **Step 2: Delete root frontend starter**

Remove the root `frontend/` directory and all tracked files below it.

Run:

```powershell
git rm -r frontend
```

Expected: removes tracked frontend files. If generated untracked directories such as `frontend/node_modules` or `frontend/.next` remain, remove them from the working tree after confirming they are inside `C:\Users\Io\Documents\Codex\HARNESS_88\frontend`.

- [ ] **Step 3: Delete generated-starter frontend template**

Run:

```powershell
git rm -r src/llm_wiki/templates/site_starter/frontend
```

Expected: removes generated starter frontend template files.

- [ ] **Step 4: Run focused generator tests**

Run:

```powershell
python -m unittest tests.test_site_generator
```

Expected: still fails only on docs/text expectations until docs are updated in the next task.

## Task 4: Make Stack Profiles Recommendation Metadata

**Files:**
- Modify: `agents/harness/stack-profiles.json`
- Modify: `src/llm_wiki/stack.py`
- Modify: `src/llm_wiki/cli.py`
- Modify: `tests/test_stack_cli.py`

- [ ] **Step 1: Write RED tests for profile trade-off metadata**

In `tests/test_stack_cli.py`, update `test_stack_list_json_includes_profile_metadata` to require these keys:

```python
for key in [
    "commands",
    "required_tools",
    "ci_policy",
    "frontend",
    "backend",
    "deploy_notes",
    "languages",
    "frameworks",
    "services",
    "best_for",
    "pros",
    "cons",
    "scaffold_policy",
    "selection_questions",
]:
    self.assertIn(key, next_static)
self.assertIn("TypeScript", next_static["languages"])
self.assertTrue(next_static["pros"])
self.assertTrue(next_static["cons"])
self.assertIn("approved scaffold task", next_static["scaffold_policy"].casefold())
```

Add one assertion to `test_stack_list_outputs_available_profiles`:

```python
self.assertIn("Pros:", output)
self.assertIn("Cons:", output)
```

Update `test_stack_select_updates_stack_md_only` expected output message to:

```python
self.assertIn("No dependencies were installed and no frontend was scaffolded", output)
```

- [ ] **Step 2: Run stack tests and confirm RED**

Run:

```powershell
python -m unittest tests.test_stack_cli
```

Expected: fails because profile metadata and CLI output do not yet include the new recommendation fields.

- [ ] **Step 3: Extend `StackProfile`**

In `src/llm_wiki/stack.py`, add fields to the dataclass:

```python
languages: list[str]
frameworks: list[str]
services: list[str]
best_for: list[str]
pros: list[str]
cons: list[str]
scaffold_policy: str
selection_questions: list[str]
```

Update `to_json()` to include these fields.

Update `stack_profile_from_json()` with a local helper:

```python
def string_list(row: dict[str, Any], key: str) -> list[str]:
    return [str(value) for value in row.get(key, [])]
```

Use that helper for `languages`, `frameworks`, `services`, `best_for`, `pros`, `cons`, and `selection_questions`, and use `scaffold_policy=str(row.get("scaffold_policy", ""))`.

- [ ] **Step 4: Update `render_selected_stack`**

In `src/llm_wiki/stack.py`, render the selected stack as a recorded choice, not a prebuilt project. Add this helper near `render_selected_stack`:

```python
def render_markdown_list(values: list[str]) -> str:
    if not values:
        return "- None recorded."
    return "\n".join(f"- {value}" for value in values)
```

Use it in `render_selected_stack` to add `## Fit`, `## Pros`, and `## Cons` sections from `profile.best_for`, `profile.pros`, and `profile.cons`. Add a `## Scaffold Policy` section containing `profile.scaffold_policy`.

Keep the existing line:

```markdown
- No dependencies were installed.
```

Replace:

```markdown
- No frontend files were changed automatically.
```

with:

```markdown
- No frontend, backend, or service files were scaffolded automatically.
```

- [ ] **Step 5: Update CLI human output**

In `src/llm_wiki/cli.py`, update `cmd_stack` list output so each profile prints:

```python
print(f"- {profile.name}: {profile.description}")
print(f"  Best for: {', '.join(profile.best_for)}")
print(f"  Pros: {'; '.join(profile.pros[:2])}")
print(f"  Cons: {'; '.join(profile.cons[:2])}")
```

Update the stack select message to:

```python
print("STACK.md updated. No dependencies were installed and no frontend was scaffolded.")
```

- [ ] **Step 6: Update profile JSON**

In `agents/harness/stack-profiles.json`, add the new fields to every profile. Use these exact policies:

- `next-static` scaffold policy: `No Next.js app is bundled. Scaffold Next.js only after the user approves this profile and an approved scaffold task records the target directory and commands.`
- `next-fullstack` scaffold policy: `No fullstack app is bundled. Scaffold Next.js and backend/service wiring only after product, design, data, auth, and deployment decisions are approved in tracked tasks.`
- `astro-content` scaffold policy: `No Astro app is bundled. Scaffold Astro only after the user approves this profile and content/source decisions are recorded.`
- `sveltekit` scaffold policy: `No SvelteKit app is bundled. Scaffold SvelteKit only after the user approves this profile and adapter/runtime decisions are recorded.`
- `custom` scaffold policy: `No custom stack is bundled. Record the user's approved language, framework, services, commands, and hosting target before scaffolding.`

Set `commands` for each non-custom profile to non-executing guidance strings:

```json
"commands": {
  "install": "Defined by the approved scaffold task.",
  "dev": "Defined by the approved scaffold task.",
  "lint": "Defined by the approved scaffold task.",
  "build": "Defined by the approved scaffold task."
}
```

For `custom`, keep the existing record-in-STACK guidance.

- [ ] **Step 7: Run stack tests and confirm GREEN**

Run:

```powershell
python -m unittest tests.test_stack_cli
```

Expected: exits 0.

## Task 5: Update Root And Generated Documentation

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `AGENT_SITE_TOOLING.md`
- Modify: `START_HERE.md`
- Modify: `DESIGN.md`
- Modify: `llms.txt`
- Modify: `agents/conductor.md`
- Modify: `agents/harness/README.md`
- Modify: `agents/harness/stack-options.md`
- Modify: `agents/harness/deploy-handoff-template.md`
- Modify matching files under `src/llm_wiki/templates/site_starter/`
- Modify: `tests/test_stack_neutral.py`
- Modify: `tests/test_site_generator.py`

- [ ] **Step 1: Replace bundled frontend language**

Across root docs and generated-starter templates, replace claims that `frontend/` is an optional bundled Next.js starter with this contract:

```markdown
No frontend app is bundled. Stack is selected through dialogue from the user's goals, site type, content model, backend/data needs, integrations, deployment expectations, and maintenance constraints.
```

- [ ] **Step 2: Update first-run stack guidance**

In `START_HERE.md` and `src/llm_wiki/templates/site_starter/START_HERE.md`, make the stack recommendation instruction explicit:

```markdown
Recommend 2-4 stack options with languages, frameworks, services, pros, cons, operational complexity, and best-fit use cases. Wait for the user to approve one option or propose a custom stack before running `python tools/llm_wiki.py stack select next-static` or the approved profile name.
```

- [ ] **Step 3: Update tooling docs**

In `AGENT_SITE_TOOLING.md` and the generated template, remove the `Optional Frontend Template` section. Add:

```markdown
## Stack Scaffolding

HARNESS_88 does not include a prebuilt frontend. After intake and stack recommendation, scaffold stack-specific files only in an approved task for the selected profile or custom stack.
```

- [ ] **Step 4: Update deploy handoff commands**

In `agents/harness/deploy-handoff-template.md`, replace `cd frontend && npm run build` guidance for Next profiles with:

```markdown
Build command guidance: use the build command produced by the approved Next.js scaffold task.
```

Keep Astro/SvelteKit/custom build guidance inactive until stack approval.

- [ ] **Step 5: Update generated-starter drift expectations**

Ensure the same docs changed in root are mirrored under `src/llm_wiki/templates/site_starter/` where generated projects use template overlays.

- [ ] **Step 6: Run docs/generator tests**

Run:

```powershell
python -m unittest tests.test_stack_neutral tests.test_site_generator
```

Expected: exits 0.

## Task 6: Confirm Quality And Security Behavior Without Frontend

**Files:**
- Modify: `tests/test_quality.py`
- Modify: `tests/test_security.py`
- Modify only if needed: `src/llm_wiki/quality.py`, `src/llm_wiki/security.py`, `src/llm_wiki/doctor.py`

- [ ] **Step 1: Add explicit no-frontend quality test**

In `tests/test_quality.py`, add:

```python
def test_no_frontend_manifest_runs_core_steps_only_by_default(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        steps = build_quality_steps(root, full=True)

        self.assertEqual(
            [step.name for step in steps],
            ["python-tests", "wiki-rebuild", "wiki-lint-strict"],
        )
```

- [ ] **Step 2: Keep existing optional frontend tests**

Do not remove tests that create a temporary `frontend/package.json`. They prove optional stack-specific projects still get frontend lint/build checks after scaffolding.

- [ ] **Step 3: Add explicit no-frontend security message test**

In `tests/test_security.py`, extend `test_security_audit_skips_when_frontend_manifest_is_missing`:

```python
self.assertIn("No frontend/package.json found", payload["message"])
```

- [ ] **Step 4: Run quality/security tests**

Run:

```powershell
python -m unittest tests.test_quality tests.test_security
```

Expected: exits 0 without changing production code unless the tests reveal a mismatch.

- [ ] **Step 5: Run no-record security audit locally**

Run:

```powershell
python tools/llm_wiki.py security audit --json --no-record --blocking
```

Expected: exits 0 and reports `status: "skipped"` with `unresolved_count: 0` because no frontend manifest exists.

## Task 7: Update Release Evidence And Wiki State

**Files:**
- Modify: `RELEASE_NOTES.md`
- Modify: `agents/tasks/2026-06-12-github-core-engine-release.md`
- Modify: `agents/tasks/progress/2026-06-12-github-core-engine-release.md`
- Modify: `agents/tasks/checkpoints/2026-06-12-github-core-engine-release.md`
- Modify: `agents/tasks/2026-06-12-no-bundled-frontend-stack-selection.md`
- Modify: `agents/tasks/progress/2026-06-12-no-bundled-frontend-stack-selection.md`
- Modify: `agents/tasks/checkpoints/2026-06-12-no-bundled-frontend-stack-selection.md`
- Modify: `wiki/review.md`
- Modify: `wiki/log.md`

- [ ] **Step 1: Update release notes**

Change `RELEASE_NOTES.md` so `v0.1.0` says HARNESS_88 is release-ready as a stack-neutral core engine/template infrastructure after bundled frontend removal. Include:

```markdown
- HARNESS_88 is not a completed site.
- No frontend app is bundled or preselected.
- New projects start with intake, stack recommendation, explicit stack approval, references, product/design approvals, and tracked tasks.
- No secrets are included or requested.
```

- [ ] **Step 2: Close the old frontend audit blocker in review notes**

In `wiki/review.md`, keep historical context but mark the Next/PostCSS item as closed by removing the bundled frontend from HARNESS_88 core. Use wording:

```markdown
Resolution: closed for v0.1.0 by removing the bundled `frontend/` starter. No npm audit target remains in the core repository; future scaffolded frontends must run their own audit after stack approval.
```

- [ ] **Step 3: Update release task status**

In `agents/tasks/2026-06-12-github-core-engine-release.md`, set:

```markdown
Status: verified
```

Only do this after Task 8 verification passes.

- [ ] **Step 4: Update task progress/checkpoint evidence**

Add verification evidence to both the release task and no-bundled-frontend task progress/checkpoint files for:

```powershell
python tools/llm_wiki.py security audit --json --no-record --blocking
python tools/llm_wiki.py quality --skip-frontend
python tools/llm_wiki.py task validate --strict
python tools/llm_wiki.py task evidence --json
```

State that `frontend/` was intentionally removed and no stack/site approval files were changed.

- [ ] **Step 5: Append wiki log entry**

Append one dated entry to `wiki/log.md` recording:

```markdown
- 2026-06-12 [decision] Removed bundled frontend starter from release scope; stack-specific frontend scaffolding now waits for user-approved stack selection.
```

## Task 8: Full Verification

**Files:**
- No new files unless verification reveals a defect.

- [ ] **Step 1: Run focused tests**

Run:

```powershell
python -m unittest tests.test_site_generator tests.test_stack_neutral tests.test_stack_cli tests.test_quality tests.test_security
```

Expected: exits 0.

- [ ] **Step 2: Run full Python test suite**

Run:

```powershell
python -m unittest discover -s tests
```

Expected: exits 0.

- [ ] **Step 3: Run core quality gate**

Run:

```powershell
python tools/llm_wiki.py quality --skip-frontend
```

Expected: exits 0; Python tests, wiki rebuild, and strict lint pass.

- [ ] **Step 4: Run security audit skip gate**

Run:

```powershell
python tools/llm_wiki.py security audit --json --no-record --blocking
```

Expected: exits 0 with `status` equal to `skipped` and `unresolved_count` equal to `0`.

- [ ] **Step 5: Run task validation and evidence**

Run:

```powershell
python tools/llm_wiki.py task validate --strict
python tools/llm_wiki.py task evidence --json
```

Expected: validation exits 0 and evidence JSON has no missing support files or verified task without verification evidence.

- [ ] **Step 6: Confirm protected files stayed untouched**

Run:

```powershell
git diff -- PRODUCT.md DESIGN.md SITE_INTAKE.md SITE_REFERENCES.md SITE_GATES.md STACK.md raw data/wiki.sqlite
```

Expected: no diff output.

- [ ] **Step 7: Confirm no frontend remains**

Run:

```powershell
git status --short
Test-Path frontend
Test-Path src/llm_wiki/templates/site_starter/frontend
```

Expected: `git status --short` shows only intentional changes, and both `Test-Path` commands print `False`.

## Task 9: Commit And Push Implementation

**Files:**
- Stage only intentional files from this plan.

- [ ] **Step 1: Review changes**

Run:

```powershell
git status --short
git diff --stat
```

Expected: only bundled frontend removal, stack-selection code/docs/templates/tests, task/wiki/release evidence, and no protected approval/raw/data changes.

- [ ] **Step 2: Stage intentional changes**

Run:

```powershell
git add -A frontend src/llm_wiki/templates/site_starter/frontend src/llm_wiki/site_generator.py src/llm_wiki/stack.py src/llm_wiki/cli.py agents/harness/stack-profiles.json agents/harness/stack-options.md README.md AGENTS.md AGENT_SITE_TOOLING.md START_HERE.md DESIGN.md llms.txt agents/conductor.md agents/harness/README.md agents/harness/deploy-handoff-template.md src/llm_wiki/templates/site_starter tests RELEASE_NOTES.md agents/tasks wiki/review.md wiki/log.md
```

Expected: stages only intended changes. If unrelated user changes appear, unstage them before committing.

- [ ] **Step 3: Commit**

Run:

```powershell
git commit -m "Remove bundled frontend stack starter"
```

Expected: commit succeeds.

- [ ] **Step 4: Push current branch**

Run:

```powershell
git push origin task-evidence-summaries
```

Expected: push succeeds.

## Task 10: Release Execution Guardrail

**Files:**
- No files unless the user explicitly resumes release publication.

- [ ] **Step 1: Do not create release artifacts in this implementation batch**

Do not merge to `main`, create tag `v0.1.0`, push a tag, or publish the GitHub release as part of this implementation plan unless the user explicitly asks for the release publication step after reviewing the verified implementation commit.

- [ ] **Step 2: If release publication is requested later**

Re-run:

```powershell
git status --short
python tools/llm_wiki.py quality --skip-frontend
python tools/llm_wiki.py security audit --json --no-record --blocking
python tools/llm_wiki.py task validate --strict
python tools/llm_wiki.py task evidence --json
```

Expected: all gates pass before merge/tag/GitHub release.

## Self-Review Notes

- Spec coverage: removes root and generated `frontend/`, updates stack recommendation metadata, preserves approval gates, updates release evidence, and verifies no protected site approval files changed.
- Incomplete-instruction scan: no incomplete fields are left for implementers; each variable command is either a literal command or an inactive guidance string intentionally recorded in stack metadata.
- Type consistency: new `StackProfile` fields are named consistently across JSON, dataclass parsing, CLI output, and JSON output.
