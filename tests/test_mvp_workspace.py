"""Tests for isolated MVP workspace management."""

from __future__ import annotations

from pathlib import Path

import pytest

from mvp.workspace import MvpWorkspace, WorkspaceManager, WorkspaceSafetyError


def test_workspace_is_created_below_approved_root(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")

    workspace = manager.create_workspace("run-1")

    assert workspace.run_id == "run-1"
    assert workspace.path.is_dir()
    assert workspace.path.is_relative_to(manager.root)
    assert workspace.path != manager.root


def test_parallel_runs_receive_different_workspaces(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")

    first = manager.create_workspace("run-1")
    second = manager.create_workspace("run-1")

    assert first.path != second.path
    assert second.run_id.startswith("run-1-")


@pytest.mark.parametrize("bad_path", ["../outside.py", "nested/../../outside.py"])
def test_parent_traversal_generated_paths_are_rejected(tmp_path: Path, bad_path: str) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-1")

    with pytest.raises(WorkspaceSafetyError, match="parent traversal"):
        manager.resolve_generated_path(workspace, bad_path)


def test_absolute_generated_paths_are_rejected(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-1")

    with pytest.raises(WorkspaceSafetyError, match="workspace-relative"):
        manager.resolve_generated_path(workspace, tmp_path / "outside.py")


def test_escaping_symlinks_are_rejected_during_inventory(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-1")
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (workspace.path / "escape.txt").symlink_to(outside)

    with pytest.raises(WorkspaceSafetyError, match="escapes workspace"):
        manager.inventory(workspace)


def test_slugger_repository_cannot_be_selected_as_workspace_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    with pytest.raises(WorkspaceSafetyError, match="repository root"):
        WorkspaceManager(repo_root)


def test_inventory_paths_are_relative_and_hashes_are_deterministic(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-1")
    manager.resolve_generated_path(workspace, "src/app.py").parent.mkdir(parents=True)
    manager.resolve_generated_path(workspace, "src/app.py").write_text("print('hi')\n", encoding="utf-8")
    manager.resolve_generated_path(workspace, "README.md").write_text("# Demo\n", encoding="utf-8")

    first = manager.inventory(workspace)
    second = manager.inventory(workspace)

    assert [file.path for file in first.files] == ["README.md", "src/app.py"]
    assert all(not Path(file.path).is_absolute() for file in first.files)
    assert first.inventory_hash == second.inventory_hash
    assert [file.sha256 for file in first.files] == [file.sha256 for file in second.files]


def test_cleanup_is_explicit_and_removes_workspace(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-1")

    manager.cleanup(MvpWorkspace(run_id=workspace.run_id, path=workspace.path))

    assert not workspace.path.exists()
