# Conductor Runtime Protocol

This protocol makes HARNESS_88 agent-first behavior executable instead of advisory.

## Main Chat Bootstrap

The first site-delivery response in the main chat must start from the Conductor role. Run:

```powershell
python tools/llm_wiki.py conductor start
```

The visible response must include `Conductor online` before intake, reference, design, implementation, QA, release, or wiki closeout work begins.

## Runtime Rule

Conductor cannot self-assign worker phases. Conductor may read state, create tasks, create delegation packets, run checks, review outputs, and summarize decisions. Worker phases require a role owner other than Conductor and a delegation packet under `agents/delegations/`.

Worker phases include:

- first-run-intake
- brief-contracts
- reference-analysis
- sitemap-content
- frontend-architecture
- frontend-build
- backend-data
- catalog-ingest
- total-audit
- remediation
- final-approval
- publish-operate
- knowledge-closeout

## Delegation Packet Gate

Before any worker phase starts, Conductor creates a task bundle and delegation packet:

```powershell
python tools/llm_wiki.py conductor delegate --phase reference-analysis --title "Reference Analysis" --objective "Complete bounded reference analysis." --owner "Reference Research" --user-language "Russian" --owned SITE_REFERENCES.md raw/assets/references/ --do-not-edit frontend/ PRODUCT.md --verification "python tools/llm_wiki.py site references --json"
```

The task must include:

- `Phase: <phase>`
- `Delegation packet: agents/delegations/<task>.md`
- `Role owner: <non-Conductor role>`

The packet must include role, task file, progress file, checkpoint file, user language, ownership/scope, allowed tooling, code permission, expected output, verification, and clean-context resume instructions.

## Reference Analysis Route

For `reference-analysis`, route work through:

- Reference Research
- UX/Product Design
- Visual Design
- Design Artifact
- QA & Accessibility

Use:

```powershell
python tools/llm_wiki.py conductor route --phase reference-analysis
```

Denied by default: checkout/cart flows, private/login/account/admin pages, form submissions, destructive flows, credential collection, and production frontend implementation.

## One-Agent Fallback

If sub-agent tooling is unavailable, fallback is allowed only after the main chat states the worker role being assumed and the task, progress, checkpoint, and delegation packet exist. The fallback worker still obeys role ownership, denied scope, tooling matrix grants, and verification.

## Validation

Run before claiming readiness or completion:

```powershell
python tools/llm_wiki.py task validate --strict
```

The validator rejects open worker-phase tasks owned by Conductor, missing delegation packets, and incomplete packet fields.
