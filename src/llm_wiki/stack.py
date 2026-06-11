from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


STACK_PATH = Path("STACK.md")


@dataclass(frozen=True)
class StackProfile:
    name: str
    description: str

    def to_json(self) -> dict[str, str]:
        return {"name": self.name, "description": self.description}


STACK_PROFILES = [
    StackProfile(
        "next-static",
        "Next.js App Router + TypeScript + Tailwind for landing pages, marketing sites, and frontend-first sites.",
    ),
    StackProfile(
        "next-fullstack",
        "Next.js App Router + TypeScript + Tailwind, with backend and data decisions made later, for SaaS or app-like sites.",
    ),
    StackProfile(
        "astro-content",
        "Astro for SEO/content-heavy sites, blogs, and documentation.",
    ),
    StackProfile(
        "sveltekit",
        "SvelteKit for interactive applications.",
    ),
    StackProfile(
        "custom",
        "A user-defined stack selected after clarification.",
    ),
]

PROFILE_BY_NAME = {profile.name: profile for profile in STACK_PROFILES}

FIELD_RE = re.compile(r"^(?P<key>status|selected_profile|note):\s*(?P<value>.+?)\s*$", re.MULTILINE)


def allowed_profile_names() -> list[str]:
    return [profile.name for profile in STACK_PROFILES]


def allowed_profile_text() -> str:
    return ", ".join(allowed_profile_names())


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
    return status["status"] == "selected" and status["selected_profile"] in PROFILE_BY_NAME


def select_stack_profile(root: Path, profile_name: str) -> dict[str, str]:
    if profile_name not in PROFILE_BY_NAME:
        raise ValueError(f"Unknown stack profile: {profile_name}. Allowed profiles: {allowed_profile_text()}.")
    path = root / STACK_PATH
    path.write_text(render_selected_stack(profile_name), encoding="utf-8")
    return read_stack_status(root)


def render_selected_stack(profile_name: str) -> str:
    profile = PROFILE_BY_NAME[profile_name]
    return f"""# Stack Selection

status: selected
selected_profile: {profile.name}
note: selected by the user or agent during the first project chat

Production implementation may begin only when `PRODUCT.md`, `DESIGN.md`, task ownership, and verification requirements are also ready.

## Selected Profile

- `{profile.name}`: {profile.description}

## Available Profiles

See `agents/harness/stack-options.md`.

## Selection Notes

- This file records the stack choice only.
- No dependencies were installed.
- No frontend files were changed automatically.
"""
