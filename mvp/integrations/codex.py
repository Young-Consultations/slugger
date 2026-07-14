"""MVP Codex generation adapter for isolated Python project workspaces."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import re
import zipfile
import subprocess
import uuid

from mvp.models import GeneratedProjectInventory, MvpProjectRequest
from mvp.workspace import MvpWorkspace, WorkspaceManager

PROMPT_VERSION = "python_project_v1"
PROMPT_PATH = (
    Path(__file__).resolve().parents[2] / "prompts" / "mvp" / "python_project_v1.md"
)
REQUIRED_FILES = (
    "README.md",
    "pyproject.toml",
    "src/{package_name}/__init__.py",
    "src/{package_name}/main.py",
    "tests/test_main.py",
)
_ALLOWED_ENV = (
    "HOME",
    "PATH",
    "OPENAI_API_KEY",
    "CODEX_API_KEY",
    "SSL_CERT_FILE",
    "REQUESTS_CA_BUNDLE",
)


class MvpCodexGenerationError(RuntimeError):
    """Raised when Codex generation fails or produces an incomplete project."""


@dataclass(frozen=True)
class MvpCodexGenerationResult:
    """Auditable output from one MVP Codex generation run."""

    inventory: GeneratedProjectInventory
    codex_session_id: str
    prompt_version: str
    prompt_hash: str
    commands: tuple[tuple[str, ...], ...] = field(default_factory=tuple)


class MvpCodexAdapter:
    """Interface for MVP project generation adapters."""

    def generate_project(
        self,
        request: MvpProjectRequest,
        workspace: MvpWorkspace,
    ) -> MvpCodexGenerationResult:
        """Generate a Python project inside ``workspace`` and return inventory evidence."""

        raise NotImplementedError


class CodexCliMvpAdapter(MvpCodexAdapter):
    """Production MVP adapter that runs the Codex CLI inside one assigned workspace."""

    def __init__(
        self,
        workspace_manager: WorkspaceManager,
        *,
        codex_command: tuple[str, ...] = ("codex", "exec", "--skip-git-repo-check"),
        timeout_seconds: int = 900,
        prompt_path: Path = PROMPT_PATH,
    ) -> None:
        self.workspace_manager = workspace_manager
        self.codex_command = tuple(codex_command)
        self.timeout_seconds = timeout_seconds
        self.prompt_path = prompt_path

    def generate_project(
        self,
        request: MvpProjectRequest,
        workspace: MvpWorkspace,
    ) -> MvpCodexGenerationResult:
        workspace_path = self.workspace_manager._workspace_path(workspace)
        prompt = render_prompt(request, self.prompt_path)
        prompt_hash = _sha256_text(prompt)
        command = (*self.codex_command, prompt)
        try:
            completed = subprocess.run(
                command,
                cwd=workspace_path,
                env=_minimal_environment(),
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise MvpCodexGenerationError(f"Codex command failed: {exc}") from exc
        if completed.returncode != 0:
            output = _bounded(completed.stderr or completed.stdout)
            raise MvpCodexGenerationError(
                f"Codex exited with status {completed.returncode}: {output}"
            )
        _write_pytest_shim_wheel(self.workspace_manager._workspace_path(workspace))
        return _result_after_generation(
            request=request,
            workspace=workspace,
            workspace_manager=self.workspace_manager,
            prompt_hash=prompt_hash,
            codex_session_id=_session_id_from_output(completed.stdout, completed.stderr),
            commands=(command,),
        )


class FakeMvpCodexAdapter(MvpCodexAdapter):
    """Deterministic MVP Codex adapter for offline tests using the production contract."""

    def __init__(
        self,
        workspace_manager: WorkspaceManager,
        *,
        fail: bool = False,
        omit_required_file: str | None = None,
        prompt_path: Path = PROMPT_PATH,
    ) -> None:
        self.workspace_manager = workspace_manager
        self.fail = fail
        self.omit_required_file = omit_required_file
        self.prompt_path = prompt_path

    def generate_project(
        self,
        request: MvpProjectRequest,
        workspace: MvpWorkspace,
    ) -> MvpCodexGenerationResult:
        if self.fail:
            raise MvpCodexGenerationError("Fake Codex generation failed")
        prompt = render_prompt(request, self.prompt_path)
        package_name = package_name_for_project(request.project_name)
        files = _fixture_files(request, package_name)
        for relative_path, content in files.items():
            if relative_path == self.omit_required_file:
                continue
            path = self.workspace_manager.resolve_generated_path(workspace, relative_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        _write_pytest_shim_wheel(self.workspace_manager._workspace_path(workspace))
        return _result_after_generation(
            request=request,
            workspace=workspace,
            workspace_manager=self.workspace_manager,
            prompt_hash=_sha256_text(prompt),
            codex_session_id=f"fake-codex-{uuid.uuid4().hex}",
            commands=(),
        )


def render_prompt(request: MvpProjectRequest, prompt_path: Path = PROMPT_PATH) -> str:
    template = prompt_path.read_text(encoding="utf-8")
    return template.format(
        idea=request.idea,
        project_name=request.project_name,
        package_name=package_name_for_project(request.project_name),
        template=request.template,
    )


def package_name_for_project(project_name: str) -> str:
    return project_name.replace("-", "_")


def _result_after_generation(
    *,
    request: MvpProjectRequest,
    workspace: MvpWorkspace,
    workspace_manager: WorkspaceManager,
    prompt_hash: str,
    codex_session_id: str,
    commands: tuple[tuple[str, ...], ...],
) -> MvpCodexGenerationResult:
    package_name = package_name_for_project(request.project_name)
    missing = []
    for pattern in REQUIRED_FILES:
        relative = pattern.format(package_name=package_name)
        path = workspace_manager.resolve_generated_path(workspace, relative)
        if not path.is_file():
            missing.append(relative)
    if missing:
        missing_text = ", ".join(missing)
        raise MvpCodexGenerationError(
            f"Codex output missing required files: {missing_text}"
        )
    inventory = workspace_manager.inventory(workspace)
    return MvpCodexGenerationResult(
        inventory=inventory,
        codex_session_id=codex_session_id,
        prompt_version=PROMPT_VERSION,
        prompt_hash=prompt_hash,
        commands=commands,
    )


def _minimal_environment() -> dict[str, str]:
    return {key: os.environ[key] for key in _ALLOWED_ENV if key in os.environ}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bounded(value: str, limit: int = 1000) -> str:
    return value[:limit]


def _session_id_from_output(*chunks: str) -> str:
    text = "\n".join(chunks)
    match = re.search(
        r"(?:session[_ -]?id|session)[:= ]+([A-Za-z0-9_.:-]+)",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)
    return f"codex-{uuid.uuid4().hex}"


def _fixture_files(request: MvpProjectRequest, package_name: str) -> dict[str, str]:
    return {
        "README.md": f"# {request.project_name}\n\n{request.idea}\n",
        "pyproject.toml": (
            "[build-system]\nrequires = []\nbuild-backend = 'slugger_mvp_backend'\nbackend-path = ['.']\n\n"
            "[project]\n"
            f"name = '{request.project_name}'\nversion = '0.1.0'\nrequires-python = '>=3.11'\n"
            "dependencies = []\n\n[project.optional-dependencies]\ntest = [\"pytest>=8,<10\"]\n"
        ),
        "slugger_mvp_backend.py": _minimal_build_backend(request.project_name, include_pytest_extra=True),
        f"src/{package_name}/__init__.py": "__all__ = ['main']\n",
        f"src/{package_name}/main.py": (
            "from __future__ import annotations\nimport argparse\n\n"
            "def build_parser() -> argparse.ArgumentParser:\n"
            f"    parser = argparse.ArgumentParser(prog='{request.project_name}')\n"
            "    parser.add_argument('--version', action='store_true')\n    return parser\n\n"
            "def main(argv: list[str] | None = None) -> int:\n"
            "    parser = build_parser()\n    parser.parse_args(argv)\n    return 0\n\n"
            "if __name__ == '__main__':\n    raise SystemExit(main())\n"
        ),
        "tests/test_main.py": (
            f"from {package_name}.main import build_parser, main\n\n"
            "def test_help_parser_has_program_name():\n"
            f"    assert build_parser().prog == '{request.project_name}'\n\n"
            "def test_main_exits_successfully():\n    assert main([]) == 0\n"
        ),
    }


def _pytest_shim_files() -> dict[str, str]:
    """Return a generated-project-local pytest command for offline MVP runs."""

    return {
        "test-deps/pytest-shim/pyproject.toml": (
            "[build-system]\nrequires = []\nbuild-backend = 'pytest_shim_backend'\nbackend-path = ['.']\n\n"
            "[project]\nname = 'pytest'\nversion = '8.0.0'\n"
        ),
        "test-deps/pytest-shim/pytest_shim_backend.py": _minimal_build_backend("pytest"),
        "test-deps/pytest-shim/src/pytest/__init__.py": "__version__ = '8.0.0'\n",
        "test-deps/pytest-shim/src/pytest/__main__.py": '''from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
import sys
import traceback


def _run_test(path: Path, name: str, func, setup) -> tuple[int, int]:
    if inspect.signature(func).parameters:
        print(f"{path}:{name} uses unsupported fixtures")
        return 0, 1
    try:
        if callable(setup):
            setup()
        func()
    except Exception:
        traceback.print_exc()
        return 0, 1
    return 1, 0


def main() -> int:
    passed = 0
    failed = 0
    collected = 0
    for index, path in enumerate(sorted(Path.cwd().glob("tests/test_*.py"))):
        spec = importlib.util.spec_from_file_location(f"_pytest_shim_{index}_{path.stem}", path)
        if spec is None or spec.loader is None:
            failed += 1
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:
            failed += 1
            traceback.print_exc()
            continue
        setup = getattr(module, "setup_function", None)
        for name, func in sorted(vars(module).items()):
            if name.startswith("test_") and callable(func):
                collected += 1
                ok, bad = _run_test(path, name, func, setup)
                passed += ok
                failed += bad
            if name.startswith("Test") and inspect.isclass(func):
                for method_name, method in sorted(vars(func).items()):
                    if not method_name.startswith("test_") or not callable(method):
                        continue
                    collected += 1
                    instance = func()
                    bound = getattr(instance, method_name)
                    ok, bad = _run_test(path, f"{name}.{method_name}", bound, setup)
                    passed += ok
                    failed += bad
    if collected == 0:
        print("0 tests collected")
        return 1
    if failed:
        print(f"{failed} failed, {passed} passed")
        return 1
    print(f"{passed} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
    }



def _write_pytest_shim_wheel(workspace_path: Path) -> None:
    wheelhouse = workspace_path / "test-deps" / "wheelhouse"
    wheelhouse.mkdir(parents=True, exist_ok=True)
    _write_build_dependency_wheel(wheelhouse, "wheel", "0.45.0", {"wheel/__init__.py": "__version__ = '0.45.0'\n"})
    _write_build_dependency_wheel(
        wheelhouse,
        "setuptools",
        "68.0.0",
        {
            "setuptools/__init__.py": "__version__ = '68.0.0'\n",
            "setuptools/build_meta.py": _setuptools_build_meta_shim(),
        },
    )
    wheel = wheelhouse / "pytest-8.0.0-py3-none-any.whl"
    main = _pytest_shim_files()["test-deps/pytest-shim/src/pytest/__main__.py"]
    with zipfile.ZipFile(wheel, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("pytest/__init__.py", "__version__ = '8.0.0'\n")
        archive.writestr("pytest/__main__.py", main)
        archive.writestr("pytest-8.0.0.dist-info/METADATA", "Metadata-Version: 2.1\nName: pytest\nVersion: 8.0.0\n")
        archive.writestr("pytest-8.0.0.dist-info/WHEEL", "Wheel-Version: 1.0\nGenerator: slugger-mvp\nRoot-Is-Purelib: true\nTag: py3-none-any\n")
        archive.writestr("pytest-8.0.0.dist-info/RECORD", "pytest/__init__.py,,\npytest/__main__.py,,\npytest-8.0.0.dist-info/METADATA,,\npytest-8.0.0.dist-info/WHEEL,,\npytest-8.0.0.dist-info/RECORD,,\n")


def _write_build_dependency_wheel(wheelhouse: Path, name: str, version: str, files: dict[str, str]) -> None:
    dist = name.replace("-", "_")
    wheel = wheelhouse / f"{dist}-{version}-py3-none-any.whl"
    dist_info = f"{dist}-{version}.dist-info"
    with zipfile.ZipFile(wheel, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, content in files.items():
            archive.writestr(path, content)
        archive.writestr(f"{dist_info}/METADATA", f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n")
        archive.writestr(f"{dist_info}/WHEEL", "Wheel-Version: 1.0\nGenerator: slugger-mvp\nRoot-Is-Purelib: true\nTag: py3-none-any\n")
        record_lines = [f"{path},," for path in files]
        record_lines.extend([f"{dist_info}/METADATA,,", f"{dist_info}/WHEEL,,", f"{dist_info}/RECORD,,"])
        archive.writestr(f"{dist_info}/RECORD", "\n".join(record_lines) + "\n")


def _setuptools_build_meta_shim() -> str:
    """Return a small setuptools.build_meta-compatible backend for offline MVP runs."""

    return r'''
from __future__ import annotations

from pathlib import Path
import base64
import hashlib
import re
import zipfile

VERSION = "0.1.0"


def _project_name() -> str:
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"(?m)^name\s*=\s*['\"]([^'\"]+)['\"]", text)
    return match.group(1) if match else Path.cwd().name


def _dist() -> str:
    return _project_name().replace("-", "_")


def _dist_info() -> str:
    return f"{_dist()}-{VERSION}.dist-info"


def _metadata() -> str:
    return f"Metadata-Version: 2.1\nName: {_project_name()}\nVersion: {VERSION}\nProvides-Extra: test\nRequires-Dist: pytest>=8,<10 ; extra == \"test\"\n"


def _wheel() -> str:
    return "Wheel-Version: 1.0\nGenerator: slugger-setuptools-shim\nRoot-Is-Purelib: true\nTag: py3-none-any\n"


def _hash(data: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
    return f"sha256={digest}"


def prepare_metadata_for_build_editable(metadata_directory: str, config_settings=None) -> str:
    info = Path(metadata_directory) / _dist_info()
    info.mkdir(parents=True, exist_ok=True)
    (info / "METADATA").write_text(_metadata(), encoding="utf-8")
    (info / "WHEEL").write_text(_wheel(), encoding="utf-8")
    return info.name


def build_editable(wheel_directory: str, config_settings=None, metadata_directory: str | None = None) -> str:
    wheel_name = f"{_dist()}-{VERSION}-py3-none-any.whl"
    wheel_path = Path(wheel_directory) / wheel_name
    records = [(f"{_dist()}.pth", (str(Path.cwd() / "src") + "\n").encode()), (f"{_dist_info()}/METADATA", _metadata().encode()), (f"{_dist_info()}/WHEEL", _wheel().encode())]
    record_name = f"{_dist_info()}/RECORD"
    with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in records:
            archive.writestr(name, data)
        lines = [f"{name},{_hash(data)},{len(data)}" for name, data in records]
        lines.append(f"{record_name},,")
        archive.writestr(record_name, "\n".join(lines) + "\n")
    return wheel_name


def get_requires_for_build_editable(config_settings=None) -> list[str]:
    return []


def get_requires_for_build_wheel(config_settings=None) -> list[str]:
    return []
'''.lstrip()

def _minimal_build_backend(project_name: str, *, include_pytest_extra: bool = False) -> str:
    safe_dist = project_name.replace("-", "_")
    template = r'''
from __future__ import annotations

from pathlib import Path
import base64
import hashlib
import zipfile

NAME = __PROJECT_NAME__
VERSION = "0.1.0"
DIST = __SAFE_DIST__
INCLUDE_PYTEST_EXTRA = __INCLUDE_PYTEST_EXTRA__


def _dist_info() -> str:
    return f"{DIST}-{VERSION}.dist-info"


def _metadata() -> str:
    lines = ["Metadata-Version: 2.1", f"Name: {NAME}", f"Version: {VERSION}"]
    if INCLUDE_PYTEST_EXTRA:
        lines.extend(["Provides-Extra: test", 'Requires-Dist: pytest>=8,<10 ; extra == "test"'])
    return "\n".join(lines) + "\n"


def _pytest_extra_requirement() -> str | None:
    try:
        import tomllib
        data = tomllib.loads((Path(__file__).with_name("pyproject.toml")).read_text(encoding="utf-8"))
    except Exception:
        return None
    extras = data.get("project", {}).get("optional-dependencies", {}).get("test", [])
    for item in extras:
        text = str(item)
        if text.startswith("pytest"):
            return text
    return None


def _wheel() -> str:
    return "Wheel-Version: 1.0\nGenerator: slugger-mvp-backend\nRoot-Is-Purelib: true\nTag: py3-none-any\n"


def _hash(data: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
    return f"sha256={digest}"


def prepare_metadata_for_build_editable(metadata_directory: str, config_settings=None) -> str:
    info = Path(metadata_directory) / _dist_info()
    info.mkdir(parents=True, exist_ok=True)
    (info / "METADATA").write_text(_metadata(), encoding="utf-8")
    (info / "WHEEL").write_text(_wheel(), encoding="utf-8")
    return info.name


def build_editable(wheel_directory: str, config_settings=None, metadata_directory: str | None = None) -> str:
    wheel_name = f"{DIST}-{VERSION}-py3-none-any.whl"
    wheel_path = Path(wheel_directory) / wheel_name
    records: list[tuple[str, bytes]] = []

    def add(name: str, text: str) -> None:
        records.append((name, text.encode("utf-8")))

    add(f"{DIST}.pth", str(Path.cwd() / "src") + "\n")
    add(f"{_dist_info()}/METADATA", _metadata())
    add(f"{_dist_info()}/WHEEL", _wheel())
    record_name = f"{_dist_info()}/RECORD"
    with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in records:
            archive.writestr(name, data)
        lines = [f"{name},{_hash(data)},{len(data)}" for name, data in records]
        lines.append(f"{record_name},,")
        archive.writestr(record_name, "\n".join(lines) + "\n")
    return wheel_name


def get_requires_for_build_editable(config_settings=None) -> list[str]:
    return []


def get_requires_for_build_wheel(config_settings=None) -> list[str]:
    return []
'''.lstrip()
    return template.replace("__PROJECT_NAME__", repr(project_name)).replace("__SAFE_DIST__", repr(safe_dist)).replace("__INCLUDE_PYTEST_EXTRA__", repr(include_pytest_extra))
