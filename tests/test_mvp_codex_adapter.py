"""Tests for the MVP Codex generation adapter."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

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


def test_package_name_for_project_normalizes_kebab_case() -> None:
    assert package_name_for_project("task-tracker") == "task_tracker"


def test_production_adapter_runs_inside_workspace_with_minimal_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-prod")
    captured: dict[str, object] = {}

    def fake_run(command, *, cwd, env, text, capture_output, timeout, check):
        captured.update(
            command=command,
            cwd=cwd,
            env=env,
            text=text,
            capture_output=capture_output,
            timeout=timeout,
            check=check,
        )
        package = workspace.path / "src" / "task_tracker"
        package.mkdir(parents=True)
        (workspace.path / "README.md").write_text("# task-tracker\n", encoding="utf-8")
        (workspace.path / "pyproject.toml").write_text(
            "[project]\nname='task-tracker'\n", encoding="utf-8"
        )
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "main.py").write_text("def main(): return 0\n", encoding="utf-8")
        tests = workspace.path / "tests"
        tests.mkdir()
        (tests / "test_main.py").write_text(
            "def test_ok(): assert True\n", encoding="utf-8"
        )
        return subprocess.CompletedProcess(
            command, 0, stdout="session id: abc123", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    monkeypatch.setenv("PYTHONPATH", "must-not-leak")
    monkeypatch.setenv("UNRELATED_SECRET", "must-not-leak")

    adapter = CodexCliMvpAdapter(manager, timeout_seconds=12)
    result = adapter.generate_project(_request(), workspace)

    assert captured["cwd"] == workspace.path
    assert captured["text"] is True
    assert captured["capture_output"] is True
    assert captured["timeout"] == 12
    assert captured["check"] is False
    assert captured["env"] == {
        key: os.environ[key]
        for key in (
            "HOME",
            "PATH",
            "OPENAI_API_KEY",
            "SSL_CERT_FILE",
            "REQUESTS_CA_BUNDLE",
        )
        if key in os.environ
    }
    assert "PYTHONPATH" not in captured["env"]
    assert "UNRELATED_SECRET" not in captured["env"]
    assert result.codex_session_id == "abc123"
    assert result.commands[0][0:3] == ("codex", "exec", "--skip-git-repo-check")


def test_production_adapter_fails_on_codex_nonzero_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-nonzero")

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 42, stdout="", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)
    adapter = CodexCliMvpAdapter(manager)

    with pytest.raises(MvpCodexGenerationError, match="Codex exited with status 42"):
        adapter.generate_project(_request(), workspace)


def test_production_adapter_preserves_prompt_hash_and_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-prompt")

    def fake_run(command, **kwargs):
        package = workspace.path / "src" / "task_tracker"
        package.mkdir(parents=True)
        (workspace.path / "README.md").write_text("# task-tracker\n", encoding="utf-8")
        (workspace.path / "pyproject.toml").write_text(
            "[project]\nname='task-tracker'\n", encoding="utf-8"
        )
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "main.py").write_text("def main(): return 0\n", encoding="utf-8")
        (workspace.path / "tests").mkdir()
        (workspace.path / "tests" / "test_main.py").write_text(
            "def test_ok(): assert True\n", encoding="utf-8"
        )
        return subprocess.CompletedProcess(
            command, 0, stdout="session: session-xyz", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = CodexCliMvpAdapter(manager).generate_project(_request(), workspace)

    assert result.prompt_version == PROMPT_VERSION
    assert (
        result.prompt_hash
        == __import__("hashlib")
        .sha256(render_prompt(_request()).encode("utf-8"))
        .hexdigest()
    )
    assert result.codex_session_id == "session-xyz"


def test_production_adapter_fails_closed_when_codex_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-missing-codex")

    def fake_run(*args, **kwargs):
        raise FileNotFoundError("codex")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(MvpCodexGenerationError, match="Codex command failed"):
        CodexCliMvpAdapter(manager).generate_project(_request(), workspace)
    assert list(workspace.path.rglob("*")) == []
