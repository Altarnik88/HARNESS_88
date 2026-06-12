from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CapabilitySpec:
    id: str
    name: str
    kind: str
    importance: str
    description: str
    detection: str
    terms: tuple[str, ...]
    install_hint: str


CAPABILITY_SPECS = [
    CapabilitySpec(
        id="local.python",
        name="Python",
        kind="local-tool",
        importance="required",
        description="Runs the HARNESS_88 CLI, tests, wiki rebuilds, and quality gates.",
        detection="command",
        terms=("python",),
        install_hint="Install Python >= 3.11, then rerun python tools/llm_wiki.py tools audit.",
    ),
    CapabilitySpec(
        id="local.git",
        name="Git",
        kind="local-tool",
        importance="required",
        description="Tracks task changes, commits, branches, and GitHub pushes.",
        detection="command",
        terms=("git",),
        install_hint="Install Git, then rerun python tools/llm_wiki.py tools audit.",
    ),
    CapabilitySpec(
        id="local.node",
        name="Node.js",
        kind="local-tool",
        importance="recommended",
        description="Runs optional frontend checks for the bundled Next.js starter.",
        detection="command",
        terms=("node",),
        install_hint="Install Node.js >= 20.9.0 when frontend checks or implementation are in scope.",
    ),
    CapabilitySpec(
        id="local.npm",
        name="npm",
        kind="local-tool",
        importance="recommended",
        description="Installs and runs optional frontend dependencies.",
        detection="command",
        terms=("npm",),
        install_hint="Install npm with Node.js, then run cd frontend && npm ci only after approval.",
    ),
    CapabilitySpec(
        id="local.gh",
        name="GitHub CLI",
        kind="local-tool",
        importance="recommended",
        description="Supports authenticated GitHub PR, issue, CI, and release workflows.",
        detection="command",
        terms=("gh",),
        install_hint="Install GitHub CLI and authenticate it, or use the Codex GitHub plugin when available.",
    ),
    CapabilitySpec(
        id="skill.playwright",
        name="Playwright skill",
        kind="codex-skill",
        importance="recommended",
        description="Automates browser flows, screenshots, responsive checks, and UI QA.",
        detection="codex-skill",
        terms=("playwright",),
        install_hint="Ask permission to install or download a Playwright skill before browser automation work.",
    ),
    CapabilitySpec(
        id="skill.gh-cli",
        name="gh-cli skill",
        kind="codex-skill",
        importance="recommended",
        description="Routes GitHub work through authenticated gh CLI workflows.",
        detection="codex-skill",
        terms=("gh-cli",),
        install_hint="Ask permission to install or download the gh-cli skill before GitHub CLI work.",
    ),
    CapabilitySpec(
        id="plugin.browser",
        name="Browser plugin",
        kind="codex-plugin",
        importance="recommended",
        description="Opens local UI previews and supports visual/browser checks.",
        detection="codex-plugin",
        terms=("browser", "browser-use", "control-in-app-browser"),
        install_hint="Ask permission to connect the Browser plugin in Codex before local UI verification.",
    ),
    CapabilitySpec(
        id="plugin.github",
        name="GitHub plugin",
        kind="codex-plugin",
        importance="recommended",
        description="Reads and writes GitHub repository, pull request, issue, and CI context when allowed.",
        detection="codex-plugin",
        terms=("github",),
        install_hint="Ask permission to connect the GitHub plugin in Codex before GitHub automation.",
    ),
    CapabilitySpec(
        id="plugin.product-design",
        name="Product Design plugin",
        kind="codex-plugin",
        importance="recommended",
        description="Supports design brief context, visual ideation, and image-to-code flows.",
        detection="codex-plugin",
        terms=("product-design", "product_design"),
        install_hint="Ask permission to connect the Product Design plugin before product UI design work.",
    ),
    CapabilitySpec(
        id="mcp.serena",
        name="Serena MCP",
        kind="mcp-server",
        importance="recommended",
        description="Provides focused symbol-level code discovery before implementation.",
        detection="codex-plugin",
        terms=("serena",),
        install_hint="Ask permission to connect Serena MCP or use local rg/file reads as fallback.",
    ),
    CapabilitySpec(
        id="mcp.context7",
        name="Context7 MCP",
        kind="mcp-server",
        importance="recommended",
        description="Fetches current library, framework, SDK, CLI, and cloud documentation.",
        detection="codex-plugin",
        terms=("context7",),
        install_hint="Ask permission to connect Context7 MCP before current-docs lookups.",
    ),
    CapabilitySpec(
        id="mcp.filesystem",
        name="Filesystem MCP",
        kind="mcp-server",
        importance="recommended",
        description="Provides scoped project file access when the host supports MCP filesystem tools.",
        detection="codex-plugin",
        terms=("filesystem",),
        install_hint="Ask permission to connect a project-scoped filesystem MCP only when the host needs it.",
    ),
    CapabilitySpec(
        id="mcp.sqlite",
        name="SQLite MCP",
        kind="mcp-server",
        importance="optional",
        description="Supports read-only inspection of local SQLite state when delegated.",
        detection="codex-plugin",
        terms=("sqlite",),
        install_hint="Ask permission to connect SQLite MCP in read-only mode when database inspection is needed.",
    ),
    CapabilitySpec(
        id="mcp.node-repl",
        name="node_repl MCP",
        kind="mcp-server",
        importance="optional",
        description="Supports compact JavaScript checks and browser automation helpers when delegated.",
        detection="codex-plugin",
        terms=("node-repl", "node_repl"),
        install_hint="Ask permission to connect node_repl only for delegated JavaScript/browser checks.",
    ),
    CapabilitySpec(
        id="skill.imagegen",
        name="imagegen skill",
        kind="codex-skill",
        importance="optional",
        description="Generates bitmap assets, mockups, textures, sprites, and visual variants.",
        detection="codex-skill",
        terms=("imagegen",),
        install_hint="Ask permission to install imagegen only when bitmap asset generation is needed.",
    ),
    CapabilitySpec(
        id="plugin.sentry",
        name="Sentry plugin/skill",
        kind="codex-plugin",
        importance="optional",
        description="Supports read-only production error inspection when environment auth is configured.",
        detection="codex-plugin",
        terms=("sentry",),
        install_hint="Ask permission to connect Sentry only when production diagnostics are requested.",
    ),
    CapabilitySpec(
        id="plugin.remotion",
        name="Remotion plugin/skill",
        kind="codex-plugin",
        importance="optional",
        description="Supports explicit video/render/export workflows.",
        detection="codex-plugin",
        terms=("remotion",),
        install_hint="Ask permission to connect Remotion only for explicit video/render tasks.",
    ),
    CapabilitySpec(
        id="plugin.canva",
        name="Canva plugin",
        kind="codex-plugin",
        importance="optional",
        description="Supports Canva presentations, social assets, resizing, and translation workflows.",
        detection="codex-plugin",
        terms=("canva",),
        install_hint="Ask permission to connect Canva only for explicit Canva design work.",
    ),
    CapabilitySpec(
        id="plugin.creative-production",
        name="Creative Production plugin",
        kind="codex-plugin",
        importance="optional",
        description="Supports campaign ideas, visual directions, mood boards, ads, logos, and scene exploration.",
        detection="codex-plugin",
        terms=("creative-production", "creative_production"),
        install_hint="Ask permission to connect Creative Production only for delegated creative exploration.",
    ),
    CapabilitySpec(
        id="plugin.data-analytics",
        name="Data Analytics plugin",
        kind="codex-plugin",
        importance="optional",
        description="Supports source-backed analysis, dashboards, reports, KPI work, and data visuals.",
        detection="codex-plugin",
        terms=("data-analytics", "datasciencewidgets"),
        install_hint="Ask permission to connect Data Analytics only for source-backed analytical work.",
    ),
    CapabilitySpec(
        id="plugin.documents",
        name="Documents plugin",
        kind="codex-plugin",
        importance="optional",
        description="Supports Word/document creation, editing, comments, and render verification.",
        detection="codex-plugin",
        terms=("documents",),
        install_hint="Ask permission to connect Documents only when document artifacts are requested.",
    ),
    CapabilitySpec(
        id="plugin.spreadsheets",
        name="Spreadsheets plugin",
        kind="codex-plugin",
        importance="optional",
        description="Supports spreadsheet creation, analysis, formatting, formulas, charts, and exports.",
        detection="codex-plugin",
        terms=("spreadsheets",),
        install_hint="Ask permission to connect Spreadsheets only when spreadsheet artifacts are provided or requested.",
    ),
    CapabilitySpec(
        id="plugin.figma",
        name="Figma plugin/MCP",
        kind="codex-plugin",
        importance="optional",
        description="Supports explicit Figma design, FigJam, Slides, and design-system workflows.",
        detection="codex-plugin",
        terms=("figma",),
        install_hint="Ask permission to connect Figma only when a Figma workflow is requested.",
    ),
    CapabilitySpec(
        id="plugin.supabase",
        name="Supabase plugin",
        kind="codex-plugin",
        importance="optional",
        description="Supports explicit Supabase database, auth, storage, realtime, and edge-function work.",
        detection="codex-plugin",
        terms=("supabase",),
        install_hint="Ask permission to connect Supabase only when Supabase is selected.",
    ),
]


def capability_audit(root: Path, codex_home: Path | None = None) -> dict[str, object]:
    codex_home = resolve_codex_home(codex_home)
    installed_names = installed_codex_names(codex_home)
    items = [capability_item(spec, codex_home, installed_names) for spec in CAPABILITY_SPECS]
    summary = capability_summary(items)
    next_actions = build_next_actions(items)
    return {
        "status": "ready" if summary["required_missing"] == 0 and summary["recommended_missing"] == 0 else "needs-setup",
        "root": str(root),
        "codex_home": str(codex_home) if codex_home else "",
        "setup_policy": "No tools, skills, MCP servers, or plugins are installed automatically. Ask the user for permission before connecting Codex plugins, downloading skills from GitHub, or installing local tools.",
        "summary": summary,
        "items": items,
        "next_actions": next_actions,
    }


def resolve_codex_home(codex_home: Path | None) -> Path | None:
    if codex_home is not None:
        return codex_home
    raw = os.environ.get("CODEX_HOME")
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".codex"


def installed_codex_names(codex_home: Path | None) -> set[str]:
    if codex_home is None or not codex_home.exists():
        return set()
    names: set[str] = set()
    for skill_root in [codex_home / "skills", codex_home / "plugins" / "cache"]:
        if not skill_root.exists():
            continue
        for skill in skill_root.rglob("SKILL.md"):
            names.add(normalize(skill.parent.name))
            for part in skill.relative_to(skill_root).parts[:-1]:
                names.add(normalize(part))
    plugin_cache = codex_home / "plugins" / "cache"
    if plugin_cache.exists():
        for manifest in plugin_cache.rglob("plugin.json"):
            names.add(normalize(manifest.parent.name))
            for part in manifest.relative_to(plugin_cache).parts[:-1]:
                names.add(normalize(part))
    return names


def capability_item(spec: CapabilitySpec, codex_home: Path | None, installed_names: set[str]) -> dict[str, object]:
    available = detect_capability(spec, installed_names)
    status = "available" if available else "missing"
    return {
        "id": spec.id,
        "name": spec.name,
        "kind": spec.kind,
        "importance": spec.importance,
        "status": status,
        "description": spec.description,
        "detected_by": detection_label(spec, codex_home, available),
        "install_hint": "" if available else spec.install_hint,
        "requires_permission": not available,
    }


def detect_capability(spec: CapabilitySpec, installed_names: set[str]) -> bool:
    if spec.detection == "command":
        return any(shutil.which(term) for term in spec.terms)
    return any(normalize(term) in installed_names for term in spec.terms)


def detection_label(spec: CapabilitySpec, codex_home: Path | None, available: bool) -> str:
    if spec.detection == "command":
        found = next((term for term in spec.terms if shutil.which(term)), "")
        return f"command:{found}" if found else "command-not-found"
    if codex_home is None:
        return "codex-home-unavailable"
    return f"codex-home:{codex_home}" if available else f"not-found-under:{codex_home}"


def capability_summary(items: list[dict[str, object]]) -> dict[str, int]:
    summary = {
        "total": len(items),
        "available": 0,
        "missing": 0,
        "required_missing": 0,
        "recommended_missing": 0,
        "optional_missing": 0,
    }
    for item in items:
        status = str(item["status"])
        importance = str(item["importance"])
        if status == "available":
            summary["available"] += 1
        else:
            summary["missing"] += 1
            if importance == "required":
                summary["required_missing"] += 1
            elif importance == "recommended":
                summary["recommended_missing"] += 1
            elif importance == "optional":
                summary["optional_missing"] += 1
    return summary


def build_next_actions(items: list[dict[str, object]]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for item in items:
        if item["status"] == "available":
            continue
        actions.append(
            {
                "id": str(item["id"]),
                "name": str(item["name"]),
                "importance": str(item["importance"]),
                "prompt": f"Ask user permission before installing, downloading from GitHub, or connecting Codex support for {item['name']}.",
                "suggested_action": str(item["install_hint"]),
            }
        )
    return actions


def normalize(value: str) -> str:
    return value.strip().casefold().replace("_", "-")
