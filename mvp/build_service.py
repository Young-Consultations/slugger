"""Build-service contract and implementation for the narrow Slugger MVP path."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import uuid

from mvp.basic_runner import BasicRunner
from mvp.integrations.codex import MvpCodexAdapter
from mvp.integrations.github import MvpGitHubPublisher
from mvp.models import MvpBuildResult, MvpProjectRequest, MvpRun, MvpRunStatus
from mvp.project_validator import ProjectValidator
from mvp.run_repository import SQLiteMvpRunRepository
from mvp.workspace import WorkspaceManager


class MvpBuildService(Protocol):
    """Application service interface for one MVP idea-to-PR build."""

    def build(self, request: MvpProjectRequest) -> MvpBuildResult:
        """Build a generated project for the supplied MVP request."""


@dataclass
class DefaultMvpBuildService(MvpBuildService):
    """Orchestrate the focused MVP dependency flow from request to draft PR."""

    run_repository: SQLiteMvpRunRepository
    workspace_manager: WorkspaceManager
    codex_adapter: MvpCodexAdapter
    project_validator: ProjectValidator
    basic_runner: BasicRunner
    github_publisher: MvpGitHubPublisher

    def build(self, request: MvpProjectRequest) -> MvpBuildResult:
        run = MvpRun(run_id=uuid.uuid4().hex, request=request)
        self.run_repository.create(run)
        workspace = None
        try:
            run.transition_to(MvpRunStatus.GENERATING)
            self.run_repository.save(run)
            workspace = self.workspace_manager.create_workspace(run.run_id)
            run.workspace_path = str(workspace.path)
            self.run_repository.save(run)

            generation = self.codex_adapter.generate_project(request, workspace)
            run.inventory = generation.inventory
            run.codex_session_id = generation.codex_session_id
            run.prompt_version = generation.prompt_version
            run.prompt_hash = generation.prompt_hash
            run.transition_to(MvpRunStatus.VALIDATING)
            self.run_repository.save(run)

            validation_results = self.project_validator.validate(request, workspace, generation.inventory)
            run.validation_results = validation_results
            if not self.project_validator.passed(validation_results):
                raise MvpBuildPhaseError("Generated project validation failed")
            run.transition_to(MvpRunStatus.TESTING)
            self.run_repository.save(run)

            runner_result = self.basic_runner.run(request, workspace)
            run.test_results = runner_result.checks
            if not runner_result.passed:
                raise MvpBuildPhaseError("Generated project tests or smoke check failed")
            run.transition_to(MvpRunStatus.PUBLISHING)
            self.run_repository.save(run)

            publish_result = self.github_publisher.publish(run, workspace, validation_results, runner_result)
            run.github_publish_result = publish_result
            run.transition_to(MvpRunStatus.COMPLETED)
            self.run_repository.save(run)
            return MvpBuildResult(run=run)
        except Exception as exc:
            if run.status is not MvpRunStatus.FAILED:
                run.error_details = str(exc)
                run.transition_to(MvpRunStatus.FAILED)
                self.run_repository.save(run)
            return MvpBuildResult(run=run)


class MvpBuildPhaseError(RuntimeError):
    """Raised internally when a required MVP phase did not pass."""


def production_mvp_build_service(root_path: Path) -> DefaultMvpBuildService:
    """Create production MVP dependencies without legacy workflow initialization."""

    from mvp.integrations.codex import CodexCliMvpAdapter
    from mvp.integrations.github import GitHubCliMvpPublisher

    workspace_manager = WorkspaceManager(root_path / ".slugger" / "workspaces")
    run_repository = SQLiteMvpRunRepository(root_path / ".slugger" / "mvp_runs.sqlite3")
    project_validator = ProjectValidator(workspace_manager)
    basic_runner = BasicRunner(workspace_manager)
    return DefaultMvpBuildService(
        run_repository=run_repository,
        workspace_manager=workspace_manager,
        codex_adapter=CodexCliMvpAdapter(workspace_manager),
        project_validator=project_validator,
        basic_runner=basic_runner,
        github_publisher=GitHubCliMvpPublisher(workspace_manager),
    )
