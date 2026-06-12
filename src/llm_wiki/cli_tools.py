from __future__ import annotations

import argparse
import json
from pathlib import Path

from .capabilities import capability_audit


MAX_HUMAN_TOOL_ITEMS = 8


def cmd_tools(args: argparse.Namespace, root: Path) -> int:
    if args.tools_command == "audit":
        codex_home = Path(args.codex_home) if args.codex_home else None
        report = capability_audit(root, codex_home=codex_home)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_tools_audit(report)
        return 0
    raise ValueError(f"Unknown tools command: {args.tools_command}")


def print_tools_audit(report: dict[str, object]) -> None:
    print(f"Tooling status: {report['status']}")
    summary = report["summary"]
    assert isinstance(summary, dict)
    print(f"Available: {summary['available']} / {summary['total']}")
    print(f"Host-managed MCP/tools: {summary.get('host_managed', 0)}")
    print(f"Missing required: {summary['required_missing']}")
    print(f"Missing recommended: {summary['recommended_missing']}")
    print(f"Missing optional: {summary['optional_missing']}")
    print(str(report["setup_policy"]))
    attention_items = [item for item in report["items"] if isinstance(item, dict) and item.get("status") == "missing"]
    if attention_items:
        print("Capabilities needing attention:")
    else:
        print("Capabilities needing attention: none")
    for item in attention_items[:MAX_HUMAN_TOOL_ITEMS]:
        assert isinstance(item, dict)
        print(f"- {item['status']} [{item['importance']}] {item['name']}: {item['description']}")
        if item.get("resource_url"):
            print(f"  Source: {item['resource_url']}")
        if item.get("install_hint"):
            print(f"  Next: {item['install_hint']}")
    if len(attention_items) > MAX_HUMAN_TOOL_ITEMS:
        print(f"... {len(attention_items) - MAX_HUMAN_TOOL_ITEMS} more item(s); use --json for full detail.")
    actions = report.get("next_actions", [])
    if actions:
        print("Permission prompts:")
        for action in actions[:MAX_HUMAN_TOOL_ITEMS]:
            assert isinstance(action, dict)
            print(f"- {action['prompt']}")
        if len(actions) > MAX_HUMAN_TOOL_ITEMS:
            print(f"... {len(actions) - MAX_HUMAN_TOOL_ITEMS} more prompt(s); use --json for full detail.")
