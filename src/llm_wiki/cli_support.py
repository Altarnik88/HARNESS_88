from __future__ import annotations


def summary_count(summary: dict[str, object], key: str) -> object:
    bucket = summary[key]
    assert isinstance(bucket, dict)
    return bucket["count"]


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def site_lock_state(readiness: dict[str, object]) -> str:
    return "unlocked" if readiness.get("site_implementation_ready") else "locked"


def print_blocker_preview(blockers: object, limit: int = 8) -> None:
    if not isinstance(blockers, list) or not blockers:
        return
    print("Blockers:")
    for blocker in blockers[:limit]:
        assert isinstance(blocker, dict)
        print(f"- {blocker['path']}: {blocker['message']}")
    if len(blockers) > limit:
        print(f"... {len(blockers) - limit} more blocker(s); use --json for full detail.")
