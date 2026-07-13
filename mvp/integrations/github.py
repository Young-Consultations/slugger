"""GitHub draft pull-request publishing for generated MVP projects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess

from mvp.basic_runner import BasicRunnerResult
from mvp.models import CheckResult, GeneratedProjectInventory, GitHubPublishResult, MvpProjectRequest, MvpRun
from mvp.project_validator import ProjectValidator
from mvp.workspace import MvpWorkspace, WorkspaceManager


class GitHubPublishError(RuntimeError):
    """Raised when generated-project publishing is unsafe or fails."""


class MvpGitHubPublisher:
    """Interface for MVP GitHub publishing adapters."""

    def publish(
        self,
        run: MvpRun,
        workspace: MvpWorkspace | Path,
        validation_results: tuple[CheckResult, ...],
        runner_result: BasicRunnerResult,
    ) -> GitHubPublishResult:
        """Publish a validated and tested generated project as a draft pull request."""

        raise NotImplementedError


@dataclass
class FakeMvpGitHubPublisher(MvpGitHubPublisher):
    """Offline publisher with production idempotency and safety semantics."""

    fail: bool = False
    publish_count: int = 0

    def publish(
        self,
        run: MvpRun,
        workspace: MvpWorkspace | Path,
        validation_results: tuple[CheckResult, ...],
        runner_result: BasicRunnerResult,
    ) -> GitHubPublishResult:
        _ensure_publishable(validation_results, runner_result)
        if run.github_publish_result is not None:
            return GitHubPublishResult(
                branch=run.github_publish_result.branch,
                pull_request_url=run.github_publish_result.pull_request_url,
                draft=True,
                existing=True,
            )
        if self.fail:
            raise GitHubPublishError("Fake GitHub publication failed")
        self.publish_count += 1
        branch = branch_name(run.request, run.run_id)
        result = GitHubPublishResult(
            branch=branch,
            pull_request_url=f"https://github.com/{run.request.github_repository}/pull/{run.run_id}",
            draft=True,
            existing=False,
        )
        run.github_publish_result = result
        return result


class GitHubCliMvpPublisher(MvpGitHubPublisher):
    """Production publisher using local git plus the GitHub CLI."""

    def __init__(self, workspace_manager: WorkspaceManager, *, timeout_seconds: int = 120) -> None:
        self.workspace_manager = workspace_manager
        self.timeout_seconds = timeout_seconds

    def publish(
        self,
        run: MvpRun,
        workspace: MvpWorkspace | Path,
        validation_results: tuple[CheckResult, ...],
        runner_result: BasicRunnerResult,
    ) -> GitHubPublishResult:
        _ensure_publishable(validation_results, runner_result)
        if run.github_publish_result is not None:
            return GitHubPublishResult(run.github_publish_result.branch, run.github_publish_result.pull_request_url, True, True)
        workspace_path = self.workspace_manager._workspace_path(workspace)
        branch = branch_name(run.request, run.run_id)
        self._run(["gh", "repo", "view", run.request.github_repository, "--json", "name"], workspace_path)
        self._run(["git", "init"], workspace_path)
        self._run(["git", "remote", "add", "origin", f"https://github.com/{run.request.github_repository}.git"], workspace_path)
        self._run(["git", "fetch", "origin", run.request.base_branch, "--depth", "1"], workspace_path)
        self._run(["git", "checkout", "-B", branch, "FETCH_HEAD"], workspace_path)
        self._stage_inventory(workspace_path, run.inventory)
        self._run(["git", "commit", "-m", f"Add generated {run.request.project_name} project"], workspace_path)
        self._run(["git", "push", "-u", "origin", branch], workspace_path)
        body = pr_body(run, validation_results, runner_result)
        completed = self._run([
            "gh", "pr", "create", "--repo", run.request.github_repository, "--base", run.request.base_branch,
            "--head", branch, "--draft", "--title", f"Add generated {run.request.project_name} project", "--body", body,
        ], workspace_path)
        url = completed.stdout.strip().splitlines()[-1]
        result = GitHubPublishResult(branch=branch, pull_request_url=url, draft=True)
        run.github_publish_result = result
        return result

    def _stage_inventory(self, workspace_path: Path, inventory: GeneratedProjectInventory | None) -> None:
        if inventory is None:
            raise GitHubPublishError("Refusing to publish without a generated-file inventory")
        paths: list[str] = []
        for file in inventory.files:
            generated_path = self.workspace_manager.resolve_generated_path(workspace_path, file.path)
            if not generated_path.is_file():
                raise GitHubPublishError(f"Recorded generated file is missing: {file.path}")
            paths.append(file.path)
        self._run(["git", "add", "--", *paths], workspace_path)

    def _run(self, command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        executable = shutil.which(command[0])
        if executable is None:
            raise GitHubPublishError(f"Required command is not available: {command[0]}")
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=self.timeout_seconds, check=False)
        if completed.returncode != 0:
            raise GitHubPublishError(f"Command failed: {' '.join(command)}\n{completed.stderr[:1000]}")
        return completed


def branch_name(request: MvpProjectRequest, run_id: str) -> str:
    return f"slugger/generated-{request.project_name}-{run_id[:8]}"


def pr_body(run: MvpRun, validation_results: tuple[CheckResult, ...], runner_result: BasicRunnerResult) -> str:
    inventory_lines = []
    if run.inventory is not None:
        inventory_lines = [f"- `{file.path}` ({file.size_bytes} bytes)" for file in run.inventory.files]
    return "\n".join([
        f"Original idea: {run.request.idea}",
        f"Template: {run.request.template}",
        f"Validation: {_summary(validation_results)}",
        f"Tests: {_summary(runner_result.checks)}",
        f"Smoke: {_check_message(runner_result.checks, 'cli_smoke')}",
        "Generated-file inventory:",
        *(inventory_lines or ["- No inventory recorded"]),
        f"Codex prompt version: {run.prompt_version or 'unknown'}",
        f"Codex session ID: {run.codex_session_id or 'unknown'}",
        "Known limitations: Generated by the focused Slugger MVP path.",
    ])


def _ensure_publishable(validation_results: tuple[CheckResult, ...], runner_result: BasicRunnerResult) -> None:
    if not ProjectValidator.passed(validation_results):
        raise GitHubPublishError("Refusing to publish after failed validation")
    if not runner_result.passed:
        raise GitHubPublishError("Refusing to publish after failed generated-project tests")


def _summary(results: tuple[CheckResult, ...]) -> str:
    passed = sum(1 for result in results if result.passed)
    return f"{passed}/{len(results)} checks passed"


def _check_message(results: tuple[CheckResult, ...], name: str) -> str:
    for result in results:
        if result.name == name:
            return "passed" if result.passed else f"failed: {result.message}"
    return "not recorded"
