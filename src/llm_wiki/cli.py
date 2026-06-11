from __future__ import annotations

import argparse
import json
from pathlib import Path

from .doctor import build_doctor_report
from .quality import quality_exit_code, run_quality
from .security import run_security_audit
from .site_generator import create_site_project
from .site_self_test import run_generated_site_self_test, run_site_init_self_test
from .stack import (
    allowed_profile_text,
    load_stack_profiles,
    read_stack_status,
    select_stack_profile,
)
from .tasks import (
    create_task,
    list_tasks,
    next_task,
    readiness_report,
    set_task_status,
    task_metrics,
    validate_task_queue,
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

    stack_parser = subparsers.add_parser("stack", help="Inspect and select the project stack profile.")
    stack_subparsers = stack_parser.add_subparsers(dest="stack_command", required=True)
    stack_list_parser = stack_subparsers.add_parser("list", help="List available stack profiles.")
    stack_list_parser.add_argument("--json", action="store_true", help="Emit JSON stack profiles.")
    stack_status_parser = stack_subparsers.add_parser("status", help="Show current stack status from STACK.md.")
    stack_status_parser.add_argument("--json", action="store_true", help="Emit JSON stack status.")
    stack_select_parser = stack_subparsers.add_parser("select", help="Record the selected stack profile in STACK.md.")
    stack_select_parser.add_argument("profile", help="Stack profile name.")
    stack_select_parser.add_argument("--json", action="store_true", help="Emit JSON stack status.")

    site_parser = subparsers.add_parser("site", help="Create clean site-development projects.")
    site_subparsers = site_parser.add_subparsers(dest="site_command", required=True)
    site_init_parser = site_subparsers.add_parser("init", help="Create a clean generated site project.")
    site_init_parser.add_argument("target", help="Target directory for the new site project.")
    site_init_parser.add_argument("--self-test", action="store_true", help="Run generated project core self-test after creation.")
    site_init_parser.add_argument("--json", action="store_true", help="Emit JSON init result.")
    site_self_test_parser = site_subparsers.add_parser("self-test", help="Create a temporary starter and run core self-test.")
    site_self_test_parser.add_argument("--json", action="store_true", help="Emit JSON self-test results.")
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
            print("STACK.md updated. No dependencies were installed and frontend/ was not changed.")
        return 0

    raise ValueError(f"Unknown stack command: {args.stack_command}")


def cmd_site(args: argparse.Namespace, root: Path) -> int:
    if args.site_command == "init":
        result = create_site_project(root, Path(args.target))
        self_test = run_site_init_self_test(root, result.target) if args.self_test else None
        if args.json:
            payload = {
                "target": str(result.target),
                "copied_files": result.copied_files,
                "self_test": self_test.to_json() if self_test else None,
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0 if self_test is None or self_test.status == "passed" else 1
        print(f"Created clean site project: {result.target}")
        print(f"Copied files: {result.copied_files}")
        if self_test is not None:
            print_self_test_result(self_test.to_json())
            return 0 if self_test.status == "passed" else 1
        print("Next: fill PRODUCT.md and DESIGN.md, then run python tools/llm_wiki.py task readiness")
        return 0
    if args.site_command == "self-test":
        result = run_generated_site_self_test(root)
        if args.json:
            print(json.dumps(result.to_json(), ensure_ascii=False, indent=2))
        else:
            print_self_test_result(result.to_json())
        return 0 if result.status == "passed" else 1
    if args.site_command == "doctor":
        report = build_doctor_report(root, skip_self_test=args.skip_self_test, run_security=args.run_security)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_doctor_report(report)
        return 0 if report["status"] == "ok" else 1
    raise ValueError(f"Unknown site command: {args.site_command}")


def cmd_security(args: argparse.Namespace, root: Path) -> int:
    if args.security_command == "audit":
        allowlist_path = Path(args.allowlist) if args.allowlist else None
        if allowlist_path is not None and not allowlist_path.is_absolute():
            allowlist_path = root / allowlist_path
        result = run_security_audit(
            root,
            blocking=args.blocking,
            no_record=args.no_record,
            allowlist_path=allowlist_path,
        )
        if args.json:
            print(json.dumps(result.to_json(), ensure_ascii=False, indent=2))
        else:
            print_security_result(result.to_json())
        return 1 if args.blocking and result.unresolved_count else 0
    raise ValueError(f"Unknown security command: {args.security_command}")


def cmd_task(args: argparse.Namespace, root: Path) -> int:
    if args.task_command == "list":
        records = list_tasks(root, status=args.status or None)
        if args.json:
            print(json.dumps([record.to_json() for record in records], ensure_ascii=False, indent=2))
        elif not records:
            print("No tasks found.")
        else:
            for record in records:
                print_task_record(record)
        return 0

    if args.task_command == "next":
        record = next_task(root)
        if args.json:
            print(json.dumps(record.to_json() if record else None, ensure_ascii=False, indent=2))
        elif record is None:
            print("No ready or planned tasks.")
        else:
            print_task_record(record)
        return 0

    if args.task_command == "validate":
        issues = validate_task_queue(root)
        if args.json:
            print(json.dumps([issue.__dict__ for issue in issues], ensure_ascii=False, indent=2))
        elif not issues:
            print("No task validation issues found.")
        else:
            for issue in issues:
                print(f"{issue.severity.upper()} {issue.path}: {issue.message}")
        return 1 if args.strict and issues else 0

    if args.task_command == "set-status":
        try:
            record = set_task_status(root, args.path, args.status, force=args.force)
        except ValueError as exc:
            print(str(exc))
            return 2
        if args.json:
            print(json.dumps(record.to_json(), ensure_ascii=False, indent=2))
        else:
            print(f"Updated {record.path}: {record.status}")
        return 0

    if args.task_command == "create":
        result = create_task(
            root,
            title=args.title,
            objective=args.objective,
            role_owner=args.owner,
            status=args.status,
            owned_files=args.owned or None,
            do_not_edit=args.do_not_edit or None,
            verification_command=args.verification,
            created=args.created or None,
        )
        if args.json:
            print(json.dumps(result.to_json(), ensure_ascii=False, indent=2))
        else:
            print(f"Created {result.task.path}")
            print(f"Progress: {result.progress_path}")
            print(f"Checkpoint: {result.checkpoint_path}")
        return 0

    if args.task_command == "report":
        metrics = task_metrics(root)
        if args.json:
            print(json.dumps(metrics, ensure_ascii=False, indent=2))
        else:
            print(f"Tasks: {metrics['total']} total, {metrics['open']} open, {metrics['closed']} closed")
            by_status = metrics["by_status"]
            assert isinstance(by_status, dict)
            for status, count in by_status.items():
                if count:
                    print(f"- {status}: {count}")
        return 0

    if args.task_command == "readiness":
        report = readiness_report(root)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            env = "ready" if report["environment_ready"] else "has issues"
            product = "ready" if report["product_design_ready"] else "pending decisions"
            print(f"Environment: {env}")
            print(f"Product/design: {product}")
            pending = report["pending_decisions"]
            if pending:
                print("Pending decisions:")
                for item in pending:
                    print(f"- {item}")
            print(f"Next command: {report['next_command']}")
        return 0

    raise ValueError(f"Unknown task command: {args.task_command}")


def print_task_record(record) -> None:
    print(f"{record.status:11} {record.path} | {record.title}")
    if record.objective:
        print(f"  {record.objective}")


def print_self_test_result(payload: dict[str, object]) -> None:
    print(f"Generated project self-test: {payload['status']}")
    print(f"Target: {payload['target']}")
    for result in payload["quality_results"]:
        assert isinstance(result, dict)
        status = "PASS" if result["exit_code"] == 0 else "FAIL"
        print(f"{status} {result['name']} ({result['exit_code']})")


def print_doctor_report(report: dict[str, object]) -> None:
    print(f"Doctor status: {report['status']}")
    readiness = report["readiness"]
    assert isinstance(readiness, dict)
    print(f"Implementation ready: {readiness['implementation_ready']}")
    print(f"Next command: {readiness['next_command']}")
    blockers = readiness.get("blockers", [])
    if blockers:
        print("Blockers:")
        for blocker in blockers:
            assert isinstance(blocker, dict)
            print(f"- {blocker['path']}: {blocker['message']}")


def print_security_result(payload: dict[str, object]) -> None:
    print(f"Security audit: {payload['status']}")
    print(f"Unresolved items: {payload['unresolved_count']}")
    if payload.get("message"):
        print(str(payload["message"]))


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
