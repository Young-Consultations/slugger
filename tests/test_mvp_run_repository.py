from __future__ import annotations

import pytest

from mvp.models import (
    CheckResult,
    GitHubPublishResult,
    MvpProjectRequest,
    MvpRun,
    MvpRunStatus,
)
from mvp.run_repository import SQLiteMvpRunRepository


def _request() -> MvpProjectRequest:
    return MvpProjectRequest(
        idea="Create a CLI task tracker",
        project_name="task-tracker",
        template="cli",
        github_repository="owner/task-tracker",
    )


def test_run_survives_repository_reopen(tmp_path):
    db = tmp_path / "runs.sqlite3"
    repo = SQLiteMvpRunRepository(db)
    run = MvpRun("run-123", _request(), workspace_path=str(tmp_path / "workspace"))
    repo.create(run)

    reopened = SQLiteMvpRunRepository(db)
    loaded = reopened.require("run-123")

    assert loaded.run_id == "run-123"
    assert loaded.request.project_name == "task-tracker"
    assert loaded.workspace_path == str(tmp_path / "workspace")
    assert loaded.status == MvpRunStatus.CREATED


def test_state_transitions_and_error_details_are_persisted(tmp_path):
    repo = SQLiteMvpRunRepository(tmp_path / "runs.sqlite3")
    repo.create(MvpRun("run-123", _request()))

    generating = repo.transition("run-123", MvpRunStatus.GENERATING)
    failed = repo.transition(
        "run-123", MvpRunStatus.FAILED, error_details="Codex failed"
    )

    assert generating.status == MvpRunStatus.GENERATING
    assert failed.error_details == "Codex failed"
    assert repo.require("run-123").status == MvpRunStatus.FAILED


def test_invalid_status_transition_is_rejected(tmp_path):
    repo = SQLiteMvpRunRepository(tmp_path / "runs.sqlite3")
    repo.create(MvpRun("run-123", _request()))
    run = repo.require("run-123")
    run.status = MvpRunStatus.COMPLETED

    with pytest.raises(ValueError, match="Invalid MVP run transition"):
        repo.save(run)


def test_completed_run_retains_github_information(tmp_path):
    repo = SQLiteMvpRunRepository(tmp_path / "runs.sqlite3")
    run = MvpRun("run-123", _request())
    run.status = MvpRunStatus.COMPLETED
    run.validation_results = (CheckResult("validation", True),)
    run.test_results = (CheckResult("cli_smoke", True),)
    run.github_publish_result = GitHubPublishResult(
        branch="slugger/generated-task-tracker-run-123",
        pull_request_url="https://github.com/owner/task-tracker/pull/1",
    )
    repo.create(run)

    loaded = repo.require("run-123")

    assert loaded.github_publish_result is not None
    assert (
        loaded.github_publish_result.branch == "slugger/generated-task-tracker-run-123"
    )
    assert loaded.github_publish_result.pull_request_url.endswith("/pull/1")
