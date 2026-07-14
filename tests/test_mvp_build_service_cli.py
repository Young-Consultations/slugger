"""Tests for MVP build-service orchestration and CLI wiring."""

from __future__ import annotations

import json
from pathlib import Path

from cli import main as cli_main
from mvp.basic_runner import BasicRunner
from mvp.build_service import DefaultMvpBuildService
from mvp.integrations.codex import FakeMvpCodexAdapter
from mvp.integrations.github import FakeMvpGitHubPublisher
from mvp.models import MvpProjectRequest, MvpRunStatus
from mvp.project_validator import ProjectValidator
from mvp.run_repository import SQLiteMvpRunRepository
from mvp.workspace import WorkspaceManager


def _service(tmp_path: Path, *, codex_fail: bool = False, github_fail: bool = False) -> tuple[DefaultMvpBuildService, FakeMvpGitHubPublisher]:
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    publisher = FakeMvpGitHubPublisher(fail=github_fail)
    return (
        DefaultMvpBuildService(
            run_repository=SQLiteMvpRunRepository(tmp_path / "runs.sqlite3"),
            workspace_manager=workspace_manager,
            codex_adapter=FakeMvpCodexAdapter(workspace_manager, fail=codex_fail),
            project_validator=ProjectValidator(workspace_manager),
            basic_runner=BasicRunner(workspace_manager),
            github_publisher=publisher,
        ),
        publisher,
    )


def _request() -> MvpProjectRequest:
    return MvpProjectRequest(
        idea="Create a CLI task tracker with add, list, and done commands",
        project_name="task-tracker",
        template="cli",
        github_repository="owner/task-tracker",
    )


def test_build_service_invokes_components_in_order_and_completes(tmp_path: Path) -> None:
    service, publisher = _service(tmp_path)

    result = service.build(_request())

    run = result.run
    assert run.status is MvpRunStatus.COMPLETED
    assert run.workspace_path is not None
    assert run.inventory is not None
    assert run.validation_results and all(check.passed for check in run.validation_results)
    assert run.test_results and all(check.passed for check in run.test_results)
    assert run.github_publish_result is not None
    assert run.github_publish_result.draft is True
    assert publisher.publish_count == 1


def test_build_service_stops_after_codex_failure(tmp_path: Path) -> None:
    service, publisher = _service(tmp_path, codex_fail=True)

    result = service.build(_request())

    assert result.run.status is MvpRunStatus.FAILED
    assert "Codex" in (result.run.error_details or "")
    assert result.run.validation_results == ()
    assert result.run.test_results == ()
    assert result.run.github_publish_result is None
    assert publisher.publish_count == 0


def test_build_service_does_not_publish_after_validation_failure(tmp_path: Path) -> None:
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    publisher = FakeMvpGitHubPublisher()
    service = DefaultMvpBuildService(
        run_repository=SQLiteMvpRunRepository(tmp_path / "runs.sqlite3"),
        workspace_manager=workspace_manager,
        codex_adapter=FakeMvpCodexAdapter(workspace_manager, omit_required_file="tests/test_main.py"),
        project_validator=ProjectValidator(workspace_manager),
        basic_runner=BasicRunner(workspace_manager),
        github_publisher=publisher,
    )

    result = service.build(_request())

    assert result.run.status is MvpRunStatus.FAILED
    assert result.run.test_results == ()
    assert result.run.github_publish_result is None
    assert publisher.publish_count == 0


def test_mvp_cli_build_outputs_structured_summary(monkeypatch, capsys, tmp_path: Path) -> None:
    class StubService:
        def build(self, request: MvpProjectRequest):
            service, _publisher = _service(tmp_path)
            return service.build(request)

    def fake_factory(root_path: Path) -> StubService:
        return StubService()

    monkeypatch.setattr("mvp.build_service.production_mvp_build_service", fake_factory)

    exit_code = cli_main.main([
        "mvp",
        "build",
        "Create a CLI task tracker with add, list, and done commands",
        "--name",
        "task-tracker",
        "--template",
        "cli",
        "--repo",
        "owner/task-tracker",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "completed"
    assert payload["generated_files"] > 0
    assert payload["validation_passed"] is True
    assert payload["test_passed"] is True
    assert payload["smoke_passed"] is True
    assert payload["github_branch"].startswith("slugger/generated-task-tracker-")
    assert payload["draft_pr_url"].startswith("https://github.com/owner/task-tracker/pull/")


def test_build_service_detects_source_tree_mutation(tmp_path: Path) -> None:
    class MutatingCodex(FakeMvpCodexAdapter):
        def __init__(self, manager: WorkspaceManager, source_file: Path) -> None:
            super().__init__(manager)
            self.source_file = source_file

        def generate_project(self, request, workspace):
            result = super().generate_project(request, workspace)
            self.source_file.write_text("changed\n", encoding="utf-8")
            return result

    source_root = tmp_path / "source"
    source_root.mkdir()
    source_file = source_root / "tracked.py"
    source_file.write_text("original\n", encoding="utf-8")
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    publisher = FakeMvpGitHubPublisher()
    service = DefaultMvpBuildService(
        run_repository=SQLiteMvpRunRepository(tmp_path / "runs.sqlite3"),
        workspace_manager=workspace_manager,
        codex_adapter=MutatingCodex(workspace_manager, source_file),
        project_validator=ProjectValidator(workspace_manager),
        basic_runner=BasicRunner(workspace_manager),
        github_publisher=publisher,
        source_root=source_root,
    )

    result = service.build(_request())

    assert result.run.status is MvpRunStatus.FAILED
    assert "source tree" in (result.run.error_details or "")
    assert result.run.validation_results == ()
    assert publisher.publish_count == 0


def test_installed_wheel_style_cli_runtime_path_outside_site_packages(monkeypatch, capsys, tmp_path: Path) -> None:
    home = tmp_path / "runtime-home"
    monkeypatch.setenv("SLUGGER_HOME", str(home))

    class StubService:
        def build(self, request: MvpProjectRequest):
            service, _publisher = _service(tmp_path)
            return service.build(request)

    monkeypatch.setattr("mvp.build_service.production_mvp_build_service", lambda root_path: StubService())
    assert cli_main.main(["mvp", "build", "Create a CLI task tracker with add, list, and done commands", "--name", "task-tracker", "--template", "cli", "--repo", "owner/task-tracker"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert Path(payload["workspace_root"]).is_relative_to(home.resolve())
    assert "site-packages" not in payload["sqlite_path"]
