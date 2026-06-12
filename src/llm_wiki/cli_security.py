from __future__ import annotations

import argparse
import json
from pathlib import Path

from .security import build_secret_plan, rejected_secret_plan_receipt, run_security_audit


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
    if args.security_command == "secret-plan":
        try:
            receipt = build_secret_plan(args.provider, args.vars, args.operation)
            code = 0
        except ValueError as exc:
            receipt = rejected_secret_plan_receipt(str(exc))
            code = 2
        if args.json:
            print(json.dumps(receipt, ensure_ascii=False, indent=2))
        else:
            print_secret_plan_receipt(receipt)
        return code
    raise ValueError(f"Unknown security command: {args.security_command}")


def print_security_result(payload: dict[str, object]) -> None:
    print(f"Security audit: {payload['status']}")
    print(f"Unresolved items: {payload['unresolved_count']}")
    if payload.get("message"):
        print(str(payload["message"]))


def print_secret_plan_receipt(payload: dict[str, object]) -> None:
    print(f"Secret plan: {payload['status']}")
    if payload.get("provider"):
        print(f"Provider: {payload['provider']}")
    if payload.get("required_variable_names"):
        print("Required variables:")
        for name in payload["required_variable_names"]:
            print(f"- {name}")
    if payload.get("operation"):
        print(f"Operation: {payload['operation']}")
    print(f"Secret values visible: {str(payload['secret_values_visible']).lower()}")
    if payload.get("message"):
        print(str(payload["message"]))
    if payload.get("next_action"):
        print(f"Next action: {payload['next_action']}")
