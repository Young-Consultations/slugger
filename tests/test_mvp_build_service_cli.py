"""Tests for MVP build-service orchestration and CLI wiring."""

from __future__ import annotations

import json
from pathlib import Path

from cli import main as cli_main
from mvp.basic_runner import BasicRunner
from mvp.build_service import DefaultMvpBuildService
from mvp.integrations.codex import ArtifactMvpCodexAdapter, FakeMvpCodexAdapter
from mvp.integrations.github import FakeMvpGitHubPublisher
from mvp.inventory_manifest import write_protected_manifest
from mvp.models import MvpProjectRequest, MvpRunStatus
from mvp.project_validator import ProjectValidator
from mvp.run_repository import SQLiteMvpRunRepository
from mvp.workspace import WorkspaceManager


def _service(
    tmp_path: Path, *, codex_fail: bool = False, github_fail: bool = False
) -> tuple[DefaultMvpBuildService, FakeMvpGitHubPublisher]:
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


def test_build_service_invokes_components_in_order_and_completes(
    tmp_path: Path,
) -> None:
    service, publisher = _service(tmp_path)

    result = service.build(_request())

    run = result.run
    assert run.status is MvpRunStatus.COMPLETED
    assert run.workspace_path is not None
    assert run.inventory is not None
    assert run.validation_results and all(
        check.passed for check in run.validation_results
    )
    assert run.test_results and all(check.passed for check in run.test_results)
    assert run.github_publish_result is not None
    assert run.github_publish_result.draft is True
    assert publisher.publish_count == 1


def test_build_service_skip_publish_completes_after_tests(
    monkeypatch, tmp_path: Path
) -> None:
    service, publisher = _service(tmp_path)
    monkeypatch.setenv("SLUGGER_MVP_SKIP_PUBLISH", "1")

    result = service.build(_request())

    run = result.run
    assert run.status is MvpRunStatus.READY_TO_PUBLISH
    assert run.error_details is None
    assert run.validation_results and all(
        check.passed for check in run.validation_results
    )
    assert run.test_results and all(check.passed for check in run.test_results)
    assert run.github_publish_result is None
    assert publisher.publish_count == 0


def test_build_service_stops_after_codex_failure(tmp_path: Path) -> None:
    service, publisher = _service(tmp_path, codex_fail=True)

    result = service.build(_request())

    assert result.run.status is MvpRunStatus.FAILED
    assert "Codex" in (result.run.error_details or "")
    assert result.run.validation_results == ()
    assert result.run.test_results == ()
    assert result.run.github_publish_result is None
    assert publisher.publish_count == 0


def test_build_service_does_not_publish_after_validation_failure(
    tmp_path: Path,
) -> None:
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    publisher = FakeMvpGitHubPublisher()
    service = DefaultMvpBuildService(
        run_repository=SQLiteMvpRunRepository(tmp_path / "runs.sqlite3"),
        workspace_manager=workspace_manager,
        codex_adapter=FakeMvpCodexAdapter(
            workspace_manager, omit_required_file="tests/test_main.py"
        ),
        project_validator=ProjectValidator(workspace_manager),
        basic_runner=BasicRunner(workspace_manager),
        github_publisher=publisher,
    )

    result = service.build(_request())

    assert result.run.status is MvpRunStatus.FAILED
    assert result.run.test_results == ()
    assert result.run.github_publish_result is None
    assert publisher.publish_count == 0


def test_mvp_cli_build_outputs_structured_summary(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    class StubService:
        def build(self, request: MvpProjectRequest):
            service, _publisher = _service(tmp_path)
            return service.build(request)

    def fake_factory(root_path: Path) -> StubService:
        return StubService()

    monkeypatch.setattr("mvp.build_service.production_mvp_build_service", fake_factory)

    exit_code = cli_main.main(
        [
            "mvp",
            "build",
            "Create a CLI task tracker with add, list, and done commands",
            "--name",
            "task-tracker",
            "--template",
            "cli",
            "--repo",
            "owner/task-tracker",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "completed"
    assert payload["generated_files"] > 0
    assert payload["validation_passed"] is True
    assert payload["test_passed"] is True
    assert payload["smoke_passed"] is True
    assert payload["github_branch"].startswith("slugger/generated-task-tracker-")
    assert payload["draft_pr_url"].startswith(
        "https://github.com/owner/task-tracker/pull/"
    )


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


def test_installed_wheel_style_cli_runtime_path_outside_site_packages(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    home = tmp_path / "runtime-home"
    monkeypatch.setenv("SLUGGER_HOME", str(home))

    class StubService:
        def build(self, request: MvpProjectRequest):
            service, _publisher = _service(tmp_path)
            return service.build(request)

    monkeypatch.setattr(
        "mvp.build_service.production_mvp_build_service",
        lambda root_path: StubService(),
    )
    assert (
        cli_main.main(
            [
                "mvp",
                "build",
                "Create a CLI task tracker with add, list, and done commands",
                "--name",
                "task-tracker",
                "--template",
                "cli",
                "--repo",
                "owner/task-tracker",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)

    assert Path(payload["workspace_root"]).is_relative_to(home.resolve())
    assert "site-packages" not in payload["sqlite_path"]


def test_publish_completed_run_is_service_idempotent_after_restart(
    tmp_path: Path,
) -> None:
    service, publisher = _service(tmp_path)
    import os

    old = os.environ.get("SLUGGER_MVP_SKIP_PUBLISH")
    os.environ["SLUGGER_MVP_SKIP_PUBLISH"] = "1"
    try:
        built = service.build(_request()).run
    finally:
        if old is None:
            os.environ.pop("SLUGGER_MVP_SKIP_PUBLISH", None)
        else:
            os.environ["SLUGGER_MVP_SKIP_PUBLISH"] = old

    first = service.publish(built.run_id).run
    assert first.status is MvpRunStatus.COMPLETED
    assert first.error_details is None
    assert first.github_publish_result is not None
    persisted = first.github_publish_result

    reloaded = service.run_repository.require(built.run_id)
    assert reloaded.github_publish_result == persisted
    second = service.publish(built.run_id).run
    assert second.status is MvpRunStatus.COMPLETED
    assert second.github_publish_result == persisted

    restarted_service, _restarted_publisher = _service(tmp_path)
    third = restarted_service.publish(built.run_id).run
    assert third.status is MvpRunStatus.COMPLETED
    assert third.error_details is None
    assert third.github_publish_result == persisted
    assert publisher.publish_count == 1


def test_artifact_adapter_build_persists_run_evidence(
    monkeypatch, tmp_path: Path
) -> None:
    artifact = tmp_path / "artifact"
    artifact.mkdir()
    from tests.test_mvp_codex_adapter import _artifact_project

    _artifact_project(artifact)
    manifest = tmp_path / "manifest.json"
    write_protected_manifest(artifact, manifest)
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    repo = SQLiteMvpRunRepository(tmp_path / "runs.sqlite3")
    service = DefaultMvpBuildService(
        run_repository=repo,
        workspace_manager=workspace_manager,
        codex_adapter=ArtifactMvpCodexAdapter(
            workspace_manager,
            artifact,
            manifest,
        ),
        project_validator=ProjectValidator(workspace_manager),
        basic_runner=BasicRunner(workspace_manager),
        github_publisher=FakeMvpGitHubPublisher(),
    )
    monkeypatch.setenv("SLUGGER_MVP_SKIP_PUBLISH", "1")

    run = service.build(
        MvpProjectRequest("Create hello", "hello-codex", "cli", "owner/repo")
    ).run
    reloaded = repo.require(run.run_id)

    assert reloaded.run_id == run.run_id
    assert reloaded.status is MvpRunStatus.READY_TO_PUBLISH
    assert reloaded.external_generation_id is None
    assert reloaded.codex_session_id is None
    assert reloaded.artifact_manifest_digest is None
    assert reloaded.inventory is not None
    assert reloaded.validation_results
    assert any(
        c.name == "functional_greet_joseph" and c.passed for c in reloaded.test_results
    )
    assert reloaded.publication_skipped is True
