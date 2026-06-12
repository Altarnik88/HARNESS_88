from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cli_security import cmd_security
from .cli_site import cmd_site
from .cli_tasks import cmd_task
from .cli_tools import cmd_tools
from .conductor_runtime import cmd_conductor
from .quality import quality_exit_code, run_quality
from .stack import (
    allowed_profile_text,
    deploy_template_payload,
    load_stack_profiles,
    read_stack_status,
    select_stack_profile,
)
from .db import (
    add_source,
    append_log,
    collect_lint_issues,
    complete_ingest_job,
    create_page,
    enqueue_ingest_jobs,
    ensure_project,
    fail_ingest_job,
    list_events,
    next_ingest_job,
    rebuild_index,
    search,
)
from .paths import DB_PATH, resolve_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-wiki", description="Maintain a local LLM Wiki index.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create directories and initialize the SQLite database.")

    subparsers.add_parser("rebuild", help="Rebuild SQLite source/page/search/link indexes from files.")

    search_parser = subparsers.add_parser("search", help="Search wiki pages and raw sources.")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--json", action="store_true", help="Emit JSON results.")

    lint_parser = subparsers.add_parser("lint", help="Check wiki health.")
    lint_parser.add_argument("--json", action="store_true", help="Emit JSON issues.")
    lint_parser.add_argument("--strict", action="store_true", help="Exit 1 when issues are found.")

    add_parser = subparsers.add_parser("add-source", help="Copy a source file into raw/sources and rebuild.")
    add_parser.add_argument("path")

    page_parser = subparsers.add_parser("new-page", help="Create a draft wiki page and rebuild.")
    page_parser.add_argument("--type", required=True, choices=[
        "entity",
        "concept",
        "source",
        "query",
        "synthesis",
        "comparison",
        "overview",
    ])
    page_parser.add_argument("--title", required=True)
    page_parser.add_argument("--summary", default="")

    log_parser = subparsers.add_parser("log", help="Append a parseable wiki log entry.")
    log_parser.add_argument("kind")
    log_parser.add_argument("summary")
    log_parser.add_argument("--path", default="")

    events_parser = subparsers.add_parser("events", help="List events synced from wiki/log.md.")
    events_parser.add_argument("--limit", type=int, default=20)
    events_parser.add_argument("--json", action="store_true", help="Emit JSON events.")

    quality_parser = subparsers.add_parser("quality", help="Run the project quality gate.")
    quality_parser.add_argument("--full", action="store_true", help="Also run slower full checks such as frontend build.")
    quality_parser.add_argument("--skip-frontend", action="store_true", help="Run core checks without optional frontend checks.")
    quality_parser.add_argument("--json", action="store_true", help="Emit JSON quality results.")

    conductor_parser = subparsers.add_parser("conductor", help="Bootstrap and route HARNESS_88 Conductor work.")
    conductor_subparsers = conductor_parser.add_subparsers(dest="conductor_command", required=True)
    conductor_start_parser = conductor_subparsers.add_parser("start", help="Print the main-chat Conductor bootstrap packet.")
    conductor_start_parser.add_argument("--json", action="store_true", help="Emit JSON Conductor packet.")
    conductor_route_parser = conductor_subparsers.add_parser("route", help="Show required roles and gates for a site-delivery phase.")
    conductor_route_parser.add_argument("--phase", required=True, help="Site-delivery phase such as reference-analysis.")
    conductor_route_parser.add_argument("--json", action="store_true", help="Emit JSON route packet.")
    conductor_delegate_parser = conductor_subparsers.add_parser("delegate", help="Create a delegated task bundle and packet.")
    conductor_delegate_parser.add_argument("--phase", required=True, help="Site-delivery phase such as reference-analysis.")
    conductor_delegate_parser.add_argument("--title", required=True, help="Task title.")
    conductor_delegate_parser.add_argument("--objective", required=True, help="Delegated objective.")
    conductor_delegate_parser.add_argument("--owner", required=True, help="Non-Conductor role owner.")
    conductor_delegate_parser.add_argument("--user-language", required=True, help="Language for user-facing questions and approvals.")
    conductor_delegate_parser.add_argument("--owned", nargs="*", default=[], help="Owned files or directories.")
    conductor_delegate_parser.add_argument("--do-not-edit", nargs="*", default=[], help="Denied files or directories.")
    conductor_delegate_parser.add_argument("--verification", default="python tools/llm_wiki.py task validate --strict", help="Verification command.")
    conductor_delegate_parser.add_argument("--created", default="", help="Creation date in YYYY-MM-DD format. Defaults to today.")
    conductor_delegate_parser.add_argument("--json", action="store_true", help="Emit JSON created delegation bundle.")

    tools_parser = subparsers.add_parser("tools", help="Audit local tools, Codex skills, plugins, and MCP setup.")
    tools_subparsers = tools_parser.add_subparsers(dest="tools_command", required=True)
    tools_audit_parser = tools_subparsers.add_parser("audit", help="Report available and missing tools/skills/plugins.")
    tools_audit_parser.add_argument("--json", action="store_true", help="Emit JSON tooling audit.")
    tools_audit_parser.add_argument("--codex-home", default="", help="Override Codex home directory for skill/plugin detection.")

    stack_parser = subparsers.add_parser("stack", help="Inspect and select the project stack profile.")
    stack_subparsers = stack_parser.add_subparsers(dest="stack_command", required=True)
    stack_list_parser = stack_subparsers.add_parser("list", help="List available stack profiles.")
    stack_list_parser.add_argument("--json", action="store_true", help="Emit JSON stack profiles.")
    stack_status_parser = stack_subparsers.add_parser("status", help="Show current stack status from STACK.md.")
    stack_status_parser.add_argument("--json", action="store_true", help="Emit JSON stack status.")
    stack_select_parser = stack_subparsers.add_parser("select", help="Record the selected stack profile in STACK.md.")
    stack_select_parser.add_argument("profile", help="Stack profile name.")
    stack_select_parser.add_argument("--json", action="store_true", help="Emit JSON stack status.")
    stack_deploy_parser = stack_subparsers.add_parser("deploy-template", help="Show inactive stack-neutral publish handoff guidance for a profile.")
    stack_deploy_parser.add_argument("profile", help="Stack profile name.")
    stack_deploy_parser.add_argument("--json", action="store_true", help="Emit JSON deploy handoff template payload.")

    site_parser = subparsers.add_parser("site", help="Create clean site-development projects.")
    site_subparsers = site_parser.add_subparsers(dest="site_command", required=True)
    site_init_parser = site_subparsers.add_parser("init", help="Create a clean generated site project.")
    site_init_parser.add_argument("target", help="Target directory for the new site project.")
    site_init_parser.add_argument("--self-test", action="store_true", help="Run generated project core self-test after creation.")
    site_init_parser.add_argument("--json", action="store_true", help="Emit JSON init result.")
    site_self_test_parser = site_subparsers.add_parser("self-test", help="Create a temporary starter and run core self-test.")
    site_self_test_parser.add_argument("--json", action="store_true", help="Emit JSON self-test results.")
    site_intake_parser = site_subparsers.add_parser("intake", help="Report first-run site intake and reference gates.")
    site_intake_parser.add_argument("--json", action="store_true", help="Emit JSON site intake status.")
    site_references_parser = site_subparsers.add_parser("references", help="Report strict pre-frontend reference analysis gate status.")
    site_references_parser.add_argument("--json", action="store_true", help="Emit JSON site reference analysis status.")
    site_gates_parser = site_subparsers.add_parser("gates", help="Report delivery approval and publish gates.")
    site_gates_parser.add_argument("--json", action="store_true", help="Emit JSON site delivery gate status.")
    site_doctor_parser = site_subparsers.add_parser("doctor", help="Report unified project health and next actions.")
    site_doctor_parser.add_argument("--json", action="store_true", help="Emit JSON doctor report.")
    site_doctor_parser.add_argument("--skip-self-test", action="store_true", help="Skip generated-project self-test.")
    site_doctor_parser.add_argument("--run-security", action="store_true", help="Run non-recording frontend npm audit when available.")

    security_parser = subparsers.add_parser("security", help="Run non-blocking security review helpers.")
    security_subparsers = security_parser.add_subparsers(dest="security_command", required=True)
    security_audit_parser = security_subparsers.add_parser("audit", help="Run optional frontend npm audit.")
    security_audit_parser.add_argument("--json", action="store_true", help="Emit JSON audit results.")
    security_audit_parser.add_argument("--blocking", action="store_true", help="Exit 1 when unresolved security items are found.")
    security_audit_parser.add_argument("--no-record", action="store_true", help="Do not record unresolved items in wiki/review.md.")
    security_audit_parser.add_argument("--allowlist", default="", help="JSON allowlist path for accepted audit items.")
    security_secret_parser = security_subparsers.add_parser("secret-plan", help="Create a redacted dry-run secret broker plan.")
    security_secret_parser.add_argument("--provider", required=True, help="Non-secret provider id such as supabase or custom.")
    security_secret_parser.add_argument("--vars", nargs="+", required=True, help="Required environment variable names only; values are rejected.")
    security_secret_parser.add_argument("--operation", required=True, help="Non-secret operation description.")
    security_secret_parser.add_argument("--json", action="store_true", help="Emit JSON dry-run receipt.")

    task_parser = subparsers.add_parser("task", help="Inspect and update Harness Engineering task files.")
    task_subparsers = task_parser.add_subparsers(dest="task_command", required=True)

    task_list_parser = task_subparsers.add_parser("list", help="List concrete task files.")
    task_list_parser.add_argument("--status", default="", help="Filter by task status.")
    task_list_parser.add_argument("--json", action="store_true", help="Emit JSON task records.")

    task_next_parser = task_subparsers.add_parser("next", help="Show the next ready or planned task.")
    task_next_parser.add_argument("--json", action="store_true", help="Emit JSON task record.")

    task_validate_parser = task_subparsers.add_parser("validate", help="Validate harness task files.")
    task_validate_parser.add_argument("--json", action="store_true", help="Emit JSON validation issues.")
    task_validate_parser.add_argument("--strict", action="store_true", help="Exit 1 when validation issues are found.")

    task_status_parser = task_subparsers.add_parser("set-status", help="Update the Status line for one task file.")
    task_status_parser.add_argument("path", help="Concrete task file path.")
    task_status_parser.add_argument("status", help="New task status.")
    task_status_parser.add_argument("--force", action="store_true", help="Bypass transition rules for queue repair.")
    task_status_parser.add_argument("--json", action="store_true", help="Emit JSON updated task record.")

    task_create_parser = task_subparsers.add_parser("create", help="Create a task with progress and checkpoint files.")
    task_create_parser.add_argument("--title", required=True, help="Task title.")
    task_create_parser.add_argument("--objective", required=True, help="Atomic task objective.")
    task_create_parser.add_argument("--owner", default="Conductor", help="Role owner.")
    task_create_parser.add_argument("--status", default="planned", help="Initial task status.")
    task_create_parser.add_argument("--owned", nargs="*", default=[], help="Owned files or directories.")
    task_create_parser.add_argument("--do-not-edit", nargs="*", default=[], help="Denied files or directories.")
    task_create_parser.add_argument("--verification", default="python tools/llm_wiki.py task validate --strict", help="Verification command.")
    task_create_parser.add_argument("--created", default="", help="Creation date in YYYY-MM-DD format. Defaults to today.")
    task_create_parser.add_argument("--json", action="store_true", help="Emit JSON created task bundle.")

    task_report_parser = task_subparsers.add_parser("report", help="Summarize task queue metrics.")
    task_report_parser.add_argument("--json", action="store_true", help="Emit JSON metrics.")

    task_evidence_parser = task_subparsers.add_parser("evidence", help="Summarize task, progress, and checkpoint evidence.")
    task_evidence_parser.add_argument("--json", action="store_true", help="Emit JSON evidence summary.")

    task_readiness_parser = task_subparsers.add_parser("readiness", help="Report harness readiness and pending decisions.")
    task_readiness_parser.add_argument("--json", action="store_true", help="Emit JSON readiness report.")

    ingest_parser = subparsers.add_parser("ingest", help="Manage agent-assisted source ingest jobs.")
    ingest_subparsers = ingest_parser.add_subparsers(dest="ingest_command", required=True)

    enqueue_parser = ingest_subparsers.add_parser("enqueue", help="Queue raw sources for agent-assisted ingest.")
    enqueue_parser.add_argument("paths", nargs="*", help="Source paths under raw/sources/.")
    enqueue_parser.add_argument("--all-new", action="store_true", help="Queue available sources not yet completed.")
    enqueue_parser.add_argument("--json", action="store_true", help="Emit JSON result.")

    next_parser = ingest_subparsers.add_parser("next", help="Claim and print the next ingest package.")
    next_parser.add_argument("--json", action="store_true", help="Emit JSON package.")

    complete_parser = ingest_subparsers.add_parser("complete", help="Mark an ingest job completed.")
    complete_parser.add_argument("job_id", type=int)
    complete_parser.add_argument("--pages", nargs="*", default=[], help="Wiki pages created or updated.")
    complete_parser.add_argument("--notes", default="", help="Short completion notes.")
    complete_parser.add_argument("--json", action="store_true", help="Emit JSON result.")

    fail_parser = ingest_subparsers.add_parser("fail", help="Mark an ingest job failed.")
    fail_parser.add_argument("job_id", type=int)
    fail_parser.add_argument("--reason", required=True)
    fail_parser.add_argument("--json", action="store_true", help="Emit JSON result.")

    return parser


def cmd_init(root: Path) -> int:
    fts_enabled = ensure_project(root)
    print(f"Initialized LLM Wiki at {root}")
    print(f"Database: {root / DB_PATH}")
    print(f"FTS5: {'enabled' if fts_enabled else 'unavailable; LIKE fallback will be used'}")
    return 0


def cmd_rebuild(root: Path) -> int:
    stats = rebuild_index(root)
    print(
        "Rebuilt index: "
        f"{stats.sources} source(s), {stats.pages} page(s), {stats.links} wikilink(s), "
        f"FTS5 {'enabled' if stats.fts_enabled else 'unavailable'}."
    )
    return 0


def cmd_search(root: Path, query: str, limit: int, as_json: bool) -> int:
    results = search(root, query, limit)
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    if not results:
        print("No results.")
        return 0
    for row in results:
        snippet = (row.get("snippet") or "").replace("\n", " ").strip()
        print(f"[{row['kind']}] {row['path']} | {row['title']}")
        if snippet:
            print(f"  {snippet}")
    return 0


def cmd_lint(root: Path, as_json: bool, strict: bool) -> int:
    issues = collect_lint_issues(root)
    if as_json:
        print(json.dumps([issue.__dict__ for issue in issues], ensure_ascii=False, indent=2))
    elif not issues:
        print("No lint issues found.")
    else:
        for issue in issues:
            print(f"{issue.severity.upper()} {issue.path}: {issue.message}")
    return 1 if strict and issues else 0


def cmd_events(root: Path, limit: int, as_json: bool) -> int:
    events = list_events(root, limit)
    if as_json:
        print(json.dumps(events, ensure_ascii=False, indent=2))
        return 0
    if not events:
        print("No events.")
        return 0
    for event in events:
        object_path = f" | {event['object_path']}" if event["object_path"] else ""
        print(f"{event['occurred_at']} [{event['kind']}] {event['summary']}{object_path}")
    return 0


def cmd_quality(root: Path, full: bool, skip_frontend: bool, as_json: bool) -> int:
    results = run_quality(root, full=full, skip_frontend=skip_frontend)
    if as_json:
        print(json.dumps([result.to_json() for result in results], ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = "PASS" if result.exit_code == 0 else "FAIL"
            command = " ".join(result.command)
            print(f"{status} {result.name} ({result.exit_code}) [{result.duration_seconds:.2f}s]: {command}")
            if result.stdout.strip():
                print(result.stdout.rstrip())
            if result.stderr.strip():
                print(result.stderr.rstrip())
    return quality_exit_code(results)


def cmd_stack(args: argparse.Namespace, root: Path) -> int:
    if args.stack_command == "list":
        profiles = load_stack_profiles(root)
        if args.json:
            print(json.dumps([profile.to_json() for profile in profiles], ensure_ascii=False, indent=2))
        else:
            print("Available stack profiles:")
            for profile in profiles:
                print(f"- {profile.name}: {profile.description}")
                print(f"  Best for: {', '.join(profile.best_for)}")
                print(f"  Pros: {'; '.join(profile.pros[:2])}")
                print(f"  Cons: {'; '.join(profile.cons[:2])}")
                print("  Deployment: compare VPS/VDS and managed hosting during intake before publish handoff.")
        return 0

    if args.stack_command == "status":
        status = read_stack_status(root)
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(f"Stack status: {status['status']}")
            print(f"Selected profile: {status['selected_profile']}")
            if status["note"]:
                print(f"Note: {status['note']}")
        return 0 if status["status"] != "missing" else 1

    if args.stack_command == "select":
        try:
            status = select_stack_profile(root, args.profile)
        except ValueError as exc:
            print(str(exc))
            print(f"Allowed profiles: {allowed_profile_text(root)}")
            return 2
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(f"Selected stack profile: {status['selected_profile']}")
            print("STACK.md updated. No dependencies were installed and no frontend was scaffolded.")
        return 0

    if args.stack_command == "deploy-template":
        try:
            payload = deploy_template_payload(root, args.profile)
        except ValueError as exc:
            print(str(exc))
            return 2
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            handoff = payload["handoff"]
            assert isinstance(handoff, dict)
            print(f"Deploy handoff template: {payload['profile']} ({payload['status']})")
            print(f"Template: {payload['template_path']}")
            print(f"Selects stack: {str(payload['selects_stack']).lower()}")
            print(f"Deploy notes: {handoff['deploy_notes']}")
            print(f"Secret handling: {handoff['secret_handling']}")
        return 0

    raise ValueError(f"Unknown stack command: {args.stack_command}")


def cmd_ingest(args: argparse.Namespace, root: Path) -> int:
    if args.ingest_command == "enqueue":
        result = enqueue_ingest_jobs(root, args.paths, args.all_new)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        for row in result["queued"]:
            print(f"Queued job {row['job_id']}: {row['source_path']}")
        for row in result["skipped"]:
            print(f"Skipped {row['source_path']}: {row['reason']}")
        if not result["queued"] and not result["skipped"]:
            print("No sources matched.")
        return 0

    if args.ingest_command == "next":
        package = next_ingest_job(root)
        if args.json:
            print(json.dumps(package, ensure_ascii=False, indent=2))
            return 0
        if package is None:
            print("No queued ingest jobs.")
            return 0
        print_ingest_package(package)
        return 0

    if args.ingest_command == "complete":
        result = complete_ingest_job(root, args.job_id, args.pages, args.notes)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Completed ingest job {result['job_id']}.")
        return 0

    if args.ingest_command == "fail":
        result = fail_ingest_job(root, args.job_id, args.reason)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Failed ingest job {result['job_id']}: {result['reason']}")
        return 0

    raise ValueError(f"Unknown ingest command: {args.ingest_command}")


def print_ingest_package(package: dict) -> None:
    source = package["source"]
    extraction = package["extraction"]
    print(f"Job: {package['job_id']} ({package['status']})")
    print(f"Source: {source['path']}")
    print(f"Title: {source['title']}")
    print(f"SHA256: {source['sha256']}")
    print(f"Extractor: {extraction['extractor']}")
    for warning in extraction["warnings"]:
        print(f"Warning: {warning}")
    print("\nRelevant pages:")
    if package["relevant_pages"]:
        for page in package["relevant_pages"]:
            print(f"- {page['path']} | {page['title']} ({page['reason']})")
    else:
        print("- None found.")
    print("\nRequired output contract:")
    for item in package["required_output_contract"]:
        print(f"- {item}")
    print("\nExtracted text preview:")
    print(extraction["text_preview"] or "[No extracted text available.]")
    if extraction["truncated"]:
        print("\n[Preview truncated.]")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = resolve_root(args.root)

    if args.command == "init":
        return cmd_init(root)
    if args.command == "rebuild":
        return cmd_rebuild(root)
    if args.command == "search":
        return cmd_search(root, args.query, args.limit, args.json)
    if args.command == "lint":
        return cmd_lint(root, args.json, args.strict)
    if args.command == "events":
        return cmd_events(root, args.limit, args.json)
    if args.command == "quality":
        return cmd_quality(root, args.full, args.skip_frontend, args.json)
    if args.command == "conductor":
        return cmd_conductor(args, root)
    if args.command == "tools":
        return cmd_tools(args, root)
    if args.command == "stack":
        return cmd_stack(args, root)
    if args.command == "site":
        return cmd_site(args, root)
    if args.command == "security":
        return cmd_security(args, root)
    if args.command == "task":
        return cmd_task(args, root)
    if args.command == "ingest":
        return cmd_ingest(args, root)
    if args.command == "add-source":
        target = add_source(root, Path(args.path).resolve())
        print(f"Added source: {target}")
        return 0
    if args.command == "new-page":
        target = create_page(root, args.type, args.title, args.summary)
        print(f"Created page: {target}")
        return 0
    if args.command == "log":
        append_log(root, args.kind, args.summary, args.path)
        print("Log entry appended.")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2
