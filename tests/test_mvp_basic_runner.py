"""Tests for the MVP basic project runner."""

from __future__ import annotations

from pathlib import Path

from mvp.basic_runner import BasicRunner
from mvp.integrations.codex import FakeMvpCodexAdapter
from mvp.models import MvpProjectRequest
from mvp.workspace import WorkspaceManager


def _request() -> MvpProjectRequest:
    return MvpProjectRequest("Create a CLI task tracker", "task-tracker", "cli", "owner/repo")


def _workspace(tmp_path: Path):
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-runner")
    FakeMvpCodexAdapter(manager).generate_project(_request(), workspace)
    return manager, workspace


def test_real_runner_installs_tests_and_smokes_valid_cli_project(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    assert result.passed
    assert [check.name for check in result.checks] == ["create_environment", "install_project", "run_tests", "cli_smoke"]
    assert any("1 passed" in check.details.get("stdout", "") or "2 passed" in check.details.get("stdout", "") for check in result.checks)


def test_test_failure_blocks_smoke_and_publication_preconditions(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "tests" / "test_main.py").write_text("def test_bad():\n    assert False\n", encoding="utf-8")

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    assert not result.passed
    assert any(check.name == "run_tests" and not check.passed for check in result.checks)
    assert any(check.name == "cli_smoke" and not check.passed and "Skipped" in check.message for check in result.checks)


def test_install_failure_blocks_later_phases(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "pyproject.toml").write_text("not toml = [", encoding="utf-8")

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    assert not result.passed
    assert any(check.name == "install_project" and not check.passed for check in result.checks)
    assert any(check.name == "run_tests" and not check.passed and "Skipped" in check.message for check in result.checks)
