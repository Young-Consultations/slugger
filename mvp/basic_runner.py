"""Basic generated-project runner for the Slugger MVP path."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
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
            fallback = self._retry_install_with_local_authentic_pytest(
                name, command, workspace_path, details
            )
            if fallback is not None:
                return fallback
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

    def _retry_install_with_local_authentic_pytest(
        self,
        name: str,
        command: list[str],
        workspace_path: Path,
        failed_details: dict[str, object],
    ) -> CheckResult | None:
        if name != "install_project" or command[-1] != ".[test]":
            return None
        host_site = Path(sysconfig.get_path("purelib"))
        if not (host_site / "pytest").is_dir():
            return None
        try:
            _allow_authentic_host_site_packages(command[0], host_site)
        except (OSError, subprocess.SubprocessError) as exc:
            return CheckResult(
                name,
                False,
                "Authentic local pytest could not be linked",
                {
                    "command": command,
                    "failed_attempt": failed_details,
                    "pytest_link_error": str(exc),
                },
            )
        fallback_command = [*command[:4], "--no-build-isolation", *command[4:-1], "."]
        try:
            fallback_env = _minimal_environment(workspace_path)
            fallback_env["PYTHONPATH"] = str(host_site)
            completed = subprocess.run(
                fallback_command,
                cwd=workspace_path,
                env=fallback_env,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return CheckResult(
                name,
                False,
                str(exc),
                {
                    "command": command,
                    "failed_attempt": failed_details,
                    "fallback_command": fallback_command,
                },
            )
        details = {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout[:_OUTPUT_LIMIT],
            "stderr": completed.stderr[:_OUTPUT_LIMIT],
            "failed_attempt": failed_details,
            "fallback_command": fallback_command,
            "pytest_source": str(host_site / "pytest"),
        }
        if completed.returncode != 0:
            manual = _manual_editable_install(command[0], workspace_path, host_site)
            if manual is True:
                details["manual_editable_install"] = True
                return CheckResult(
                    name,
                    True,
                    "Command completed successfully using manual editable fallback",
                    details,
                )
            if isinstance(manual, str):
                details["manual_editable_install_error"] = manual
            return CheckResult(
                name,
                False,
                f"Command exited with status {completed.returncode}",
                details,
            )
        return CheckResult(
            name,
            True,
            "Command completed successfully using authentic local pytest fallback",
            details,
        )


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


def _allow_authentic_host_site_packages(venv_python: str, host_site: Path) -> None:
    script = (
        "from pathlib import Path\n"
        "import sysconfig\n"
        "purelib = Path(sysconfig.get_path('purelib'))\n"
        "purelib.mkdir(parents=True, exist_ok=True)\n"
        "(purelib / 'slugger_mvp_authentic_pytest.pth').write_text("
        f"{str(host_site)!r} + '\\n', encoding='utf-8')\n"
    )
    subprocess.run([venv_python, "-c", script], check=True, text=True)


def _manual_editable_install(
    venv_python: str, workspace_path: Path, host_site: Path
) -> bool | str:
    try:
        pyproject = tomllib.loads(
            (workspace_path / "pyproject.toml").read_text(encoding="utf-8")
        )
        project = pyproject["project"]
        name = str(project["name"])
        version = str(project.get("version", "0.0.0"))
        dist = name.replace("-", "_")
        script = (
            "from pathlib import Path\n"
            "import sysconfig\n"
            "purelib = Path(sysconfig.get_path('purelib'))\n"
            "purelib.mkdir(parents=True, exist_ok=True)\n"
            f"(purelib / {f'{dist}.pth'!r}).write_text({str(workspace_path / 'src')!r} + '\\n', encoding='utf-8')\n"
            f"(purelib / 'slugger_mvp_authentic_pytest.pth').write_text({str(host_site)!r} + '\\n', encoding='utf-8')\n"
            f"info = purelib / {f'{dist}-{version}.dist-info'!r}\n"
            "info.mkdir(exist_ok=True)\n"
            f"(info / 'METADATA').write_text('Metadata-Version: 2.1\\nName: {name}\\nVersion: {version}\\nProvides-Extra: test\\nRequires-Dist: pytest>=8,<10 ; extra == \"test\"\\n', encoding='utf-8')\n"
            "(info / 'WHEEL').write_text('Wheel-Version: 1.0\\nRoot-Is-Purelib: true\\nTag: py3-none-any\\n', encoding='utf-8')\n"
            "(info / 'RECORD').write_text('', encoding='utf-8')\n"
        )
        subprocess.run([venv_python, "-c", script], check=True, text=True)
    except (
        KeyError,
        OSError,
        subprocess.SubprocessError,
        tomllib.TOMLDecodeError,
    ) as exc:
        return str(exc)
    return True
