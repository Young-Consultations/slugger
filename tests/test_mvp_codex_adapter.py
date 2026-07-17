"""Tests for the MVP Codex generation adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
from typing import Any

import pytest

from mvp.integrations.codex import (
    ArtifactMvpCodexAdapter,
    CodexCliMvpAdapter,
    FakeMvpCodexAdapter,
    MvpCodexAdapter,
    MvpCodexGenerationError,
    PROMPT_VERSION,
    _minimal_build_backend,
    package_name_for_project,
    render_prompt,
)
from mvp.models import MvpProjectRequest
from mvp.inventory_manifest import sanitize_protected_artifact, write_protected_manifest
from mvp.workspace import WorkspaceManager


def _request() -> MvpProjectRequest:
    return MvpProjectRequest(
        idea="Create a CLI task tracker with add, list, and done commands",
        project_name="task-tracker",
        template="cli",
        github_repository="mightyjoe909/task-tracker",
    )


def _write_required_project(workspace: Path) -> None:
    package = workspace / "src" / "task_tracker"
    package.mkdir(parents=True)
    (workspace / "README.md").write_text("# task-tracker\n", encoding="utf-8")
    (workspace / "pyproject.toml").write_text(
        "[project]\nname='task-tracker'\n", encoding="utf-8"
    )
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "main.py").write_text("def main(): return 0\n", encoding="utf-8")
    tests = workspace / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text(
        "def test_ok(): assert True\n", encoding="utf-8"
    )


def _fake_successful_subprocess(workspace: Path, captured: list[dict[str, Any]]):
    def fake_run(command, **kwargs):
        captured.append({"command": command, **kwargs})
        if command == ["codex", "--version"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="codex 1.0\n", stderr=""
            )
        if command == ["codex", "login", "status"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="authenticated\n", stderr=""
            )
        _write_required_project(workspace)
        stdout = "diagnostic line\n" + json.dumps(
            {"type": "session.started", "session_id": "session-jsonl-123"}
        )
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    return fake_run


def test_fake_codex_adapter_implements_production_contract(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-004")
    adapter: MvpCodexAdapter = FakeMvpCodexAdapter(manager)

    result = adapter.generate_project(_request(), workspace)

    assert result.prompt_version == PROMPT_VERSION
    assert len(result.prompt_hash) == 64
    assert result.codex_session_id is None
    assert result.slugger_correlation_id == "run-004"
    paths = {file.path for file in result.inventory.files}
    assert {
        "README.md",
        "pyproject.toml",
        "src/task_tracker/__init__.py",
        "src/task_tracker/main.py",
        "tests/test_main.py",
    }.issubset(paths)
    main_py = (workspace.path / "src" / "task_tracker" / "main.py").read_text(
        encoding="utf-8"
    )
    assert "subparsers.add_parser('greet')" in main_py
    assert "Hello, {args.name}!" in main_py


def test_fake_codex_adapter_fails_without_required_files(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-missing")
    adapter = FakeMvpCodexAdapter(manager, omit_required_file="tests/test_main.py")

    with pytest.raises(MvpCodexGenerationError, match="missing required files"):
        adapter.generate_project(_request(), workspace)


def test_fake_codex_failure_blocks_inventory(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-failed")
    adapter = FakeMvpCodexAdapter(manager, fail=True)

    with pytest.raises(MvpCodexGenerationError, match="Fake Codex generation failed"):
        adapter.generate_project(_request(), workspace)
    assert list(workspace.path.rglob("*")) == []


def test_prompt_is_versioned_and_contains_constraints() -> None:
    prompt = render_prompt(_request())

    assert "Python 3.11" in prompt
    assert "src/" in prompt
    assert "Do not run Git commands" in prompt
    assert "Do not modify anything outside" in prompt
    assert "task_tracker" in prompt
    assert "[project.optional-dependencies]" in prompt
    assert ".[test]" in prompt


def test_package_name_for_project_normalizes_kebab_case() -> None:
    assert package_name_for_project("task-tracker") == "task_tracker"


def test_production_adapter_runs_inside_workspace_with_minimal_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-prod")
    captured: list[dict[str, Any]] = []

    monkeypatch.setattr(
        subprocess, "run", _fake_successful_subprocess(workspace.path, captured)
    )
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    monkeypatch.delenv("CODEX_API_KEY", raising=False)
    monkeypatch.setenv("PYTHONPATH", "must-not-leak")
    monkeypatch.setenv("UNRELATED_SECRET", "must-not-leak")

    adapter = CodexCliMvpAdapter(manager, timeout_seconds=12)
    result = adapter.generate_project(_request(), workspace)

    generation = captured[-1]
    command = generation["command"]
    assert tuple(command) == (
        "codex",
        "exec",
        "--sandbox",
        "workspace-write",
        "--ask-for-approval",
        "never",
        "--skip-git-repo-check",
        "--json",
        "-",
    )
    assert "--dangerously-bypass-approvals-and-sandbox" not in command
    assert "--yolo" not in command
    assert "danger-full-access" not in command
    assert "secret" not in command
    assert generation["cwd"] == workspace.path
    assert generation["input"] == render_prompt(_request())
    assert generation["text"] is True
    assert generation["capture_output"] is True
    assert generation["timeout"] == 12
    assert generation["check"] is False
    assert "shell" not in generation
    assert generation["env"] == {
        key: os.environ[key]
        for key in (
            "HOME",
            "PATH",
            "SSL_CERT_FILE",
            "REQUESTS_CA_BUNDLE",
        )
        if key in os.environ
    }
    assert "OPENAI_API_KEY" not in generation["env"]
    assert "CODEX_API_KEY" not in generation["env"]
    assert "PYTHONPATH" not in generation["env"]
    assert "UNRELATED_SECRET" not in generation["env"]
    assert result.codex_session_id == "session-jsonl-123"


def test_production_adapter_accepts_scoped_exec_api_key_without_login_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-exec-key")
    captured: list[dict[str, Any]] = []

    def fake_run(command, **kwargs):
        captured.append({"command": command, **kwargs})
        if command == ["codex", "--version"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="codex 1.0\n", stderr=""
            )
        if command == ["codex", "login", "status"]:
            raise AssertionError("login status must be skipped for CODEX_API_KEY auth")
        assert kwargs["env"]["CODEX_API_KEY"] == "exec-only-secret"
        _write_required_project(workspace.path)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {"type": "session.started", "session_id": "session-with-key"}
            ),
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("CODEX_API_KEY", "exec-only-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-leak")

    result = CodexCliMvpAdapter(manager).generate_project(_request(), workspace)

    assert [tuple(call["command"]) for call in captured] == [
        ("codex", "--version"),
        result.commands[0],
    ]
    assert result.codex_session_id == "session-with-key"
    assert "exec-only-secret" not in result.commands[0]
    assert "OPENAI_API_KEY" not in captured[-1]["env"]


def test_production_adapter_fails_on_codex_nonzero_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-nonzero")

    def fake_run(command, **kwargs):
        if command == ["codex", "--version"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="codex 1.0\n", stderr=""
            )
        if command == ["codex", "login", "status"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="authenticated\n", stderr=""
            )
        return subprocess.CompletedProcess(
            command, 42, stdout='{"type": "error", "message": "bad"}\n', stderr="boom"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    adapter = CodexCliMvpAdapter(manager)

    with pytest.raises(MvpCodexGenerationError, match="Codex exited with status 42"):
        adapter.generate_project(_request(), workspace)


def test_production_adapter_preserves_prompt_hash_and_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-prompt")

    captured: list[dict[str, Any]] = []
    monkeypatch.setattr(
        subprocess, "run", _fake_successful_subprocess(workspace.path, captured)
    )
    result = CodexCliMvpAdapter(manager).generate_project(_request(), workspace)

    assert result.prompt_version == PROMPT_VERSION
    assert (
        result.prompt_hash
        == __import__("hashlib")
        .sha256(render_prompt(_request()).encode("utf-8"))
        .hexdigest()
    )
    assert result.codex_session_id == "session-jsonl-123"


def test_production_adapter_fails_closed_when_codex_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-missing-codex")

    def fake_run(*args, **kwargs):
        raise FileNotFoundError("codex")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(
        MvpCodexGenerationError, match="Codex CLI executable is not available"
    ):
        CodexCliMvpAdapter(manager).generate_project(_request(), workspace)
    assert list(workspace.path.rglob("*")) == []


def test_production_adapter_fails_when_codex_unauthenticated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-unauth")

    def fake_run(command, **kwargs):
        if command == ["codex", "--version"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="codex 1.0\n", stderr=""
            )
        if command == ["codex", "login", "status"]:
            return subprocess.CompletedProcess(
                command, 1, stdout="", stderr="not logged in"
            )
        raise AssertionError("generation must not run when auth preflight fails")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(MvpCodexGenerationError, match="Codex CLI authentication"):
        CodexCliMvpAdapter(manager).generate_project(_request(), workspace)
    assert list(workspace.path.rglob("*")) == []


def test_production_adapter_fails_when_codex_generates_no_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-empty")

    def fake_run(command, **kwargs):
        if command == ["codex", "--version"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="codex 1.0\n", stderr=""
            )
        if command == ["codex", "login", "status"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="authenticated\n", stderr=""
            )
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({"type": "session.started", "session_id": "empty"}),
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(MvpCodexGenerationError, match="missing required files"):
        CodexCliMvpAdapter(manager).generate_project(_request(), workspace)


def _write_hello_codex_artifact(root: Path) -> None:
    package = root / "src" / "hello_codex"
    (package / "__pycache__").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "README.md").write_text("# hello-codex\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        "[build-system]\nrequires=[]\nbuild-backend='slugger_mvp_backend'\nbackend-path=['.']\n\n[project]\nname='hello-codex'\nversion='0.1.0'\nrequires-python='>=3.11'\n[project.optional-dependencies]\ntest=['pytest>=8,<10']\n",
        encoding="utf-8",
    )
    (root / "slugger_mvp_backend.py").write_text(
        _minimal_build_backend("hello-codex", include_pytest_extra=True),
        encoding="utf-8",
    )
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "main.py").write_text(
        "from __future__ import annotations\nimport argparse\ndef build_parser():\n    parser=argparse.ArgumentParser(prog='hello-codex')\n    subparsers=parser.add_subparsers(dest='command')\n    greet=subparsers.add_parser('greet')\n    greet.add_argument('name')\n    return parser\ndef main(argv=None):\n    args=build_parser().parse_args(argv)\n    if args.command == 'greet': print(f'Hello, {args.name}!')\n    return 0\n",
        encoding="utf-8",
    )
    (root / "tests" / "test_main.py").write_text(
        "def test_ok(): assert True\n", encoding="utf-8"
    )
    (package / "__pycache__" / "main.cpython-312.pyc").write_bytes(b"pyc")
    (package / "__pycache__" / "__init__.cpython-312.pyc").write_bytes(b"pyc")
    for dirname in [".pytest_cache", "src/hello_codex.egg-info", "build", "dist"]:
        d = root / dirname
        d.mkdir(parents=True, exist_ok=True)
        (d / "runtime.txt").write_text("runtime", encoding="utf-8")
    (root / ".coverage").write_text("coverage", encoding="utf-8")


def _artifact_project(root: Path, project_name: str = "hello-codex") -> None:
    package_name = project_name.replace("-", "_")
    package = root / "src" / package_name
    package.mkdir(parents=True)
    (root / "README.md").write_text(f"# {project_name}\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        f"[build-system]\nrequires=[]\nbuild-backend='slugger_mvp_backend'\nbackend-path=['.']\n\n[project]\nname='{project_name}'\nversion='0.1.0'\ndependencies=[]\n[project.optional-dependencies]\ntest=['pytest>=8,<10']\n",
        encoding="utf-8",
    )
    (root / "slugger_mvp_backend.py").write_text(
        _minimal_build_backend(project_name, include_pytest_extra=True),
        encoding="utf-8",
    )
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "main.py").write_text(
        "from __future__ import annotations\nimport argparse\n"
        "def build_parser():\n    p=argparse.ArgumentParser(prog='hello-codex'); s=p.add_subparsers(dest='command'); g=s.add_parser('greet'); g.add_argument('name'); return p\n"
        "def main(argv=None):\n    a=build_parser().parse_args(argv)\n    if a.command == 'greet': print(f'Hello, {a.name}!')\n    return 0\n"
        "if __name__ == '__main__': raise SystemExit(main())\n",
        encoding="utf-8",
    )
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text(
        "from hello_codex.main import main\n\ndef test_greet(capsys):\n    assert main(['greet','Joseph']) == 0\n    assert capsys.readouterr().out == 'Hello, Joseph!\\n'\ndef test_empty(): assert main([]) == 0\ndef test_import(): import hello_codex\n",
        encoding="utf-8",
    )


def test_artifact_adapter_imports_sanitized_workflow_29529825540_shape(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    _write_hello_codex_artifact(raw)
    sanitized = tmp_path / "sanitized"
    manifest = tmp_path / "generated-project-manifest.json"
    sanitize_protected_artifact(raw, sanitized)
    write_protected_manifest(sanitized, manifest)

    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("imported")
    result = ArtifactMvpCodexAdapter(manager, sanitized, manifest).generate_project(
        MvpProjectRequest(
            idea="Small dependency-minimal Python CLI demo",
            project_name="hello-codex",
            template="cli",
            github_repository="example/hello-codex",
        ),
        workspace,
    )

    assert result.inventory.inventory_hash
    assert not any("__pycache__" in p.as_posix() for p in workspace.path.rglob("*"))
    assert not (workspace.path / ".coverage").exists()


def test_artifact_adapter_fails_closed_on_unknown_extra_source_and_cleans_workspace(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    _write_hello_codex_artifact(raw)
    sanitized = tmp_path / "sanitized"
    sanitize_protected_artifact(raw, sanitized)
    manifest = tmp_path / "generated-project-manifest.json"
    write_protected_manifest(sanitized, manifest)
    (sanitized / "unexpected.bin").write_bytes(b"bad")

    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("bad-import")
    with pytest.raises(MvpCodexGenerationError):
        ArtifactMvpCodexAdapter(manager, sanitized, manifest).generate_project(
            MvpProjectRequest(
                idea="Small dependency-minimal Python CLI demo",
                project_name="hello-codex",
                template="cli",
                github_repository="example/hello-codex",
            ),
            workspace,
        )
    assert list(workspace.path.rglob("*")) == []


def test_artifact_adapter_rejects_manifest_tampering(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    _write_hello_codex_artifact(raw)
    sanitized = tmp_path / "sanitized"
    sanitize_protected_artifact(raw, sanitized)
    manifest = tmp_path / "generated-project-manifest.json"
    write_protected_manifest(sanitized, manifest)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["entries"][0]["sha256"] = "0" * 64
    manifest.write_text(json.dumps(data), encoding="utf-8")

    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("tampered")
    with pytest.raises(MvpCodexGenerationError):
        ArtifactMvpCodexAdapter(manager, sanitized, manifest).generate_project(
            MvpProjectRequest(
                idea="Small dependency-minimal Python CLI demo",
                project_name="hello-codex",
                template="cli",
                github_repository="example/hello-codex",
            ),
            workspace,
        )
