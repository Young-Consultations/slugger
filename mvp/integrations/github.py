"""GitHub draft pull-request publishing for generated MVP projects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import shutil
import os
import subprocess

from mvp.basic_runner import BasicRunnerResult
from mvp.models import (
    CheckResult,
    GeneratedProjectInventory,
    GitHubPublishResult,
    MvpProjectRequest,
    MvpRun,
)
from mvp.project_validator import ProjectValidator
from mvp.workspace import MvpWorkspace, WorkspaceManager


@dataclass(frozen=True)
class PublicationCommandDiagnostic:
    """Sanitized bounded diagnostics for one publication command."""

    phase: str
    command: str
    return_code: int
    repository: str | None
    branch: str | None
    stdout: str
    stderr: str


def _bounded(value: str, limit: int = 4000) -> str:
    value = _sanitize(value)
    if len(value) <= limit:
        return value
    return value[:limit] + "\n...[truncated]"


def _sanitize(value: str) -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    if token:
        value = value.replace(token, "[REDACTED]")
    value = value.replace("https://x-access-token:", "https://[REDACTED]:")
    return value


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
                commit_sha=run.github_publish_result.commit_sha,
                pull_request_number=run.github_publish_result.pull_request_number,
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
            commit_sha="fake-" + run.run_id[:12],
            pull_request_number=1,
        )
        run.github_publish_result = result
        return result


class GitHubCliMvpPublisher(MvpGitHubPublisher):
    """Production publisher using local git plus the GitHub CLI.

    The publisher is intentionally idempotent: it reuses the deterministic branch
    and any open PR for that branch, and it persists enough metadata for a
    restarted process to finish missing publish steps without duplicating PRs.
    """

    def __init__(
        self, workspace_manager: WorkspaceManager, *, timeout_seconds: int = 120
    ) -> None:
        self.workspace_manager = workspace_manager
        self.timeout_seconds = timeout_seconds
        self.diagnostics: list[PublicationCommandDiagnostic] = []
        self._active_repository: str | None = None
        self._active_branch: str | None = None

    def publish(
        self,
        run: MvpRun,
        workspace: MvpWorkspace | Path,
        validation_results: tuple[CheckResult, ...],
        runner_result: BasicRunnerResult,
    ) -> GitHubPublishResult:
        _ensure_publishable(validation_results, runner_result)
        workspace_path = self.workspace_manager._workspace_path(workspace)
        branch = branch_name(run.request, run.run_id)
        self.diagnostics = []
        self._active_repository = run.request.github_repository
        self._active_branch = branch
        existing_pr = self._find_pr(run.request.github_repository, branch)
        if existing_pr is not None:
            return self._result_from_existing_pr(
                run, branch, existing_pr, workspace_path
            )

        self._verify_repo(run.request.github_repository, workspace_path)
        base_branch = self._resolve_base_branch(run, workspace_path)
        self._prepare_git(workspace_path, run.request.github_repository)
        remote_sha = self._remote_branch_sha(
            run.request.github_repository, branch, workspace_path
        )
        commit_sha: str | None
        if remote_sha is not None:
            self._run(
                [
                    "git",
                    "fetch",
                    "origin",
                    f"refs/heads/{branch}:refs/remotes/origin/{branch}",
                    "--depth",
                    "1",
                ],
                workspace_path,
            )
            self._verify_remote_inventory_tree(workspace_path, run, f"origin/{branch}")
            existing_pr = self._find_pr(run.request.github_repository, branch)
            if existing_pr is not None:
                return self._result_from_existing_pr(
                    run, branch, existing_pr, workspace_path
                )
            commit_sha = remote_sha
        else:
            self._run(
                ["git", "fetch", "origin", base_branch, "--depth", "1"], workspace_path
            )
            self._validate_target_repository(workspace_path, run)
            self._run(["git", "checkout", "-B", branch, "FETCH_HEAD"], workspace_path)
            self._stage_inventory(workspace_path, run.inventory)
            status = self._run(["git", "status", "--porcelain"], workspace_path).stdout
            if not status.strip():
                commit_sha = self._remote_branch_sha(
                    run.request.github_repository, branch, workspace_path
                )
            else:
                self._run(
                    [
                        "git",
                        "commit",
                        "-m",
                        f"Add generated {run.request.project_name} project",
                    ],
                    workspace_path,
                )
                commit_sha = self._run(
                    ["git", "rev-parse", "HEAD"], workspace_path
                ).stdout.strip()
            self._run(["git", "push", "-u", "origin", branch], workspace_path)
        existing_pr = self._find_pr(run.request.github_repository, branch)
        pr_existed_before_create = existing_pr is not None
        if existing_pr is None:
            body = pr_body(run, validation_results, runner_result)
            completed = self._run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--repo",
                    run.request.github_repository,
                    "--base",
                    base_branch,
                    "--head",
                    branch,
                    "--draft",
                    "--title",
                    f"Add generated {run.request.project_name} project",
                    "--body",
                    body,
                ],
                workspace_path,
            )
            url = completed.stdout.strip().splitlines()[-1]
            existing_pr = self._find_pr(run.request.github_repository, branch) or {
                "url": url,
                "number": 0,
                "isDraft": True,
            }
        if not bool(existing_pr.get("isDraft", True)):
            raise GitHubPublishError("Published pull request is not draft")
        result = GitHubPublishResult(
            branch=branch,
            pull_request_url=str(existing_pr["url"]),
            draft=True,
            existing=pr_existed_before_create,
            commit_sha=commit_sha,
            pull_request_number=int(str(existing_pr.get("number", 0))) or None,
        )
        run.github_publish_result = result
        return result

    def _result_from_existing_pr(
        self, run: MvpRun, branch: str, existing_pr: dict[str, object], cwd: Path
    ) -> GitHubPublishResult:
        if not bool(existing_pr.get("isDraft", True)):
            raise GitHubPublishError("Existing pull request is not draft")
        commit_sha = (
            run.github_publish_result.commit_sha
            if run.github_publish_result is not None
            else self._remote_branch_sha(run.request.github_repository, branch, cwd)
        )
        return GitHubPublishResult(
            branch=branch,
            pull_request_url=str(existing_pr["url"]),
            draft=True,
            existing=True,
            commit_sha=commit_sha,
            pull_request_number=int(str(existing_pr["number"])),
        )

    def _verify_remote_inventory_tree(
        self, workspace_path: Path, run: MvpRun, treeish: str
    ) -> None:
        if run.inventory is None:
            raise GitHubPublishError(
                "Refusing to publish without a generated-file inventory"
            )
        for file in run.inventory.files:
            completed = self._run(
                ["git", "show", f"{treeish}:{file.path}"], workspace_path, check=False
            )
            if completed.returncode != 0:
                raise GitHubPublishError(
                    f"Remote generated branch is missing recorded file: {file.path}"
                )
            import hashlib

            if (
                hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest()
                != file.sha256
            ):
                raise GitHubPublishError(
                    "Remote generated branch tree does not match persisted inventory"
                )

    def _verify_repo(self, repository: str, cwd: Path) -> None:
        raw = self._run(
            [
                "gh",
                "repo",
                "view",
                repository,
                "--json",
                "name,defaultBranchRef,viewerPermission",
            ],
            cwd,
        ).stdout
        data = json.loads(raw or "{}")
        if data.get("viewerPermission") not in {"ADMIN", "MAINTAIN", "WRITE"}:
            raise GitHubPublishError(
                "SLUGGER_GITHUB_TOKEN can read the target repository but does not have push access"
            )

    def _resolve_base_branch(self, run: MvpRun, cwd: Path) -> str:
        base = run.request.base_branch
        if base == "default":
            raw = self._run(
                [
                    "gh",
                    "repo",
                    "view",
                    run.request.github_repository,
                    "--json",
                    "defaultBranchRef",
                ],
                cwd,
            ).stdout
            data = json.loads(raw or "{}")
            default_ref = data.get("defaultBranchRef") or {}
            if not default_ref.get("name"):
                raise GitHubPublishError(
                    "Target repository has no default/base branch; initialize the sandbox repository with an initial commit on main before running Codex generation."
                )
            return str(default_ref["name"])
        exists = self._run(
            ["git", "ls-remote", "--exit-code", "--heads", "origin", base],
            cwd,
            check=False,
        )
        if exists.returncode != 0:
            raise GitHubPublishError(
                f"Target base branch {base!r} does not exist; initialize the sandbox repository with an initial commit or choose an existing base branch before running Codex generation."
            )
        return base

    def _prepare_git(self, workspace_path: Path, repository: str) -> None:
        if not (workspace_path / ".git").exists():
            self._run(["git", "init"], workspace_path)
        self._run(["git", "config", "user.name", "Slugger MVP"], workspace_path)
        self._run(
            ["git", "config", "user.email", "slugger-mvp@users.noreply.github.com"],
            workspace_path,
        )
        self._run(["gh", "auth", "setup-git"], workspace_path)
        remotes = self._run(["git", "remote"], workspace_path).stdout.split()
        url = f"https://github.com/{repository}.git"
        if "origin" in remotes:
            self._run(["git", "remote", "set-url", "origin", url], workspace_path)
        else:
            self._run(["git", "remote", "add", "origin", url], workspace_path)

    def _validate_target_repository(self, workspace_path: Path, run: MvpRun) -> None:
        raw = self._run(
            ["git", "ls-tree", "-r", "--name-only", "FETCH_HEAD"], workspace_path
        ).stdout
        existing = {line.strip() for line in raw.splitlines() if line.strip()}
        if not existing:
            return
        marker = self._run(
            ["git", "show", "FETCH_HEAD:.slugger-run-id"], workspace_path, check=False
        )
        if marker.returncode == 0 and marker.stdout.strip() == run.run_id:
            return
        inventory_paths = {
            file.path for file in (run.inventory.files if run.inventory else ())
        }
        conflicts = sorted(
            existing
            & (inventory_paths | {"pyproject.toml", "README.md", "src", "tests"})
        )
        if conflicts or existing:
            raise GitHubPublishError(
                "Target repository is not empty or Slugger-managed for this run"
            )

    def _find_pr(self, repository: str, branch: str) -> dict[str, object] | None:
        command = [
            "gh",
            "pr",
            "list",
            "--repo",
            repository,
            "--head",
            branch,
            "--state",
            "open",
            "--json",
            "number,url,isDraft",
        ]
        try:
            completed = self._run(command, Path.cwd(), check=False)
        except TypeError:
            completed = self._run(command, Path.cwd())  # type: ignore[call-arg]
        if completed.returncode != 0:
            return None
        prs = json.loads(completed.stdout or "[]")
        return prs[0] if prs else None

    def _remote_branch_sha(self, repository: str, branch: str, cwd: Path) -> str | None:
        command = [
            "gh",
            "api",
            f"repos/{repository}/git/ref/heads/{branch}",
            "--jq",
            ".object.sha",
        ]
        try:
            completed = self._run(command, cwd, check=False)
        except TypeError:
            completed = self._run(command, cwd)  # type: ignore[call-arg]
        return (
            completed.stdout.strip()
            if completed.returncode == 0 and completed.stdout.strip()
            else None
        )

    def _stage_inventory(
        self, workspace_path: Path, inventory: GeneratedProjectInventory | None
    ) -> None:
        if inventory is None:
            raise GitHubPublishError(
                "Refusing to publish without a generated-file inventory"
            )
        paths: list[str] = []
        for file in inventory.files:
            generated_path = self.workspace_manager.resolve_generated_path(
                workspace_path, file.path
            )
            if not generated_path.is_file():
                raise GitHubPublishError(
                    f"Recorded generated file is missing: {file.path}"
                )
            paths.append(file.path)
        self._run(["git", "add", "--", *paths], workspace_path)

    def _run(
        self, command: list[str], cwd: Path, *, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        executable = shutil.which(command[0])
        if executable is None:
            raise GitHubPublishError(f"Required command is not available: {command[0]}")
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        diagnostic = PublicationCommandDiagnostic(
            phase=_phase_for_command(command),
            command=_sanitize_command(command),
            return_code=completed.returncode,
            repository=self._active_repository,
            branch=self._active_branch,
            stdout=_bounded(completed.stdout),
            stderr=_bounded(completed.stderr),
        )
        self.diagnostics.append(diagnostic)
        diagnostics_path = os.environ.get("SLUGGER_PUBLICATION_DIAGNOSTICS")
        if diagnostics_path:
            Path(diagnostics_path).write_text(
                json.dumps(
                    [asdict(item) for item in self.diagnostics],
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
        if check and completed.returncode != 0:
            raise GitHubPublishError(
                f"Publication command failed during {diagnostic.phase}: {diagnostic.command}\n{diagnostic.stderr[:1000]}"
            )
        return completed


def _phase_for_command(command: list[str]) -> str:
    if command[:3] == ["gh", "repo", "view"]:
        return "verify_target_repository"
    if command[:2] == ["git", "ls-remote"]:
        return "verify_base_branch"
    if command[:2] == ["git", "push"]:
        return "push_generated_branch"
    if command[:3] == ["gh", "pr", "create"]:
        return "create_draft_pull_request"
    if command[:3] == ["gh", "pr", "list"]:
        return "find_existing_pull_request"
    return command[0] if command else "unknown"


def _sanitize_command(command: list[str]) -> str:
    return " ".join(_sanitize(part) for part in command)


def branch_name(request: MvpProjectRequest, run_id: str) -> str:
    return f"slugger/generated-{request.project_name}-{run_id[:8]}"


def pr_body(
    run: MvpRun,
    validation_results: tuple[CheckResult, ...],
    runner_result: BasicRunnerResult,
) -> str:
    inventory_lines = []
    if run.inventory is not None:
        inventory_lines = [
            f"- `{file.path}` ({file.size_bytes} bytes)" for file in run.inventory.files
        ]
    return "\n".join(
        [
            f"Original idea: {run.request.idea}",
            f"Project name: {run.request.project_name}",
            f"Template: {run.request.template}",
            f"Validation: {_summary(validation_results)}",
            f"Tests: {_summary(runner_result.checks)}",
            f"Smoke: {_check_message(runner_result.checks, 'cli_smoke')}",
            "Generated-file inventory:",
            *(inventory_lines or ["- No inventory recorded"]),
            f"Codex session ID: {run.codex_session_id or 'unknown'}",
            f"Codex prompt version: {run.prompt_version or 'unknown'}",
            f"Prompt version: {run.prompt_version or 'unknown'}",
            f"Prompt hash: {run.prompt_hash or 'unknown'}",
            f"Inventory hash: {run.inventory.inventory_hash if run.inventory else 'unknown'}",
            f"Installation result: {_check_message(runner_result.checks, 'install_project')}",
            "Known limitations: Generated by the focused Slugger MVP path; empty or same-run Slugger-managed target repositories only.",
            f"Slugger run ID: {run.run_id}",
        ]
    )


def _ensure_publishable(
    validation_results: tuple[CheckResult, ...], runner_result: BasicRunnerResult
) -> None:
    if not ProjectValidator.passed(validation_results):
        raise GitHubPublishError("Refusing to publish after failed validation")
    if not runner_result.passed:
        raise GitHubPublishError(
            "Refusing to publish after failed generated-project tests"
        )


def _summary(results: tuple[CheckResult, ...]) -> str:
    passed = sum(1 for result in results if result.passed)
    return f"{passed}/{len(results)} checks passed"


def _check_message(results: tuple[CheckResult, ...], name: str) -> str:
    for result in results:
        if result.name == name:
            return "passed" if result.passed else f"failed: {result.message}"
    return "not recorded"
