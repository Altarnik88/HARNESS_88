# Stack Options

These are selection profiles, not pre-scaffolded projects. No frontend app is bundled. Stack is selected through dialogue from the user's goals, site type, content model, backend/data needs, integrations, deployment expectations, and maintenance constraints.

Detailed machine-readable profile metadata lives in `agents/harness/stack-profiles.json`, including languages, frameworks, services, best-fit cases, pros, cons, selection questions, scaffold policy, and deployment options.

## Profiles

- `next-static`: Next.js App Router + TypeScript + Tailwind for landing pages, marketing sites, and frontend-first sites.
- `next-fullstack`: Next.js App Router + TypeScript + Tailwind, with backend and data decisions made later, for SaaS or app-like sites.
- `astro-content`: Astro for SEO/content-heavy sites, blogs, and documentation.
- `sveltekit`: SvelteKit for interactive applications.
- `custom`: A user-defined stack selected after clarification.

## Rules

- Do not scaffold every profile.
- Do not scaffold any stack until the user approves a profile or proposes a custom stack.
- Ask the user to choose between VPS/VDS vs hosting before publish planning.
- Explain pros and cons of VPS/VDS and managed hosting, then recommend a target from the user's budget, traffic, backend/runtime, operations, and maintenance answers.
- Use `custom` only after the user confirms the approach or answers enough questions for a clear recommendation.
