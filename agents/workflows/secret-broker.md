# Secret Broker Protocol

## Goal

Let users provide deployment, database, auth, payment, and service secrets without exposing secret values to agents, project files, wiki pages, task files, MCP arguments, screenshots, or chat history.

This document defines the contract for a future local secret broker program. It does not store secrets and does not implement a provider-specific integration by itself.

## Core Rule

Agents may request secret-backed actions, but they must not read, print, copy, persist, or infer secret values.

Allowed agent actions:

- Ask the user which provider or service is being configured.
- Ask the user to open or run the local broker program.
- Pass non-secret metadata to the broker, such as provider name, project URL, required variable names, and intended operation.
- Trigger an allowed broker operation after the user confirms it.
- Verify success through non-secret status output.

Forbidden agent actions:

- Ask the user to paste secret values into chat.
- Store secrets in `AGENTS.md`, `PRODUCT.md`, `DESIGN.md`, `STACK.md`, wiki pages, task files, `.env` files committed to git, MCP arguments, or Codex config.
- Print secret values to terminal output or logs.
- Take screenshots of screens that display secret values.
- Read secret stores directly unless a future task explicitly designs a safe read-redaction boundary.

## Broker Responsibilities

A safe broker program should:

- Run locally on the user's machine.
- Accept secret values through a human-controlled UI or prompt that agents cannot inspect.
- Store secrets only in an approved local secret store or target provider, never in project files.
- Expose only redacted status to agents, such as `configured`, `missing`, `failed`, or `requires-user-action`.
- Support dry-run/planning mode without secret entry.
- Require explicit user confirmation before writing provider settings, database records, auth config, payment config, or deployment secrets.
- Produce an audit-safe receipt that names actions and variable names without values.

## Required Workflow

1. Backend/Data or DevOps/Release identifies required secret names and provider actions.
2. Conductor records non-secret requirements in the task/checkpoint.
3. User opens the broker program and enters secret values locally.
4. Agent invokes only the approved broker command or action.
5. Broker performs the action and returns redacted status.
6. Agent records redacted verification evidence.

## Dry-Run Planning Command

Agents can create a redacted planning receipt without invoking a broker or writing any files:

```powershell
python tools/llm_wiki.py security secret-plan --provider supabase --vars SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY --operation "configure deployment env" --json
```

The command accepts only non-secret metadata:

- provider id;
- required variable names;
- operation description.

It must not accept secret values, `VAR=value` pairs, `.env` writes, secret-store reads, screenshots, or MCP secret arguments. The JSON receipt is evidence-safe and uses `status: dry-run` plus `secret_values_visible: false`.

## Example Non-Secret Record

```text
Provider: Supabase
Required variables: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
Operation: configure backend environment for selected deployment target
Status: configured
Secret values: not visible to agents
```

## Follow-Up Implementation Task

Implementing the actual broker program requires a separate approved task because provider choice, OS secret-store support, UI behavior, logging, redaction, and deployment target all affect the safety model.
