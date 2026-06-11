from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from .quality import QualityResult, quality_exit_code, run_quality
from .site_generator import SiteProjectCreateResult, create_site_project


@dataclass(frozen=True)
class SiteSelfTestResult:
    status: str
    target: str
    copied_files: int
    quality_results: list[QualityResult]

    def to_json(self) -> dict[str, object]:
        return {
            "status": self.status,
            "target": self.target,
            "copied_files": self.copied_files,
            "quality_results": [result.to_json() for result in self.quality_results],
        }


def run_site_init_self_test(source_root: Path, target: Path) -> SiteSelfTestResult:
    quality_results = run_quality(target, skip_frontend=True)
    status = "passed" if quality_exit_code(quality_results) == 0 else "failed"
    return SiteSelfTestResult(
        status=status,
        target=str(target),
        copied_files=count_project_files(target),
        quality_results=quality_results,
    )


def run_generated_site_self_test(source_root: Path) -> SiteSelfTestResult:
    temp_parent = source_root / ".llm-wiki"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="site-self-test-", dir=temp_parent) as tmp:
        target = Path(tmp) / "generated-site"
        result: SiteProjectCreateResult = create_site_project(source_root, target)
        quality_results = run_quality(target, skip_frontend=True)
        status = "passed" if quality_exit_code(quality_results) == 0 else "failed"
        return SiteSelfTestResult(
            status=status,
            target=str(result.target),
            copied_files=result.copied_files,
            quality_results=quality_results,
        )


def count_project_files(root: Path) -> int:
    return sum(1 for path in root.rglob("*") if path.is_file())
