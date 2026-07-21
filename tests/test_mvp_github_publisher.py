from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path

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

    assert first.branch == branch_name(_request(), None)
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


def test_branch_name_uses_deterministic_publication_identity():
    assert (
        branch_name(_request(), "1234567890")
        == "slugger/generated-task-tracker-165b46bd7115"
    )
    other = MvpProjectRequest(
        idea="Different idea",
        project_name="task-tracker",
        template="cli",
        github_repository="owner/task-tracker",
        base_branch="main",
    )
    assert branch_name(other) != branch_name(_request())


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
            "headRefName": branch,
            "baseRefName": "main",
            "body": pr_body(_run(), _validation(), _runner()),
        }

    def _remote_branch_sha(self, repository: str, branch: str, cwd):  # type: ignore[no-untyped-def]
        return "remote-sha"

    def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
        self.commands.append(command)
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
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")


def test_cli_publisher_reuses_existing_pr_without_saved_publish_metadata(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    run = _run()
    publisher = ExistingPrGitHubCliPublisher(workspace_manager)

    result = publisher.publish(run, workspace, _validation(), _runner())

    assert result.pull_request_url == "https://github.com/owner/task-tracker/pull/7"
    assert result.pull_request_number == 7
    assert result.commit_sha == "remote-sha"
    assert result.existing is True
    assert any(command[:3] == ["gh", "pr", "edit"] for command in publisher.commands)
    assert not any(
        command[:3] == ["gh", "pr", "create"] for command in publisher.commands
    )


def test_cli_publisher_preserves_generated_inventory_before_existing_branch_checkout(
    tmp_path,
):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text(
        "fresh generated readme", encoding="utf-8"
    )
    run = _run()

    class OverwritingCheckoutPublisher(ExistingPrGitHubCliPublisher):
        def __init__(self, workspace_manager: WorkspaceManager) -> None:
            super().__init__(workspace_manager)
            self.checkout_cwds = []

        def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
            completed = super()._run(command, cwd, check=check)
            if command[:3] == ["git", "checkout", "-B"]:
                self.checkout_cwds.append(cwd)
                (cwd / "README.md").write_text("old branch readme", encoding="utf-8")
            return completed

    publisher = OverwritingCheckoutPublisher(workspace_manager)

    publisher.publish(run, workspace, _validation(), _runner())

    assert (workspace.path / "README.md").read_text(encoding="utf-8") == (
        "fresh generated readme"
    )
    assert ["git", "add", "--", "README.md"] in publisher.commands
    assert publisher.checkout_cwds
    assert workspace.path not in publisher.checkout_cwds


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
        if command[:2] == ["gh", "api"] and command[2].startswith(
            "repos/owner/task-tracker/git/ref/heads/slugger/generated-task-tracker-"
        ):
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
        def __init__(self, workspace_manager: WorkspaceManager) -> None:
            super().__init__(workspace_manager, [])
            self.commands: list[list[str]] = []

        def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
            self.commands.append(command)
            if command[:2] == ["git", "ls-remote"]:
                return subprocess.CompletedProcess(
                    command, 2, stdout="", stderr="not found"
                )
            return super()._run(command, cwd, check=check)

    publisher = MissingBasePublisher(workspace_manager)

    with pytest.raises(GitHubPublishError, match="base branch 'main' does not exist"):
        publisher.publish(_run(), workspace, _validation(), _runner())

    remote_config_index = next(
        index
        for index, command in enumerate(publisher.commands)
        if command[:3] == ["git", "remote", "add"]
    )
    base_check_index = next(
        index
        for index, command in enumerate(publisher.commands)
        if command[:2] == ["git", "ls-remote"]
    )
    assert remote_config_index < base_check_index


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
    assert failed.branch == branch_name(_request(), None)
    assert "token-secret" not in failed.stderr


def test_cli_publisher_records_failed_pr_creation_diagnostics(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    publisher = FailingCommandGitHubCliPublisher(
        workspace_manager, ["gh", "pr", "create"]
    )

    with pytest.raises(GitHubPublishError, match="race recovery"):
        publisher.publish(_run(), workspace, _validation(), _runner())

    assert any(
        diagnostic.phase == "create_draft_pull_request"
        for diagnostic in publisher.diagnostics
    )


def test_fake_publisher_reuses_one_draft_for_independent_runs(tmp_path):
    first = _run()
    first.run_id = "111111111111"
    second = _run()
    second.run_id = "222222222222"
    second.inventory = GeneratedProjectInventory(
        files=(GeneratedFile("README.md", "d" * 64, 20),), inventory_hash="e" * 64
    )
    publisher = FakeMvpGitHubPublisher()

    first_result = publisher.publish(first, tmp_path, _validation(), _runner())
    second_result = publisher.publish(second, tmp_path, _validation(), _runner())

    assert first_result.branch == second_result.branch
    assert first_result.pull_request_url == second_result.pull_request_url
    assert second_result.existing is True
    assert second_result.commit_sha == "fake-222222222222"
    assert publisher.publish_count == 1


def test_cli_publisher_detects_duplicate_matching_drafts(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    run = _run()
    body = pr_body(run, _validation(), _runner())

    class DuplicatePublisher(RecordingGitHubCliPublisher):
        def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
            self.commands.append(command)
            if command[:3] == ["gh", "pr", "list"] and "--head" not in command:
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout=(
                        '[{"number":1,"url":"https://github.com/owner/task-tracker/pull/1",'
                        '"isDraft":true,"headRefName":"slugger/generated-task-tracker-old1",'
                        '"baseRefName":"main","body":'
                        + __import__("json").dumps(body)
                        + '},{"number":2,"url":"https://github.com/owner/task-tracker/pull/2",'
                        '"isDraft":true,"headRefName":"slugger/generated-task-tracker-old2",'
                        '"baseRefName":"main","body":'
                        + __import__("json").dumps(body)
                        + "}]"
                    ),
                    stderr="",
                )
            if command[:3] == ["gh", "pr", "list"]:
                return subprocess.CompletedProcess(command, 0, stdout="[]", stderr="")
            return super()._run(command, cwd, check=check)

    publisher = DuplicatePublisher(workspace_manager)

    with pytest.raises(GitHubPublishError, match="Multiple open Slugger draft"):
        publisher.publish(run, workspace, _validation(), _runner())

    assert not any(
        command[:3] == ["gh", "pr", "create"] for command in publisher.commands
    )


def test_cli_publisher_removes_stale_slugger_inventory_only(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    run = _run()
    old_run = _run()
    old_run.inventory = GeneratedProjectInventory(
        files=(
            GeneratedFile("README.md", "a" * 64, 10),
            GeneratedFile("stale.txt", "f" * 64, 5),
        ),
        inventory_hash="9" * 64,
    )
    existing = {
        "url": "https://github.com/owner/task-tracker/pull/7",
        "number": 7,
        "isDraft": True,
        "headRefName": branch_name(run.request, run.prompt_hash),
        "baseRefName": "main",
        "body": pr_body(old_run, _validation(), _runner()),
    }

    class StalePublisher(ExistingPrGitHubCliPublisher):
        def _find_pr(self, repository: str, branch: str):  # type: ignore[no-untyped-def]
            return existing

    publisher = StalePublisher(workspace_manager)
    publisher.publish(run, workspace, _validation(), _runner())

    assert ["git", "rm", "-f", "--", "stale.txt"] in publisher.commands
    assert not any("untracked.txt" in command for command in publisher.commands)


def test_cli_publisher_recovers_create_race_by_reusing_draft(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    run = _run()
    body = pr_body(run, _validation(), _runner())

    class RacePublisher(FailingCommandGitHubCliPublisher):
        def __init__(self, workspace_manager: WorkspaceManager) -> None:
            super().__init__(workspace_manager, ["gh", "pr", "create"])
            self.created = False

        def _remote_branch_sha(self, repository: str, branch: str, cwd):  # type: ignore[no-untyped-def]
            return "remote-sha" if self.created else None

        def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
            if command[:3] == ["gh", "pr", "create"]:
                self.created = True
                return subprocess.CompletedProcess(
                    command, 1, stdout="", stderr="already exists"
                )
            if (
                self.created
                and command[:3] == ["gh", "pr", "list"]
                and "--head" not in command
            ):
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout='[{"number":8,"url":"https://github.com/owner/task-tracker/pull/8","isDraft":true,"headRefName":"'
                    + branch_name(run.request, run.prompt_hash)
                    + '","baseRefName":"main","body":'
                    + __import__("json").dumps(body)
                    + "}]",
                    stderr="",
                )
            return super()._run(command, cwd, check=check)

    publisher = RacePublisher(workspace_manager)
    result = publisher.publish(run, workspace, _validation(), _runner())

    assert result.existing is True
    assert result.pull_request_number == 8


def test_cli_publisher_rejects_symlink_inventory_artifact(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "target.txt").write_text("target", encoding="utf-8")
    (workspace.path / "README.md").symlink_to(workspace.path / "target.txt")
    publisher = RecordingGitHubCliPublisher(workspace_manager)

    with pytest.raises(GitHubPublishError, match="must not be a symlink"):
        publisher.publish(_run(), workspace, _validation(), _runner())


class PublicationWorkspaceRecordingPublisher(ExistingPrGitHubCliPublisher):
    def __init__(self, workspace_manager: WorkspaceManager) -> None:
        super().__init__(workspace_manager)
        self.publication_cwds = []

    def _prepare_git(self, workspace_path, repository):  # type: ignore[no-untyped-def]
        self.publication_cwds.append(workspace_path)
        return super()._prepare_git(workspace_path, repository)


def test_cli_publisher_cleans_publication_workspace_after_success(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    publisher = PublicationWorkspaceRecordingPublisher(workspace_manager)

    publisher.publish(_run(), workspace, _validation(), _runner())

    assert publisher.publication_cwds
    assert all(not path.exists() for path in publisher.publication_cwds)


def test_cli_publisher_cleans_publication_workspace_after_failure(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")

    class FailingAfterPreparePublisher(PublicationWorkspaceRecordingPublisher):
        def _run(self, command: list[str], cwd, *, check: bool = True):  # type: ignore[no-untyped-def]
            if command[:2] == ["git", "fetch"]:
                raise GitHubPublishError("simulated fetch failure")
            return super()._run(command, cwd, check=check)

    publisher = FailingAfterPreparePublisher(workspace_manager)

    with pytest.raises(GitHubPublishError, match="simulated fetch failure"):
        publisher.publish(_run(), workspace, _validation(), _runner())

    assert publisher.publication_cwds
    assert all(not path.exists() for path in publisher.publication_cwds)


def test_publication_marker_uses_organization_target_repository() -> None:
    from mvp.integrations.github import (
        parse_publication_marker,
        publication_identity,
        publication_marker,
    )

    run = _run()
    run.request = replace(
        run.request, github_repository="Young-Consultations/slugger-generated-demos"
    )
    identity = publication_identity(run.request, run.prompt_hash)

    marker = parse_publication_marker(publication_marker(run, identity))

    assert marker["repository"] == "Young-Consultations/slugger-generated-demos"
    assert marker["publication_identity"] == identity


def test_former_namespace_marker_is_not_organization_owned() -> None:
    from mvp.integrations.github import publication_identity, publication_marker

    run = _run()
    run.request = replace(
        run.request, github_repository="Young-Consultations/slugger-generated-demos"
    )
    identity = publication_identity(run.request, run.prompt_hash)
    old_run = _run()
    old_run.request = replace(
        old_run.request, github_repository="mighty" + "joe909/slugger-generated-demos"
    )
    old_body = publication_marker(old_run, identity)
    publisher = RecordingGitHubCliPublisher(WorkspaceManager(Path("/tmp") / "unused"))

    assert not publisher._valid_slugger_pr(
        run,
        branch_name(run.request, run.prompt_hash),
        identity,
        {
            "isDraft": True,
            "headRefName": branch_name(run.request, run.prompt_hash),
            "baseRefName": "main",
            "body": old_body,
        },
    )


def test_publication_identity_is_independent_of_run_id() -> None:
    from mvp.integrations.github import publication_identity

    first = _run()
    first.run_id = "111"
    second = _run()
    second.run_id = "222"

    assert publication_identity(
        first.request, first.prompt_hash
    ) == publication_identity(second.request, second.prompt_hash)


def test_cli_publisher_fails_closed_on_mismatched_repository_marker(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    run = _run()
    from mvp.integrations.github import publication_identity

    branch = branch_name(run.request, run.prompt_hash)
    identity = publication_identity(run.request, run.prompt_hash)
    old_run = _run()
    old_run.request = replace(
        old_run.request, github_repository="other-owner/task-tracker"
    )
    publisher = RecordingGitHubCliPublisher(workspace_manager)

    assert not publisher._valid_slugger_pr(
        run,
        branch,
        identity,
        {
            "isDraft": True,
            "headRefName": branch,
            "baseRefName": "main",
            "body": pr_body(old_run, _validation(), _runner()),
        },
    )


def test_cli_publisher_rejects_matching_non_draft_pr(tmp_path):
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = workspace_manager.create_workspace("run-1")
    (workspace.path / "README.md").write_text("generated readme", encoding="utf-8")
    run = _run()

    class NonDraftPublisher(ExistingPrGitHubCliPublisher):
        def _find_pr(self, repository: str, branch: str):  # type: ignore[no-untyped-def]
            pr = super()._find_pr(repository, branch)
            pr["isDraft"] = False
            return pr

    publisher = NonDraftPublisher(workspace_manager)

    with pytest.raises(GitHubPublishError, match="not draft"):
        publisher.publish(run, workspace, _validation(), _runner())

    assert not any(
        command[:3] == ["gh", "pr", "create"] for command in publisher.commands
    )
