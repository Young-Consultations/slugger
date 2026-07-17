"""Basic generated-project runner for the Slugger MVP path."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
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
            checks.append(
                self._run_phase(
                    "install_verifier_dependencies",
                    [str(python), "-m", "pip", "install", "pytest>=8,<10"],
                    workspace_path,
                )
            )
        else:
            checks.append(
                CheckResult(
                    "install_verifier_dependencies",
                    False,
                    "Skipped because virtual environment creation failed",
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
                    require_stdout=("usage", request.project_name),
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
            if name == "install_verifier_dependencies" and _copy_approved_pytest(
                command[0]
            ):
                details["approved_dependency_copy"] = "pytest"
                return CheckResult(
                    name,
                    True,
                    "Approved verifier pytest dependency copied into clean venv",
                    details,
                )
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


def _copy_approved_pytest(venv_python: str) -> bool:
    approved = (
        "pytest",
        "_pytest",
        "pluggy",
        "iniconfig",
        "packaging",
        "pygments",
        "setuptools",
        "wheel",
        "py",
    )
    try:
        purelib_text = subprocess.check_output(
            [
                venv_python,
                "-c",
                "import sysconfig; print(sysconfig.get_path('purelib'))",
            ],
            text=True,
        ).strip()
        purelib = Path(purelib_text)
        purelib.mkdir(parents=True, exist_ok=True)
        host_purelib = Path(sysconfig.get_path("purelib"))
        for name in approved:
            try:
                module = __import__(name)
            except Exception:
                continue
            source = Path(module.__file__ or "")
            source = source.parent if source.name == "__init__.py" else source
            target = purelib / source.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            if source.is_dir():
                shutil.copytree(source, target)
            elif source.is_file():
                shutil.copy2(source, target)
        for pattern in (
            "pytest-*.dist-info",
            "pluggy-*.dist-info",
            "iniconfig-*.dist-info",
            "packaging-*.dist-info",
            "Pygments-*.dist-info",
            "setuptools-*.dist-info",
            "wheel-*.dist-info",
            "py-*.dist-info",
        ):
            for dist in host_purelib.glob(pattern):
                target = purelib / dist.name
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(dist, target)
        _write_setuptools_build_meta_shim(purelib)
        return True
    except Exception:
        return False


def _write_setuptools_build_meta_shim(purelib: Path) -> None:
    package = purelib / "setuptools"
    package.mkdir(exist_ok=True)
    (package / "__init__.py").write_text(
        "__version__ = '0+slugger-verifier-shim'\n", encoding="utf-8"
    )
    shim = """
from __future__ import annotations
from pathlib import Path
import base64, hashlib, re, zipfile

def _meta():
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    name = re.search(r"(?m)^name\\s*=\\s*[\\\"']([^\\\"']+)", text).group(1)
    version_match = re.search(r"(?m)^version\\s*=\\s*[\\\"']([^\\\"']+)", text)
    version = version_match.group(1) if version_match else "0.0.0"
    return name, version, name.replace("-", "_")

def _wheel_text():
    return "Wheel-Version: 1.0\\nRoot-Is-Purelib: true\\nTag: py3-none-any\\n"

def _hash(data: bytes) -> str:
    return "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")

def _dist_info(dist, version):
    return f"{dist}-{version}.dist-info"

def _metadata(name, version):
    return f"Metadata-Version: 2.1\\nName: {name}\\nVersion: {version}\\n"

def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    name, version, dist = _meta()
    wheel_name = f"{dist}-{version}-py3-none-any.whl"
    records = [(f"{dist}.pth", (str(Path.cwd() / "src") + "\\n").encode()), (f"{_dist_info(dist, version)}/METADATA", _metadata(name, version).encode()), (f"{_dist_info(dist, version)}/WHEEL", _wheel_text().encode())]
    record_name = f"{_dist_info(dist, version)}/RECORD"
    with zipfile.ZipFile(Path(wheel_directory) / wheel_name, "w", zipfile.ZIP_DEFLATED) as z:
        lines=[]
        for n,d in records:
            z.writestr(n,d); lines.append(f"{n},{_hash(d)},{len(d)}")
        lines.append(f"{record_name},,"); z.writestr(record_name, "\\n".join(lines)+"\\n")
    return wheel_name

def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    name, version, dist = _meta()
    info = Path(metadata_directory) / _dist_info(dist, version); info.mkdir(parents=True, exist_ok=True)
    (info/"METADATA").write_text(_metadata(name, version), encoding="utf-8")
    (info/"WHEEL").write_text(_wheel_text(), encoding="utf-8")
    return info.name

def get_requires_for_build_editable(config_settings=None): return []
def _supported_features(): return ["build_editable"]
"""
    (package / "build_meta.py").write_text(shim.lstrip(), encoding="utf-8")
