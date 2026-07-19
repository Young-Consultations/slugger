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
    return BasicRunnerResult(
        (
            CheckResult("run_tests", passed),
            CheckResult("cli_smoke", passed),
        )
    )


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
    assert (
        branch_name(_request(), "1234567890")
        == "slugger/generated-task-tracker-12345678"
    )


class RecordingGitHubCliPublisher(GitHubCliMvpPublisher):
    def __init__(self, workspace_manager: WorkspaceManager) -> None:
        super().__init__(workspace_manager)
        self.commands: list[list[str]] = []

    def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
        self.commands.append(command)
        if command[:4] == ["gh", "repo", "view", "owner/task-tracker"]:
            stdout = '{"viewerPermission":"WRITE","defaultBranchRef":{"name":"main"}}'
        elif command[:2] == ["git", "ls-remote"]:
            stdout = "sha\trefs/heads/main\n"
        elif command[:3] == ["gh", "pr", "create"]:
            stdout = "https://github.com/owner/task-tracker/pull/1\n"
        else:
            stdout = ""
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")


def test_cli_publisher_stages_only_recorded_inventory_files(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    (workspace.path / "pyproject.toml").write_text(
        "[project]\nname = 'task-tracker'\n", encoding="utf-8"
    )
    (workspace.path / ".venv").mkdir()
    (workspace.path / ".venv" / "artifact.py").write_text(
        "runner artifact", encoding="utf-8"
    )
    (workspace.path / ".pytest_cache").mkdir()
    (workspace.path / ".pytest_cache" / "README.md").write_text(
        "cache", encoding="utf-8"
    )
    run = _run()
    run.inventory = GeneratedProjectInventory(
        files=(
            GeneratedFile("README.md", "a" * 64, 16),
            GeneratedFile("pyproject.toml", "b" * 64, 32),
        ),
        inventory_hash="c" * 64,
    )
    publisher = RecordingGitHubCliPublisher(workspace_manager)

    publisher.publish(run, workspace, _validation(), _runner())

    add_commands = [
        command for command in publisher.commands if command[:3] == ["git", "add", "--"]
    ]
    assert add_commands == [["git", "add", "--", "README.md", "pyproject.toml"]]
    assert all(
        ".venv" not in command and ".pytest_cache" not in command
        for command in add_commands[0]
    )


def test_cli_publisher_rejects_missing_inventory(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    run = _run()
    run.inventory = None
    publisher = RecordingGitHubCliPublisher(workspace_manager)

    with pytest.raises(GitHubPublishError, match="without a generated-file inventory"):
        publisher.publish(run, workspace, _validation(), _runner())


class ExistingPrGitHubCliPublisher(GitHubCliMvpPublisher):
    def __init__(self, workspace_manager: WorkspaceManager) -> None:
        super().__init__(workspace_manager)
        self.commands: list[list[str]] = []

    def _find_pr(self, repository: str, branch: str):  # type: ignore[no-untyped-def]
        return {
            "url": "https://github.com/owner/task-tracker/pull/7",
            "number": 7,
            "isDraft": True,
        }

    def _remote_branch_sha(self, repository: str, branch: str, cwd):  # type: ignore[no-untyped-def]
        return "remote-sha"

    def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
        self.commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")


def test_cli_publisher_reuses_existing_pr_without_saved_publish_metadata(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    run = _run()
    publisher = ExistingPrGitHubCliPublisher(workspace_manager)

    result = publisher.publish(run, workspace, _validation(), _runner())

    assert result.pull_request_url == "https://github.com/owner/task-tracker/pull/7"
    assert result.pull_request_number == 7
    assert result.commit_sha == "remote-sha"
    assert result.existing is True
    assert not any(command[:2] == ["git", "push"] for command in publisher.commands)
    assert not any(
        command[:3] == ["gh", "pr", "create"] for command in publisher.commands
    )


class FailingCommandGitHubCliPublisher(GitHubCliMvpPublisher):
    def __init__(
        self, workspace_manager: WorkspaceManager, failing_prefix: list[str]
    ) -> None:
        super().__init__(workspace_manager)
        self.failing_prefix = failing_prefix

    def _find_pr(self, repository: str, branch: str):  # type: ignore[no-untyped-def]
        return None

    def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
        if (
            self.failing_prefix
            and command[: len(self.failing_prefix)] == self.failing_prefix
        ):
            completed = subprocess.CompletedProcess(
                command, 1, stdout="", stderr="remote: denied token-secret"
            )
            diagnostic = __import__(
                "mvp.integrations.github",
                fromlist=[
                    "PublicationCommandDiagnostic",
                    "_phase_for_command",
                    "_sanitize_command",
                    "_bounded",
                ],
            )
            self.diagnostics.append(
                diagnostic.PublicationCommandDiagnostic(
                    phase=diagnostic._phase_for_command(command),
                    command=diagnostic._sanitize_command(command),
                    return_code=1,
                    repository=self._active_repository,
                    branch=self._active_branch,
                    stdout="",
                    stderr=diagnostic._bounded(completed.stderr),
                )
            )
            if check:
                raise GitHubPublishError("simulated publication failure")
            return completed
        if command[:4] == ["gh", "repo", "view", "owner/task-tracker"]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout='{"viewerPermission":"WRITE","defaultBranchRef":{"name":"main"}}',
                stderr="",
            )
        if command[:2] == ["git", "ls-remote"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="sha\trefs/heads/main\n", stderr=""
            )
        if command[:2] == ["git", "status"]:
            return subprocess.CompletedProcess(
                command, 0, stdout=" M README.md\n", stderr=""
            )
        if command[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="commit-sha\n", stderr=""
            )
        if command[:3] == ["gh", "pr", "create"]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="https://github.com/owner/task-tracker/pull/1\n",
                stderr="",
            )
        if command[:3] == ["gh", "pr", "list"]:
            return subprocess.CompletedProcess(command, 0, stdout="[]", stderr="")
        if command[:3] == [
            "gh",
            "api",
            "repos/owner/task-tracker/git/ref/heads/slugger/generated-task-tracker-abcdef12",
        ]:
            return subprocess.CompletedProcess(
                command, 1, stdout="", stderr="not found"
            )
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")


def test_cli_publisher_rejects_read_only_token_before_push(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    run = _run()

    class ReadOnlyPublisher(FailingCommandGitHubCliPublisher):
        def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
            if command[:4] == ["gh", "repo", "view", "owner/task-tracker"]:
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout='{"viewerPermission":"READ","defaultBranchRef":{"name":"main"}}',
                    stderr="",
                )
            return super()._run(command, cwd, check=check)

    with pytest.raises(GitHubPublishError, match="does not have push access"):
        ReadOnlyPublisher(workspace_manager, []).publish(
            run, workspace, _validation(), _runner()
        )


def test_cli_publisher_rejects_missing_base_branch_before_push(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")

    class MissingBasePublisher(FailingCommandGitHubCliPublisher):
        def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
            if command[:2] == ["git", "ls-remote"]:
                return subprocess.CompletedProcess(
                    command, 2, stdout="", stderr="not found"
                )
            return super()._run(command, cwd, check=check)

    with pytest.raises(GitHubPublishError, match="base branch 'main' does not exist"):
        MissingBasePublisher(workspace_manager, []).publish(
            _run(), workspace, _validation(), _runner()
        )


def test_cli_publisher_records_failed_push_diagnostics(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "token-secret")
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    publisher = FailingCommandGitHubCliPublisher(workspace_manager, ["git", "push"])

    with pytest.raises(GitHubPublishError, match="simulated publication failure"):
        publisher.publish(_run(), workspace, _validation(), _runner())

    failed = publisher.diagnostics[-1]
    assert failed.phase == "push_generated_branch"
    assert failed.repository == "owner/task-tracker"
    assert failed.branch == "slugger/generated-task-tracker-abcdef12"
    assert "token-secret" not in failed.stderr


def test_cli_publisher_records_failed_pr_creation_diagnostics(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    publisher = FailingCommandGitHubCliPublisher(
        workspace_manager, ["gh", "pr", "create"]
    )

    with pytest.raises(GitHubPublishError, match="simulated publication failure"):
        publisher.publish(_run(), workspace, _validation(), _runner())

    assert publisher.diagnostics[-1].phase == "create_draft_pull_request"
