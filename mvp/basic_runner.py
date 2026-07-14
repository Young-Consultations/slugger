"""Basic generated-project runner for the Slugger MVP path."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import tomllib

from mvp.integrations.codex import package_name_for_project
from mvp.models import CheckResult, MvpProjectRequest
from mvp.workspace import MvpWorkspace, WorkspaceManager

_OUTPUT_LIMIT = 12000


@dataclass(frozen=True)
class BasicRunnerResult:
    """Structured results for install, pytest, and CLI smoke phases."""

    checks: tuple[CheckResult, ...]

    @property
    def passed(self) -> bool:
        return bool(self.checks) and all(check.passed for check in self.checks)


class BasicRunner:
    """Install and exercise a generated Python CLI project in its own virtualenv."""

    def __init__(
        self, workspace_manager: WorkspaceManager, *, timeout_seconds: int = 120
    ) -> None:
        self.workspace_manager = workspace_manager
        self.timeout_seconds = timeout_seconds

    def run(
        self, request: MvpProjectRequest, workspace: MvpWorkspace | Path
    ) -> BasicRunnerResult:
        workspace_path = self.workspace_manager._workspace_path(workspace)
        checks = [
            self._run_phase(
                "create_environment",
                [sys.executable, "-m", "venv", str(workspace_path / ".venv")],
                workspace_path,
            ),
        ]
        python = (
            workspace_path
            / ".venv"
            / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        )
        if checks[-1].passed:
            checks.append(
                self._run_phase(
                    "install_project",
                    [
                        str(python),
                        "-m",
                        "pip",
                        "install",
                        "-e",
                        _editable_install_target(workspace_path),
                    ],
                    workspace_path,
                )
            )
        else:
            checks.append(
                CheckResult(
                    "install_project",
                    False,
                    "Skipped because virtual environment creation failed",
                )
            )
        if checks[-1].passed:
            checks.append(
                self._run_phase(
                    "verify_pytest_available",
                    [str(python), "-c", "import pytest; print(pytest.__version__)"],
                    workspace_path,
                )
            )
        else:
            checks.append(
                CheckResult(
                    "verify_pytest_available",
                    False,
                    "Skipped because installation failed",
                )
            )
        if checks[-1].passed:
            checks.append(
                self._run_phase(
                    "run_tests", [str(python), "-m", "pytest", "-q"], workspace_path
                )
            )
        else:
            checks.append(
                CheckResult(
                    "run_tests", False, "Skipped because pytest is not installed"
                )
            )
        if checks[-1].passed:
            package = package_name_for_project(request.project_name)
            checks.append(
                self._run_phase(
                    "cli_smoke",
                    [str(python), "-m", f"{package}.main", "--help"],
                    workspace_path,
                    require_stdout=("usage", request.project_name),
                )
            )
        else:
            checks.append(
                CheckResult("cli_smoke", False, "Skipped because tests failed")
            )
        return BasicRunnerResult(tuple(checks))

    def _run_phase(
        self,
        name: str,
        command: list[str],
        workspace_path: Path,
        *,
        require_stdout: tuple[str, ...] = (),
    ) -> CheckResult:
        try:
            completed = subprocess.run(
                command,
                cwd=workspace_path,
                env=_minimal_environment(workspace_path),
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return CheckResult(name, False, str(exc), {"command": command})
        details = {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout[:_OUTPUT_LIMIT],
            "stderr": completed.stderr[:_OUTPUT_LIMIT],
        }
        if completed.returncode != 0:
            return CheckResult(
                name,
                False,
                f"Command exited with status {completed.returncode}",
                details,
            )
        missing_stdout = [
            text for text in require_stdout if text not in completed.stdout
        ]
        if missing_stdout:
            details["missing_stdout"] = missing_stdout
            return CheckResult(
                name,
                False,
                f"Command succeeded but stdout missed expected text: {', '.join(missing_stdout)}",
                details,
            )
        return CheckResult(name, True, "Command completed successfully", details)


def _minimal_environment(workspace_path: Path | None = None) -> dict[str, str]:
    allowed = {
        "HOME",
        "PATH",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "SSL_CERT_FILE",
        "REQUESTS_CA_BUNDLE",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
        "PIP_INDEX_URL",
        "PIP_EXTRA_INDEX_URL",
        "PIP_TRUSTED_HOST",
        "PIP_CERT",
    }
    env = {key: os.environ[key] for key in allowed if key in os.environ}
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _editable_install_target(workspace_path: Path) -> str:
    if _declares_pytest_extra(workspace_path):
        return ".[test]"
    return "."


def _declares_pytest_extra(workspace_path: Path) -> bool:
    pyproject = workspace_path / "pyproject.toml"
    if not pyproject.is_file():
        return False
    try:
        parsed = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return False
    test_extra = (
        parsed.get("project", {}).get("optional-dependencies", {}).get("test", [])
    )
    return bool(test_extra)
