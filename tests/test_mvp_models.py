"""Unit tests for MVP domain models and build-service contract."""

from __future__ import annotations

from typing import cast

import pytest

from mvp.build_service import MvpBuildService
from mvp.models import (
    CheckResult,
    GeneratedFile,
    GeneratedProjectInventory,
    GitHubPublishResult,
    MvpBuildResult,
    MvpProjectRequest,
    MvpRun,
    MvpRunStatus,
)


def test_project_request_accepts_valid_cli_request() -> None:
    request = MvpProjectRequest(
        idea="Create a CLI task tracker",
        project_name="task-tracker",
        template="cli",
        github_repository="Young-Consultations/task-tracker",
        base_branch="main",
    )

    assert request.idea == "Create a CLI task tracker"
    assert request.project_name == "task-tracker"
    assert request.template == "cli"
    assert request.github_repository == "Young-Consultations/task-tracker"
    assert request.base_branch == "main"


@pytest.mark.parametrize("idea", ["", "   "])
def test_project_request_rejects_empty_idea(idea: str) -> None:
    with pytest.raises(ValueError, match="idea is required"):
        MvpProjectRequest(
            idea=idea,
            project_name="task-tracker",
            template="cli",
            github_repository="owner/repo",
        )


@pytest.mark.parametrize(
    "project_name",
    ["TaskTracker", "task_tracker", "task tracker", "-task", "task-", "1-task"],
)
def test_project_request_rejects_invalid_project_names(project_name: str) -> None:
    with pytest.raises(ValueError, match="project_name"):
        MvpProjectRequest(
            idea="Create a CLI task tracker",
            project_name=project_name,
            template="cli",
            github_repository="owner/repo",
        )


def test_project_request_rejects_unsupported_template() -> None:
    with pytest.raises(ValueError, match="Unsupported MVP template"):
        MvpProjectRequest(
            idea="Create an API",
            project_name="task-tracker",
            template="fastapi",
            github_repository="owner/repo",
        )


def test_project_request_rejects_invalid_repository() -> None:
    with pytest.raises(ValueError, match="owner/repository"):
        MvpProjectRequest(
            idea="Create a CLI task tracker",
            project_name="task-tracker",
            template="cli",
            github_repository="owner-only",
        )


def test_run_state_transitions_are_explicitly_modeled() -> None:
    run = MvpRun(
        run_id="run-1",
        request=MvpProjectRequest(
            idea="Create a CLI task tracker",
            project_name="task-tracker",
            template="cli",
            github_repository="owner/repo",
        ),
    )

    for status in (
        MvpRunStatus.GENERATING,
        MvpRunStatus.VALIDATING,
        MvpRunStatus.TESTING,
        MvpRunStatus.READY_TO_PUBLISH,
        MvpRunStatus.PUBLISHING,
        MvpRunStatus.COMPLETED,
    ):
        run.transition_to(status)

    assert run.status is MvpRunStatus.COMPLETED


def test_run_can_reach_ready_to_publish_for_skip_publish() -> None:
    run = MvpRun(
        run_id="run-1",
        request=MvpProjectRequest(
            idea="Create a CLI task tracker",
            project_name="task-tracker",
            template="cli",
            github_repository="owner/repo",
        ),
    )

    for status in (
        MvpRunStatus.GENERATING,
        MvpRunStatus.VALIDATING,
        MvpRunStatus.TESTING,
        MvpRunStatus.READY_TO_PUBLISH,
    ):
        run.transition_to(status)

    assert run.status is MvpRunStatus.READY_TO_PUBLISH


def test_invalid_run_state_transition_is_rejected() -> None:
    run = MvpRun(
        run_id="run-1",
        request=MvpProjectRequest(
            idea="Create a CLI task tracker",
            project_name="task-tracker",
            template="cli",
            github_repository="owner/repo",
        ),
    )

    with pytest.raises(ValueError, match="created -> completed"):
        run.transition_to(MvpRunStatus.COMPLETED)


def test_inventory_and_results_are_structured() -> None:
    generated_file = GeneratedFile(
        path="README.md",
        sha256="0" * 64,
        size_bytes=123,
    )
    inventory = GeneratedProjectInventory(
        files=(generated_file,),
        inventory_hash="1" * 64,
    )
    check = CheckResult(name="required-files", passed=True, message="ok")
    publish = GitHubPublishResult(
        branch="slugger/generated-task-tracker-run-1",
        pull_request_url="https://github.com/owner/repo/pull/1",
    )

    run = MvpRun(
        run_id="run-1",
        request=MvpProjectRequest(
            idea="Create a CLI task tracker",
            project_name="task-tracker",
            template="cli",
            github_repository="owner/repo",
        ),
        inventory=inventory,
        validation_results=(check,),
        github_publish_result=publish,
    )

    assert run.inventory == inventory
    assert run.validation_results == (check,)
    assert run.github_publish_result == publish


def test_build_service_contract_can_be_implemented_without_external_services() -> None:
    class FakeBuildService:
        def build(self, request: MvpProjectRequest) -> MvpBuildResult:
            return MvpBuildResult(run=MvpRun(run_id="run-1", request=request))

    service = cast(MvpBuildService, FakeBuildService())
    request = MvpProjectRequest(
        idea="Create a CLI task tracker",
        project_name="task-tracker",
        template="cli",
        github_repository="owner/repo",
    )

    result = service.build(request)

    assert result.status is MvpRunStatus.CREATED
