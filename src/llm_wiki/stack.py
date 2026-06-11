from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STACK_PATH = Path("STACK.md")
STACK_PROFILES_PATH = Path("agents") / "harness" / "stack-profiles.json"
PACKAGE_PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class StackProfile:
    name: str
    description: str
    commands: dict[str, str]
    required_tools: list[str]
    ci_policy: str
    frontend: bool
    backend: bool
    deploy_notes: str

    def to_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "commands": self.commands,
            "required_tools": self.required_tools,
            "ci_policy": self.ci_policy,
            "frontend": self.frontend,
            "backend": self.backend,
            "deploy_notes": self.deploy_notes,
        }


FIELD_RE = re.compile(r"^(?P<key>status|selected_profile|note):\s*(?P<value>.+?)\s*$", re.MULTILINE)


def profile_data_path(root: Path | None = None) -> Path:
    if root is not None and (root / STACK_PROFILES_PATH).exists():
        return root / STACK_PROFILES_PATH
    return PACKAGE_PROJECT_ROOT / STACK_PROFILES_PATH


def load_stack_profiles(root: Path | None = None) -> list[StackProfile]:
    path = profile_data_path(root)
    raw_profiles = json.loads(path.read_text(encoding="utf-8"))
    return [stack_profile_from_json(row) for row in raw_profiles]


def stack_profile_from_json(row: dict[str, Any]) -> StackProfile:
    return StackProfile(
        name=str(row["name"]),
        description=str(row["description"]),
        commands={str(key): str(value) for key, value in dict(row.get("commands", {})).items()},
        required_tools=[str(value) for value in row.get("required_tools", [])],
        ci_policy=str(row.get("ci_policy", "")),
        frontend=bool(row.get("frontend", False)),
        backend=bool(row.get("backend", False)),
        deploy_notes=str(row.get("deploy_notes", "")),
    )


def profiles_by_name(root: Path | None = None) -> dict[str, StackProfile]:
    return {profile.name: profile for profile in load_stack_profiles(root)}


STACK_PROFILES = load_stack_profiles(PACKAGE_PROJECT_ROOT)
PROFILE_BY_NAME = {profile.name: profile for profile in STACK_PROFILES}


def allowed_profile_names(root: Path | None = None) -> list[str]:
    return [profile.name for profile in load_stack_profiles(root)]


def allowed_profile_text(root: Path | None = None) -> str:
    return ", ".join(allowed_profile_names(root))


def parse_stack_text(text: str) -> dict[str, str]:
    fields = {match.group("key"): match.group("value").strip() for match in FIELD_RE.finditer(text)}
    return {
        "status": fields.get("status", "unknown"),
        "selected_profile": fields.get("selected_profile", "none"),
        "note": fields.get("note", ""),
    }


def read_stack_status(root: Path) -> dict[str, str]:
    path = root / STACK_PATH
    if not path.exists():
        return {
            "status": "missing",
            "selected_profile": "none",
            "note": "STACK.md is missing.",
            "path": STACK_PATH.as_posix(),
        }
    status = parse_stack_text(path.read_text(encoding="utf-8", errors="replace"))
    status["path"] = STACK_PATH.as_posix()
    return status


def stack_is_selected(root: Path) -> bool:
    status = read_stack_status(root)
    return status["status"] == "selected" and status["selected_profile"] in profiles_by_name(root)


def select_stack_profile(root: Path, profile_name: str) -> dict[str, str]:
    profiles = profiles_by_name(root)
    if profile_name not in profiles:
        raise ValueError(f"Unknown stack profile: {profile_name}. Allowed profiles: {allowed_profile_text(root)}.")
    path = root / STACK_PATH
    path.write_text(render_selected_stack(profile_name, root), encoding="utf-8")
    return read_stack_status(root)


def render_selected_stack(profile_name: str, root: Path | None = None) -> str:
    profile = profiles_by_name(root)[profile_name]
    commands = "\n".join(f"- {name}: `{command}`" for name, command in profile.commands.items())
    tools = "\n".join(f"- {tool}" for tool in profile.required_tools)
    return f"""# Stack Selection

status: selected
selected_profile: {profile.name}
note: selected by the user or agent during the first project chat

Production implementation may begin only when `PRODUCT.md`, `DESIGN.md`, task ownership, and verification requirements are also ready.

## Selected Profile

- `{profile.name}`: {profile.description}

## Commands

{commands}

## Required Tools

{tools}

## CI Policy

{profile.ci_policy}

## Deploy Notes

{profile.deploy_notes}

## Available Profiles

See `agents/harness/stack-options.md` and `agents/harness/stack-profiles.json`.

## Selection Notes

- This file records the stack choice only.
- No dependencies were installed.
- No frontend files were changed automatically.
"""
