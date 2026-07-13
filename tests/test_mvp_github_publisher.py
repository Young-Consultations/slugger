from __future__ import annotations

import pytest

from mvp.basic_runner import BasicRunnerResult
from mvp.integrations.github import FakeMvpGitHubPublisher, GitHubPublishError, branch_name, pr_body
from mvp.models import CheckResult, GeneratedFile, GeneratedProjectInventory, MvpProjectRequest, MvpRun


def _request() -> MvpProjectRequest:
    return MvpProjectRequest(
        idea="Create a CLI task tracker with add, list, and done commands",
        project_name="task-tracker",
        template="cli",
        github_repository="owner/task-tracker",
        base_branch="main",
    )


def _run() -> MvpRun:
    run = MvpRun("abcdef123456", _request())
    run.codex_session_id = "session-123"
    run.prompt_version = "python_project_v1"
    run.inventory = GeneratedProjectInventory(
        files=(GeneratedFile("README.md", "a" * 64, 10),),
        inventory_hash="b" * 64,
    )
    return run


def _validation(passed: bool = True) -> tuple[CheckResult, ...]:
    return (CheckResult("required_files", passed),)


def _runner(passed: bool = True) -> BasicRunnerResult:
    return BasicRunnerResult((CheckResult("run_tests", passed), CheckResult("cli_smoke", passed),))


def test_fake_publisher_creates_one_draft_pr_and_is_idempotent(tmp_path):
    run = _run()
    publisher = FakeMvpGitHubPublisher()

    first = publisher.publish(run, tmp_path, _validation(), _runner())
    second = publisher.publish(run, tmp_path, _validation(), _runner())

    assert first.branch == "slugger/generated-task-tracker-abcdef12"
    assert first.draft is True
    assert first.existing is False
    assert second.pull_request_url == first.pull_request_url
    assert second.existing is True
    assert publisher.publish_count == 1


def test_failed_validation_creates_no_branch(tmp_path):
    publisher = FakeMvpGitHubPublisher()

    with pytest.raises(GitHubPublishError, match="failed validation"):
        publisher.publish(_run(), tmp_path, _validation(False), _runner())

    assert publisher.publish_count == 0


def test_failed_tests_create_no_branch(tmp_path):
    publisher = FakeMvpGitHubPublisher()

    with pytest.raises(GitHubPublishError, match="failed generated-project tests"):
        publisher.publish(_run(), tmp_path, _validation(), _runner(False))

    assert publisher.publish_count == 0


def test_github_failure_leaves_run_publish_result_empty(tmp_path):
    run = _run()
    publisher = FakeMvpGitHubPublisher(fail=True)

    with pytest.raises(GitHubPublishError, match="Fake GitHub publication failed"):
        publisher.publish(run, tmp_path, _validation(), _runner())

    assert run.github_publish_result is None


def test_pr_body_includes_required_audit_sections():
    body = pr_body(_run(), _validation(), _runner())

    assert "Original idea: Create a CLI task tracker" in body
    assert "Template: cli" in body
    assert "Validation: 1/1 checks passed" in body
    assert "Tests: 2/2 checks passed" in body
    assert "Smoke: passed" in body
    assert "`README.md`" in body
    assert "Codex prompt version: python_project_v1" in body
    assert "Codex session ID: session-123" in body
    assert "Known limitations:" in body


def test_branch_name_uses_project_and_short_run_id():
    assert branch_name(_request(), "1234567890") == "slugger/generated-task-tracker-12345678"
