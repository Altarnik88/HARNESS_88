from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cli_support import print_blocker_preview, site_lock_state, yes_no
from .doctor import build_doctor_report
from .gates import gates_status
from .intake import intake_status
from .references import reference_status
from .site_generator import create_site_project
from .site_self_test import run_generated_site_self_test, run_site_init_self_test


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
    if args.site_command == "intake":
        status = intake_status(root)
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print_intake_status(status)
        return 0
    if args.site_command == "references":
        status = reference_status(root)
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print_reference_status(status)
        return 0
    if args.site_command == "gates":
        status = gates_status(root)
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print_gates_status(status)
        return 0
    if args.site_command == "doctor":
        report = build_doctor_report(root, skip_self_test=args.skip_self_test, run_security=args.run_security)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_doctor_report(report)
        return 0 if report["status"] == "ok" else 1
    raise ValueError(f"Unknown site command: {args.site_command}")


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
    print(f"Core workflow: {'ready' if readiness['core_development_ready'] else 'has issues'}")
    print(f"Core work may proceed: {yes_no(bool(readiness['core_development_ready']))}")
    print(f"Site intake: {'ready' if readiness['intake_ready'] else 'pending'}")
    print(f"References: {'ready' if readiness['references_ready'] else 'pending'}")
    print(f"Site implementation: {'ready' if readiness['site_implementation_ready'] else 'not configured'}")
    print(f"Site implementation lock: {site_lock_state(readiness)}")
    print(f"Delivery gates: {'ready' if readiness['delivery_gates_ready'] else 'pending'}")
    print(f"Publish handoff: {'ready' if readiness['publish_ready'] else 'blocked'}")
    tooling = report.get("tooling", {})
    if isinstance(tooling, dict):
        summary = tooling.get("summary", {})
        if isinstance(summary, dict):
            print(f"Tooling: {tooling.get('status', 'unknown')} ({summary.get('available', 0)} available, {summary.get('missing', 0)} missing)")
    print(f"Next command: {readiness['next_command']}")
    print_blocker_preview(readiness.get("blockers", []))


def print_intake_status(status: dict[str, object]) -> None:
    print(f"Site intake: {'ready' if status['intake_ready'] else 'pending'}")
    print(f"References: {'ready' if status['references_ready'] else 'pending'}")
    print(f"Path: {status['path']}")
    print(f"Status: {status['status']}")
    missing = status.get("missing_fields", [])
    if missing:
        print("Missing fields:")
        for field in missing:
            print(f"- {field}")
    blockers = status.get("blockers", [])
    if blockers:
        print("Blockers:")
        for blocker in blockers:
            assert isinstance(blocker, dict)
            print(f"- {blocker['message']}")


def print_reference_status(status: dict[str, object]) -> None:
    print(f"Reference analysis: {'ready' if status['reference_analysis_ready'] else 'pending'}")
    print(f"Path: {status['path']}")
    print(f"Status: {status['status']}")
    pending = status.get("pending_reference_gates", [])
    if pending:
        print("Pending reference gates:")
        for gate in pending:
            print(f"- {gate}")
    manifest = status.get("manifest", {})
    if isinstance(manifest, dict):
        print(f"Manifest: {'valid' if manifest.get('valid') else 'pending'}")
        print(f"Captured pages: {manifest.get('captured_page_count', 0)}")
    blockers = status.get("blockers", [])
    if blockers:
        print("Blockers:")
        for blocker in blockers:
            assert isinstance(blocker, dict)
            print(f"- {blocker['message']}")


def print_gates_status(status: dict[str, object]) -> None:
    print(f"Delivery gates: {'ready' if status['delivery_gates_ready'] else 'pending'}")
    print(f"Publish handoff: {'ready' if status['publish_ready'] else 'blocked'}")
    print(f"Path: {status['path']}")
    print(f"Status: {status['status']}")
    pending = status.get("pending_delivery_gates", [])
    if pending:
        print("Pending delivery gates:")
        for gate in pending:
            print(f"- {gate}")
    blockers = status.get("blockers", [])
    if blockers:
        print("Blockers:")
        for blocker in blockers:
            assert isinstance(blocker, dict)
            print(f"- {blocker['message']}")
