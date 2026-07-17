"""MVP Codex generation adapter for isolated Python project workspaces."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

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
    "SSL_CERT_FILE",
    "REQUESTS_CA_BUNDLE",
)
_CODEX_EXEC_API_KEY_ENV = "CODEX_API_KEY"
_CODEX_AUTH_HELP = """Codex CLI authentication is not available.
Run:
    codex login
    codex login status
Alternatively, authenticate with an OpenAI Platform API key by piping
OPENAI_API_KEY to:
    codex login --with-api-key
Do not store the API key in this repository.
For non-interactive exec-only automation, set CODEX_API_KEY only on the
Slugger command invocation; Slugger passes it only to codex exec and skips
the login-status preflight for that scoped environment variable."""


class MvpCodexGenerationError(RuntimeError):
    """Raised when Codex generation fails or produces an incomplete project."""


@dataclass(frozen=True)
class MvpCodexGenerationResult:
    """Auditable output from one MVP Codex generation run."""

    inventory: GeneratedProjectInventory
    codex_session_id: str | None
    slugger_correlation_id: str
    prompt_version: str
    prompt_hash: str
    commands: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    external_generation_id: str | None = None
    artifact_manifest_digest: str | None = None


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
        codex_command: tuple[str, ...] = ("codex",),
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
        codex_executable = self.codex_command[0]
        _preflight_codex(
            codex_executable,
            workspace_path,
            exec_api_key=os.environ.get("CODEX_API_KEY"),
        )
        prompt = render_prompt(request, self.prompt_path)
        prompt_hash = _sha256_text(prompt)
        command = _codex_exec_command(self.codex_command)
        try:
            completed = subprocess.run(
                command,
                cwd=workspace_path,
                env=_minimal_environment(include_codex_api_key=True),
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise MvpCodexGenerationError(
                _missing_codex_message(codex_executable)
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise MvpCodexGenerationError(
                f"Codex timed out after {self.timeout_seconds} seconds"
            ) from exc
        except OSError as exc:
            raise MvpCodexGenerationError(f"Codex command failed: {exc}") from exc
        parsed_output = _parse_codex_jsonl(completed.stdout)
        if completed.returncode != 0:
            output = _bounded(_codex_failure_details(parsed_output, completed.stderr))
            raise MvpCodexGenerationError(
                f"Codex exited with status {completed.returncode}: {output}"
            )
        return _result_after_generation(
            request=request,
            workspace=workspace,
            workspace_manager=self.workspace_manager,
            prompt_hash=prompt_hash,
            codex_session_id=parsed_output.session_id
            or _session_id_from_output(completed.stdout, completed.stderr),
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
            path = self.workspace_manager.resolve_generated_path(
                workspace, relative_path
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return _result_after_generation(
            request=request,
            workspace=workspace,
            workspace_manager=self.workspace_manager,
            prompt_hash=_sha256_text(prompt),
            codex_session_id=None,
            commands=(),
        )


class ArtifactMvpCodexAdapter(MvpCodexAdapter):
    """Import a pre-generated protected artifact through the Codex adapter contract."""

    def __init__(
        self,
        workspace_manager: WorkspaceManager,
        artifact_dir: Path,
        manifest_path: Path,
        *,
        prompt_path: Path = PROMPT_PATH,
    ) -> None:
        self.workspace_manager = workspace_manager
        self.artifact_dir = Path(artifact_dir)
        self.manifest_path = Path(manifest_path)
        self.prompt_path = prompt_path

    def generate_project(
        self,
        request: MvpProjectRequest,
        workspace: MvpWorkspace,
    ) -> MvpCodexGenerationResult:
        from mvp.inventory_manifest import (
            ManifestError,
            create_protected_manifest,
            load_manifest,
            verify_protected_manifest,
        )

        workspace_path = self.workspace_manager._workspace_path(workspace)
        try:
            supplied = load_manifest(self.manifest_path)
            verify_protected_manifest(self.artifact_dir, self.manifest_path)
            expected_paths = {entry["path"] for entry in supplied["entries"]}
            protected = create_protected_manifest(self.artifact_dir)
            protected_paths = {entry["path"] for entry in protected["entries"]}
            if protected_paths != expected_paths:
                raise MvpCodexGenerationError("Artifact manifest path mismatch")
            if protected["artifact_digest"] != supplied.get("artifact_digest"):
                raise MvpCodexGenerationError("Artifact manifest digest mismatch")
            for entry in supplied["entries"]:
                rel = entry["path"]
                source = (self.artifact_dir / rel).resolve(strict=True)
                if not source.is_relative_to(self.artifact_dir.resolve(strict=True)):
                    raise MvpCodexGenerationError(f"Artifact path escapes root: {rel}")
                target = self.workspace_manager.resolve_generated_path(workspace, rel)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
                mode = 0o755 if entry.get("executable") else 0o644
                target.chmod(mode)
            workspace_manifest = create_protected_manifest(workspace_path)
            if workspace_manifest["artifact_digest"] != supplied.get("artifact_digest"):
                raise MvpCodexGenerationError("Imported artifact digest mismatch")
            result = _result_after_generation(
                request=request,
                workspace=workspace,
                workspace_manager=self.workspace_manager,
                prompt_hash=_sha256_text(render_prompt(request, self.prompt_path)),
                codex_session_id=None,
                commands=(),
            )
            return result
        except (OSError, ManifestError, MvpCodexGenerationError) as exc:
            for child in workspace_path.iterdir():
                if child.is_dir():
                    import shutil

                    shutil.rmtree(child)
                else:
                    child.unlink()
            if isinstance(exc, MvpCodexGenerationError):
                raise
            raise MvpCodexGenerationError(f"Imported artifact rejected: {exc}") from exc


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
    codex_session_id: str | None,
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
        slugger_correlation_id=workspace.run_id,
        prompt_version=PROMPT_VERSION,
        prompt_hash=prompt_hash,
        commands=commands,
    )


def _minimal_environment(*, include_codex_api_key: bool = False) -> dict[str, str]:
    environment = {key: os.environ[key] for key in _ALLOWED_ENV if key in os.environ}
    if include_codex_api_key and _CODEX_EXEC_API_KEY_ENV in os.environ:
        environment[_CODEX_EXEC_API_KEY_ENV] = os.environ[_CODEX_EXEC_API_KEY_ENV]
    return environment


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bounded(value: str, limit: int = 1000) -> str:
    return value[:limit]


def _codex_exec_command(codex_command: tuple[str, ...]) -> tuple[str, ...]:
    executable = codex_command[0]
    return (
        executable,
        "exec",
        "--sandbox",
        "workspace-write",
        "--ask-for-approval",
        "never",
        "--skip-git-repo-check",
        "--json",
        "-",
    )


def _preflight_codex(
    codex_executable: str, workspace_path: Path, *, exec_api_key: str | None = None
) -> None:
    if not workspace_path.is_dir():
        raise MvpCodexGenerationError(f"Workspace does not exist: {workspace_path}")
    if not os.access(workspace_path, os.W_OK):
        raise MvpCodexGenerationError(f"Workspace is not writable: {workspace_path}")
    _run_preflight_command(
        [codex_executable, "--version"],
        missing_message=_missing_codex_message(codex_executable),
        failure_message=f"Codex CLI version check failed for {codex_executable!r}.",
    )
    if exec_api_key:
        return
    _run_preflight_command(
        [codex_executable, "login", "status"],
        missing_message=_missing_codex_message(codex_executable),
        failure_message=_CODEX_AUTH_HELP,
    )


def _run_preflight_command(
    command: list[str], *, missing_message: str, failure_message: str
) -> None:
    try:
        completed = subprocess.run(
            command,
            env=_minimal_environment(),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except FileNotFoundError as exc:
        raise MvpCodexGenerationError(missing_message) from exc
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MvpCodexGenerationError(f"{failure_message} {exc}") from exc
    if completed.returncode != 0:
        details = _bounded(completed.stderr or completed.stdout)
        raise MvpCodexGenerationError(f"{failure_message}\n{details}")


def _missing_codex_message(codex_executable: str) -> str:
    return (
        f"Codex CLI executable is not available: {codex_executable!r}.\n"
        "Install Codex CLI, then run:\n"
        "    codex --version\n"
        "    codex login\n"
        "    codex login status"
    )


@dataclass(frozen=True)
class _CodexJsonlParseResult:
    session_id: str | None
    error_details: tuple[str, ...] = ()


def _parse_codex_jsonl(output: str) -> _CodexJsonlParseResult:
    session_id: str | None = None
    errors: list[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        session_id = session_id or _session_id_from_event(event)
        if _event_looks_like_error(event):
            errors.append(_bounded(json.dumps(event, sort_keys=True), 500))
    return _CodexJsonlParseResult(session_id=session_id, error_details=tuple(errors))


def _session_id_from_event(event: dict[str, Any]) -> str | None:
    direct = _first_string_value(
        event,
        (
            "session_id",
            "sessionId",
            "thread_id",
            "threadId",
            "conversation_id",
            "conversationId",
            "id",
        ),
    )
    event_type = str(event.get("type", "")).lower()
    if direct and any(token in event_type for token in ("session", "thread")):
        return direct
    nested = event.get("session") or event.get("thread")
    if isinstance(nested, dict):
        return _first_string_value(nested, ("id", "session_id", "thread_id"))
    return None


def _first_string_value(mapping: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _event_looks_like_error(event: dict[str, Any]) -> bool:
    event_type = str(event.get("type", "")).lower()
    return "error" in event_type or event.get("level") == "error"


def _codex_failure_details(parsed: _CodexJsonlParseResult, stderr: str) -> str:
    parts = [*parsed.error_details]
    if stderr.strip():
        parts.append(stderr.strip())
    return "\n".join(parts) or "No error details emitted by Codex"


def _session_id_from_output(*chunks: str) -> str | None:
    text = "\n".join(chunks)
    match = re.search(
        r"(?:session[_ -]?id|session)[:= ]+([A-Za-z0-9_.:-]+)",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)
    return None


def _fixture_files(request: MvpProjectRequest, package_name: str) -> dict[str, str]:
    return {
        "README.md": f"# {request.project_name}\n\n{request.idea}\n",
        "pyproject.toml": (
            "[build-system]\nrequires = []\nbuild-backend = 'slugger_mvp_backend'\nbackend-path = ['.']\n\n"
            "[project]\n"
            f"name = '{request.project_name}'\nversion = '0.1.0'\nrequires-python = '>=3.11'\n"
            'dependencies = []\n\n[project.optional-dependencies]\ntest = ["pytest>=8,<10"]\n'
        ),
        "slugger_mvp_backend.py": _minimal_build_backend(
            request.project_name, include_pytest_extra=True
        ),
        f"src/{package_name}/__init__.py": "__all__ = ['main']\n",
        f"src/{package_name}/main.py": (
            "from __future__ import annotations\nimport argparse\n\n"
            "def build_parser() -> argparse.ArgumentParser:\n"
            f"    parser = argparse.ArgumentParser(prog='{request.project_name}')\n"
            "    parser.add_argument('--version', action='store_true')\n"
            "    subparsers = parser.add_subparsers(dest='command')\n"
            "    greet = subparsers.add_parser('greet')\n"
            "    greet.add_argument('name')\n"
            "    return parser\n\n"
            "def main(argv: list[str] | None = None) -> int:\n"
            "    parser = build_parser()\n    args = parser.parse_args(argv)\n"
            "    if args.command == 'greet':\n"
            "        print(f'Hello, {args.name}!')\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n    raise SystemExit(main())\n"
        ),
        "tests/test_main.py": (
            f"from {package_name}.main import build_parser, main\n\n"
            "def test_help_parser_has_program_name():\n"
            f"    assert build_parser().prog == '{request.project_name}'\n\n"
            "def test_main_exits_successfully():\n    assert main([]) == 0\n\n"
            "def test_greet_prints_name(capsys):\n"
            "    assert main(['greet', 'Joseph']) == 0\n"
            "    assert capsys.readouterr().out.strip() == 'Hello, Joseph!'\n"
        ),
    }


def _minimal_build_backend(
    project_name: str, *, include_pytest_extra: bool = False
) -> str:
    safe_dist = project_name.replace("-", "_")
    template = r"""
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
""".lstrip()
    return (
        template.replace("__PROJECT_NAME__", repr(project_name))
        .replace("__SAFE_DIST__", repr(safe_dist))
        .replace("__INCLUDE_PYTEST_EXTRA__", repr(include_pytest_extra))
    )
