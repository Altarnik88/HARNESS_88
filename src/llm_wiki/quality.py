from __future__ import annotations

import subprocess
import shutil
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QualityStep:
    name: str
    command: list[str]
    cwd: Path

    def command_text(self) -> str:
        return " ".join(self.command)


@dataclass(frozen=True)
class QualityResult:
    name: str
    command: list[str]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float

    def to_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "command": self.command,
            "cwd": self.cwd,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_seconds": round(self.duration_seconds, 3),
        }


StepRunner = Callable[[QualityStep], tuple[int, str, str]]


def build_quality_steps(root: Path, full: bool = False) -> list[QualityStep]:
    steps = [
        QualityStep("python-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"], root),
        QualityStep("wiki-rebuild", [sys.executable, "tools/llm_wiki.py", "rebuild"], root),
        QualityStep("wiki-lint-strict", [sys.executable, "tools/llm_wiki.py", "lint", "--strict"], root),
    ]
    frontend = root / "frontend"
    if (frontend / "package.json").exists():
        steps.append(QualityStep("frontend-lint", ["npm", "run", "lint"], frontend))
        if full:
            steps.append(QualityStep("frontend-build", ["npm", "run", "build"], frontend))
    return steps


def run_quality(root: Path, full: bool = False, runner: StepRunner | None = None) -> list[QualityResult]:
    execute = runner or run_subprocess
    results: list[QualityResult] = []
    for step in build_quality_steps(root, full):
        started = time.perf_counter()
        exit_code, stdout, stderr = execute(step)
        duration = time.perf_counter() - started
        results.append(
            QualityResult(
                name=step.name,
                command=step.command,
                cwd=str(step.cwd),
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=duration,
            )
        )
    return results


def run_subprocess(step: QualityStep) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            resolve_command(step.command),
            cwd=step.cwd,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except OSError as exc:
        return 1, "", str(exc)
    return completed.returncode, completed.stdout, completed.stderr


def resolve_command(command: list[str]) -> list[str]:
    if not command:
        return command
    resolved = shutil.which(command[0])
    if resolved:
        return [resolved, *command[1:]]
    return command


def quality_exit_code(results: list[QualityResult]) -> int:
    return 0 if all(result.exit_code == 0 for result in results) else 1
