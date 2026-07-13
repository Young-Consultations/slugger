from __future__ import annotations

import subprocess

import pytest

from mvp.basic_runner import BasicRunnerResult
from mvp.integrations.github import (
    FakeMvpGitHubPublisher,
    GitHubCliMvpPublisher,
    GitHubPublishError,
    branch_name,
    pr_body,
)
from mvp.models import (
    CheckResult,
    GeneratedFile,
    GeneratedProjectInventory,
    MvpProjectRequest,
    MvpRun,
)
from mvp.workspace import WorkspaceManager


class RecordingGitHubCliPublisher(GitHubCliMvpPublisher):
    def __init__(self, workspace_manager: WorkspaceManager) -> None:
        super().__init__(workspace_manager)
        self.commands: list[list[str]] = []

    def _run(self, command: list[str], cwd):  # type: ignore[override]
        self.commands.append(command)
        stdout = (
            "https://github.com/owner/task-tracker/pull/123\n"
            if command[:3] == ["gh", "pr", "create"]
            else ""
        )
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")


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


def test_cli_publisher_stages_only_recorded_generated_files(tmp_path):
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("abcdef123456")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    (workspace.path / ".pytest_cache").mkdir()
    (workspace.path / ".pytest_cache" / "README.md").write_text("runner cache", encoding="utf-8")
    (workspace.path / ".venv").mkdir()
    (workspace.path / ".venv" / "pyvenv.cfg").write_text("runner venv", encoding="utf-8")
    run = _run()
    publisher = RecordingGitHubCliPublisher(manager)

    result = publisher.publish(run, workspace, _validation(), _runner())

    assert result.pull_request_url == "https://github.com/owner/task-tracker/pull/123"
    assert ["git", "add", "."] not in publisher.commands
    assert ["git", "add", "--", "README.md"] in publisher.commands
    add_command = next(command for command in publisher.commands if command[:3] == ["git", "add", "--"])
    assert ".venv/pyvenv.cfg" not in add_command
    assert ".pytest_cache/README.md" not in add_command


def test_cli_publisher_requires_recorded_inventory(tmp_path):
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("abcdef123456")
    run = _run()
    run.inventory = None
    publisher = RecordingGitHubCliPublisher(manager)

    with pytest.raises(GitHubPublishError, match="without a generated-file inventory"):
        publisher.publish(run, workspace, _validation(), _runner())
