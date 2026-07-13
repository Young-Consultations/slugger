"""Tests for generated-project validation in the MVP path."""

from __future__ import annotations

from pathlib import Path

from mvp.integrations.codex import FakeMvpCodexAdapter
from mvp.models import MvpProjectRequest
from mvp.project_validator import ProjectValidator
from mvp.workspace import WorkspaceManager


def _request() -> MvpProjectRequest:
    return MvpProjectRequest("Create a CLI task tracker", "task-tracker", "cli", "owner/repo")


def _generated(tmp_path: Path):
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-validate")
    inventory = FakeMvpCodexAdapter(manager).generate_project(_request(), workspace).inventory
    return manager, workspace, inventory


def test_valid_cli_project_passes(tmp_path: Path) -> None:
    manager, workspace, inventory = _generated(tmp_path)

    results = ProjectValidator(manager).validate(_request(), workspace, inventory)

    assert ProjectValidator.passed(results)
    assert {result.name for result in results} == {"path_safety", "content_safety", "required_files", "python_syntax", "pyproject"}


def test_missing_required_files_fail(tmp_path: Path) -> None:
    manager, workspace, inventory = _generated(tmp_path)
    (workspace.path / "README.md").unlink()

    results = ProjectValidator(manager).validate(_request(), workspace, inventory)

    assert not ProjectValidator.passed(results)
    assert any(result.name == "required_files" and not result.passed for result in results)


def test_invalid_python_syntax_fails(tmp_path: Path) -> None:
    manager, workspace, inventory = _generated(tmp_path)
    (workspace.path / "src" / "task_tracker" / "main.py").write_text("def nope(:\n", encoding="utf-8")

    results = ProjectValidator(manager).validate(_request(), workspace, inventory)

    assert any(result.name == "python_syntax" and not result.passed for result in results)


def test_secret_like_files_fail(tmp_path: Path) -> None:
    manager, workspace, inventory = _generated(tmp_path)
    (workspace.path / ".env").write_text("TOKEN=secret\n", encoding="utf-8")

    results = ProjectValidator(manager).validate(_request(), workspace, inventory)

    assert any(result.name == "content_safety" and not result.passed for result in results)


def test_symlink_escape_fails(tmp_path: Path) -> None:
    manager, workspace, inventory = _generated(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    (workspace.path / "escape.txt").symlink_to(outside)

    results = ProjectValidator(manager).validate(_request(), workspace, inventory)

    assert any(result.name == "path_safety" and not result.passed for result in results)


def test_invalid_pyproject_fails(tmp_path: Path) -> None:
    manager, workspace, inventory = _generated(tmp_path)
    (workspace.path / "pyproject.toml").write_text("not toml = [", encoding="utf-8")

    results = ProjectValidator(manager).validate(_request(), workspace, inventory)

    assert any(result.name == "pyproject" and not result.passed for result in results)
