"""MVP Codex generation adapter for isolated Python project workspaces."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import re
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
        completed = subprocess.run(
            command,
            cwd=workspace_path,
            env=_minimal_environment(),
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            output = _bounded(completed.stderr or completed.stdout)
            raise MvpCodexGenerationError(
                f"Codex exited with status {completed.returncode}: {output}"
            )
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
            "[build-system]\nrequires = ['setuptools>=68']\nbuild-backend = 'setuptools.build_meta'\n\n"
            "[project]\n"
            f"name = '{request.project_name}'\nversion = '0.1.0'\nrequires-python = '>=3.11'\n"
            "dependencies = []\n\n[project.optional-dependencies]\ntest = ['pytest']\n"
        ),
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
