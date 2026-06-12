from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cli_support import print_blocker_preview, site_lock_state, summary_count, yes_no
from .evidence import evidence_report
from .tasks import (
    create_task,
    list_tasks,
    next_task,
    readiness_report,
    set_task_status,
    task_metrics,
    validate_task_queue,
)


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

    if args.task_command == "evidence":
        report = evidence_report(root)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_evidence_report(report)
        return 0

    if args.task_command == "readiness":
        report = readiness_report(root)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            env = "ready" if report["environment_ready"] else "has issues"
            product = "ready" if report["product_design_ready"] else "pending decisions"
            print(f"Environment: {env}")
            print(f"Core development: {'ready' if report['core_development_ready'] else 'has issues'}")
            print(f"Core work may proceed: {yes_no(bool(report['core_development_ready']))}")
            print(f"Product/design: {product}")
            print(f"Site intake: {'ready' if report['intake_ready'] else 'pending'}")
            print(f"References: {'ready' if report['references_ready'] else 'pending'}")
            print(f"Site implementation: {'ready' if report['site_implementation_ready'] else 'not configured'}")
            print(f"Site implementation lock: {site_lock_state(report)}")
            print(f"Delivery gates: {'ready' if report['delivery_gates_ready'] else 'pending'}")
            print(f"Publish handoff: {'ready' if report['publish_ready'] else 'blocked'}")
            pending = report["pending_decisions"]
            if pending:
                print("Pending decisions:")
                for item in pending:
                    print(f"- {item}")
            print_blocker_preview(report.get("blockers", []))
            print(f"Next command: {report['next_command']}")
        return 0

    raise ValueError(f"Unknown task command: {args.task_command}")


def print_task_record(record) -> None:
    print(f"{record.status:11} {record.path} | {record.title}")
    if record.objective:
        print(f"  {record.objective}")


def print_evidence_report(report: dict[str, object]) -> None:
    metrics = report["task_metrics"]
    assert isinstance(metrics, dict)
    summary = report["summary"]
    assert isinstance(summary, dict)
    print(f"Tasks: {metrics['total']} total, {metrics['open']} open, {metrics['closed']} closed")
    print(f"Missing support files: {summary_count(summary, 'missing_support_files')}")
    print(f"Verified without verification evidence: {summary_count(summary, 'verified_without_verification')}")
    print(f"Implementation evidence: {summary_count(summary, 'implementation_evidence')}")
    print(f"Verification evidence: {summary_count(summary, 'verification_evidence')}")
    print(f"Review evidence: {summary_count(summary, 'review_evidence')}")
    print(f"Wiki/log evidence: {summary_count(summary, 'wiki_log_evidence')}")
    print(f"Residual risk: {summary_count(summary, 'residual_risk')}")
    issues = report.get("issues", [])
    if issues:
        print("Issues:")
        for issue in issues:
            assert isinstance(issue, dict)
            print(f"- {issue['path']}: {issue['message']}")
