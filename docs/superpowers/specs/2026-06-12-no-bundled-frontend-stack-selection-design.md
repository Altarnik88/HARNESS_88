# No Bundled Frontend Stack Selection Design

## Goal

HARNESS_88 must remain a stack-neutral core engine/template infrastructure. It should not ship a preselected frontend starter. Instead, it should guide the user through stack selection during the first project conversation, present suitable stack options with trade-offs, wait for explicit approval, and only then allow stack-specific scaffolding.

## Problem

The repository currently includes a root `frontend/` Next.js starter and generated starter templates also include a bundled frontend. This conflicts with the stack-neutral contract because it looks like Next.js has already been chosen. It also makes full-repo release security depend on an optional starter dependency tree that may be unrelated to the user's actual future site.

## Approved Direction

Remove the bundled frontend starter from the HARNESS_88 core and from generated site starters. Keep HARNESS_88 focused on intake, stack recommendation, approvals, task tracking, quality gates, and handoff.

The stack flow becomes:

1. Gather the user's site goals, audience, content model, interaction level, data/backend needs, commerce/payment needs, integrations, deployment expectations, team skills, and maintenance constraints.
2. Recommend several suitable stack options rather than assuming one.
3. For each option, explain the main language, framework, services, strengths, weaknesses, operational complexity, and best-fit use cases.
4. Ask whether publication should use VPS/VDS or managed hosting, explain the pros and cons of each, and recommend the better target from the user's budget, traffic, backend/runtime, operations, and maintenance answers.
5. Wait for the user to approve one option or propose a custom stack and deployment direction.
6. Record the approved stack selection in `STACK.md`.
7. Scaffold or implement stack-specific code only in a later approved task.

## User-Facing Behavior

When stack selection is needed, HARNESS_88 should present options such as:

- Astro + TypeScript + Tailwind + CMS for SEO/content-heavy sites.
- Next.js + TypeScript + Tailwind + backend services for app-like sites.
- SvelteKit + TypeScript for highly interactive applications.
- Laravel/Rails/Django-style backend-led stacks when admin/data workflows dominate.
- Custom stack when the user already has a preferred language, framework, service, or hosting constraint.

Each recommendation should include clear pros and cons for the language, framework, services, hosting, maintainability, performance, SEO, security, and team fit where relevant.

Deployment recommendations must compare:

- VPS/VDS: more control over runtime, logs, backups, reverse proxy, colocated services, and custom server setup; more responsibility for server administration, updates, monitoring, security, backups, and incidents.
- Managed hosting: faster setup, preview deploys, CDN/HTTPS, rollback, and lower maintenance; less low-level control, provider/runtime limits, possible vendor lock-in, and pricing constraints.

## Implementation Shape

- Remove root `frontend/` source, dependencies, generated build artifacts, and frontend-specific starter files from the repository.
- Remove bundled frontend files from `src/llm_wiki/templates/site_starter/`.
- Update documentation that currently describes `frontend/` as an optional bundled Next.js starter.
- Update stack profile metadata so profiles are recommendation/scaffolding targets, not references to an existing `frontend/` folder.
- Add stack/profile metadata and docs for VPS/VDS vs managed hosting recommendation prompts, pros, cons, and approval before publish planning.
- Update CLI quality/security/doctor behavior so missing `frontend/package.json` is normal for the core, not a problem.
- Update tests that currently require generated starters to contain `frontend/`.
- Preserve the existing gates that block serious site implementation until intake, references, product/design, stack selection, tasks, and approvals are recorded.

## Non-Goals

- Do not choose a stack in root `STACK.md`.
- Do not approve `PRODUCT.md`, `DESIGN.md`, `SITE_INTAKE.md`, `SITE_REFERENCES.md`, or `SITE_GATES.md`.
- Do not scaffold a replacement frontend.
- Do not install frontend dependencies.
- Do not change `raw/` or edit `data/wiki.sqlite` directly.
- Do not request or store secrets.

## Acceptance Criteria

- HARNESS_88 no longer contains a root bundled `frontend/` starter.
- Generated site starters no longer include a prebuilt frontend app.
- Stack documentation says stacks are selected through dialogue and explicit approval.
- `python tools/llm_wiki.py quality --skip-frontend` passes.
- `python tools/llm_wiki.py task validate --strict` passes.
- `python tools/llm_wiki.py task evidence --json` remains valid.
- Release documentation can honestly describe HARNESS_88 as stack-neutral core/template infrastructure, not a completed site and not a preselected Next.js starter.
