"""Basic generated-project runner for the Slugger MVP path."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import json
import subprocess
import sys
import tomllib

from mvp.integrations.codex import package_name_for_project
from mvp.models import CheckResult, MvpProjectRequest
from mvp.workspace import MvpWorkspace, WorkspaceManager

_OUTPUT_LIMIT = 12000
_BUILD_TOOL_DISTRIBUTIONS = ("pip", "setuptools", "wheel")
_VERIFIER_DISTRIBUTIONS = _BUILD_TOOL_DISTRIBUTIONS + ("pytest",)
_CONSTRAINTS_FILE = Path(__file__).resolve().parent.parent / "constraints-ci.txt"
_DEFAULT_WHEELHOUSE = Path("/opt/slugger-wheelhouse")


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
        self,
        workspace_manager: WorkspaceManager,
        *,
        timeout_seconds: int = 120,
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
                [
                    sys.executable,
                    "-m",
                    "venv",
                    str(workspace_path / ".venv"),
                ],
                workspace_path,
            ),
        ]
        python = (
            workspace_path
            / ".venv"
            / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        )
        if checks[-1].passed:
            checks.append(self._provision_build_tools(python, workspace_path))
        else:
            checks.append(
                CheckResult(
                    "provision_build_tools",
                    False,
                    "Skipped because virtual environment creation failed",
                )
            )
        if checks[-1].passed:
            checks.append(
                self._run_phase(
                    "install_verifier_dependencies",
                    _pinned_install_command(python, ("pytest",)),
                    workspace_path,
                )
            )
        else:
            checks.append(
                CheckResult(
                    "install_verifier_dependencies",
                    False,
                    "Skipped because Python build tool provisioning failed",
                )
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
                        "--no-deps",
                        "--no-build-isolation",
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
                    "Skipped because verifier dependency installation failed",
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
        package = package_name_for_project(request.project_name)
        if checks[-1].passed:
            checks.append(
                self._run_phase(
                    "cli_smoke",
                    [str(python), "-m", f"{package}.main", "--help"],
                    workspace_path,
                    require_stdout=("usage",),
                )
            )
        else:
            checks.append(
                CheckResult("cli_smoke", False, "Skipped because tests failed")
            )
        if checks[-1].passed and request.project_name == "hello-codex":
            checks.append(
                self._run_phase(
                    "functional_greet_joseph",
                    [str(python), "-m", f"{package}.main", "greet", "Joseph"],
                    workspace_path,
                    exact_stdout="Hello, Joseph!\n",
                )
            )
        elif request.project_name == "hello-codex":
            checks.append(
                CheckResult(
                    "functional_greet_joseph", False, "Skipped because smoke failed"
                )
            )
        return BasicRunnerResult(tuple(checks))

    def _provision_build_tools(self, python: Path, workspace_path: Path) -> CheckResult:
        expected = _expected_distribution_versions(_BUILD_TOOL_DISTRIBUTIONS)
        command = _pinned_install_command(python, _BUILD_TOOL_DISTRIBUTIONS)
        result = self._run_phase("provision_build_tools", command, workspace_path)
        details = _build_tool_details(expected, result.details)
        if result.passed:
            return self._verify_build_tools(python, workspace_path, details)
        details["diagnostic"] = (
            "Required Python build tools are unavailable. Ensure the restricted "
            "verifier image contains /opt/slugger-wheelhouse with exact versions "
            "pinned by constraints-ci.txt."
        )
        return CheckResult(
            "provision_build_tools",
            False,
            "Required Python build tools are unavailable in verifier environment",
            details,
        )

    def _verify_build_tools(
        self, python: Path, workspace_path: Path, details: dict[str, object]
    ) -> CheckResult:
        verify = self._run_phase(
            "provision_build_tools",
            [
                str(python),
                "-c",
                (
                    "import importlib.metadata as m, json; "
                    "names = ('pip', 'setuptools', 'wheel'); "
                    "print(json.dumps({n: m.version(n) for n in names}, sort_keys=True))"
                ),
            ],
            workspace_path,
        )
        merged = dict(details)
        merged["verification"] = verify.details
        installed: dict[str, str] = {}
        if verify.passed:
            try:
                installed = json.loads(str(verify.details.get("stdout", "{}")))
            except json.JSONDecodeError:
                verify = CheckResult(
                    verify.name, False, "Invalid metadata JSON", verify.details
                )
        merged["installed_versions"] = installed
        raw_expected = merged.get("expected_versions", {})
        expected = raw_expected if isinstance(raw_expected, dict) else {}
        missing = [name for name in expected if name not in installed]
        mismatched = {
            name: {"expected": version, "installed": installed.get(name)}
            for name, version in expected.items()
            if installed.get(name) != version
        }
        merged["missing_distributions"] = missing
        merged["version_mismatches"] = mismatched
        if not verify.passed or missing or mismatched:
            merged["diagnostic"] = (
                "Verifier venv build-tool metadata did not match pinned versions."
            )
            return CheckResult(
                "provision_build_tools",
                False,
                "Required Python build tools are unavailable in verifier environment",
                merged,
            )
        return CheckResult(
            "provision_build_tools",
            True,
            "Python build tools match pinned verifier metadata",
            merged,
        )

    def _run_phase(
        self,
        name: str,
        command: list[str],
        workspace_path: Path,
        *,
        require_stdout: tuple[str, ...] = (),
        exact_stdout: str | None = None,
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
        if exact_stdout is not None and completed.stdout != exact_stdout:
            details["expected_stdout"] = exact_stdout
            return CheckResult(
                name,
                False,
                "Command succeeded but stdout did not exactly match expected output",
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
    env.setdefault("PIP_RETRIES", "0")
    env.setdefault("PIP_TIMEOUT", "5")
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


def _expected_distribution_versions(names: tuple[str, ...]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for line in _CONSTRAINTS_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "==" not in stripped:
            continue
        name, version = stripped.split("==", 1)
        if name in names:
            versions[name] = version
    missing = [name for name in names if name not in versions]
    if missing:
        raise RuntimeError(f"Missing exact verifier constraints: {', '.join(missing)}")
    return versions


def _pinned_install_command(python: Path, names: tuple[str, ...]) -> list[str]:
    versions = _expected_distribution_versions(names)
    command = [str(python), "-m", "pip", "install", "--upgrade"]
    wheelhouse = Path(os.environ.get("SLUGGER_WHEELHOUSE", str(_DEFAULT_WHEELHOUSE)))
    if wheelhouse.is_dir():
        command.extend(["--no-index", "--find-links", str(wheelhouse)])
    command.extend(["--constraint", str(_CONSTRAINTS_FILE)])
    command.extend(f"{name}=={versions[name]}" for name in names)
    return command


def _build_tool_details(
    expected: dict[str, str], provisioning_details: dict[str, object]
) -> dict[str, object]:
    return {
        "expected_versions": expected,
        "installed_versions": {},
        "missing_distributions": [],
        "failed_provisioning_command": provisioning_details.get("command"),
        "returncode": provisioning_details.get("returncode"),
        "stdout": provisioning_details.get("stdout", ""),
        "stderr": provisioning_details.get("stderr", ""),
        "provisioning": provisioning_details,
    }
