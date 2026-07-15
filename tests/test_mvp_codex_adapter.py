"""Tests for the MVP Codex generation adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
from typing import Any

import pytest

from mvp.integrations.codex import (
    CodexCliMvpAdapter,
    FakeMvpCodexAdapter,
    MvpCodexAdapter,
    MvpCodexGenerationError,
    PROMPT_VERSION,
    package_name_for_project,
    render_prompt,
)
from mvp.models import MvpProjectRequest
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
