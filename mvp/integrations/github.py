"""GitHub draft pull-request publishing for generated MVP projects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import shutil
import os
import subprocess
import hashlib
import re
import tempfile

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
    _published: dict[str, GitHubPublishResult] = None  # type: ignore[assignment]

    def publish(
        self,
        run: MvpRun,
        workspace: MvpWorkspace | Path,
        validation_results: tuple[CheckResult, ...],
        runner_result: BasicRunnerResult,
    ) -> GitHubPublishResult:
        _ensure_publishable(validation_results, runner_result)
        if self._published is None:
            self._published = {}
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
        identity = publication_identity(run.request, run.prompt_hash)
        branch = branch_name(run.request, run.prompt_hash)
        if identity in self._published:
            previous = self._published[identity]
            result = GitHubPublishResult(
                branch=previous.branch,
                pull_request_url=previous.pull_request_url,
                draft=True,
                existing=True,
                commit_sha="fake-" + run.run_id[:12],
                pull_request_number=previous.pull_request_number,
            )
            run.github_publish_result = result
            self._published[identity] = result
            return result
        self.publish_count += 1
        result = GitHubPublishResult(
            branch=branch,
            pull_request_url=f"https://github.com/{run.request.github_repository}/pull/{run.run_id}",
            draft=True,
            existing=False,
            commit_sha="fake-" + run.run_id[:12],
            pull_request_number=1,
        )
        run.github_publish_result = result
        self._published[identity] = result
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
        artifact_path = self.workspace_manager._workspace_path(workspace)
        identity = publication_identity(run.request, run.prompt_hash)
        branch = branch_name(run.request, run.prompt_hash)
        self.diagnostics = []
        self._active_repository = run.request.github_repository
        self._active_branch = branch
        self._validate_inventory_artifact(artifact_path, run.inventory)
        existing_pr = self._find_matching_pr(run, branch, identity, artifact_path)

        with tempfile.TemporaryDirectory(
            prefix="slugger-publication-"
        ) as publication_dir:
            publication_path = Path(publication_dir).resolve(strict=True)
            self._verify_repo(run.request.github_repository, publication_path)
            self._prepare_git(publication_path, run.request.github_repository)
            base_branch = self._resolve_base_branch(run, publication_path)
            if existing_pr is not None:
                return self._update_existing_pr(
                    run,
                    branch,
                    identity,
                    existing_pr,
                    publication_path,
                    artifact_path,
                    validation_results,
                    runner_result,
                    base_branch,
                )

            remote_sha = self._remote_branch_sha(
                run.request.github_repository, branch, publication_path
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
                    publication_path,
                )
                self._verify_remote_inventory_tree(
                    publication_path, run, f"origin/{branch}"
                )
                existing_pr = self._find_matching_pr(
                    run, branch, identity, publication_path
                )
                if existing_pr is not None:
                    return self._update_existing_pr(
                        run,
                        branch,
                        identity,
                        existing_pr,
                        publication_path,
                        artifact_path,
                        validation_results,
                        runner_result,
                        base_branch,
                    )
                commit_sha = remote_sha
            else:
                self._run(
                    ["git", "fetch", "origin", base_branch, "--depth", "1"],
                    publication_path,
                )
                self._validate_target_repository(publication_path, run)
                self._run(
                    ["git", "checkout", "-B", branch, "FETCH_HEAD"], publication_path
                )
                self._copy_inventory_files(
                    artifact_path, publication_path, run.inventory
                )
                self._stage_inventory(publication_path, run.inventory)
                status = self._run(
                    ["git", "status", "--porcelain"], publication_path
                ).stdout
                if not status.strip():
                    commit_sha = self._remote_branch_sha(
                        run.request.github_repository, branch, publication_path
                    )
                else:
                    self._run(
                        [
                            "git",
                            "commit",
                            "-m",
                            f"Add generated {run.request.project_name} project",
                        ],
                        publication_path,
                    )
                    commit_sha = self._run(
                        ["git", "rev-parse", "HEAD"], publication_path
                    ).stdout.strip()
                self._run(["git", "push", "-u", "origin", branch], publication_path)
            existing_pr = self._find_matching_pr(
                run, branch, identity, publication_path
            )
            pr_existed_before_create = existing_pr is not None
            if existing_pr is None:
                body = pr_body(run, validation_results, runner_result, identity)
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
                    publication_path,
                    check=False,
                )
                if completed.returncode != 0:
                    existing_pr = self._find_matching_pr(
                        run, branch, identity, publication_path
                    )
                    if existing_pr is None:
                        raise GitHubPublishError(
                            "Draft pull request creation failed and no matching Slugger draft PR was found after race recovery"
                        )
                    return self._update_existing_pr(
                        run,
                        branch,
                        identity,
                        existing_pr,
                        publication_path,
                        artifact_path,
                        validation_results,
                        runner_result,
                        base_branch,
                    )
                url = completed.stdout.strip().splitlines()[-1]
                existing_pr = self._find_matching_pr(
                    run, branch, identity, publication_path
                ) or {
                    "url": url,
                    "number": 0,
                    "isDraft": True,
                    "headRefName": branch,
                    "baseRefName": base_branch,
                    "body": body,
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

    def _find_matching_pr(
        self, run: MvpRun, branch: str, identity: str, cwd: Path
    ) -> dict[str, object] | None:
        matches = self._list_identity_prs(run, branch, identity, cwd)
        if len(matches) > 1:
            summary = ", ".join(
                f"#{pr.get('number')} {pr.get('url')}" for pr in matches[:5]
            )
            raise GitHubPublishError(
                f"Multiple open Slugger draft pull requests match publication identity {identity[:12]}: {summary}. Close duplicates manually before retrying."
            )
        return matches[0] if matches else None

    def _list_identity_prs(
        self, run: MvpRun, branch: str, identity: str, cwd: Path
    ) -> list[dict[str, object]]:
        prs: list[dict[str, object]] = []
        direct = self._find_pr(run.request.github_repository, branch)
        if direct is not None:
            prs.append(direct)
        command = [
            "gh",
            "pr",
            "list",
            "--repo",
            run.request.github_repository,
            "--state",
            "open",
            "--json",
            "number,url,isDraft,headRefName,baseRefName,body",
        ]
        try:
            completed = self._run(command, cwd, check=False)
        except TypeError:
            completed = self._run(command, cwd)  # type: ignore[call-arg]
        if completed.returncode == 0:
            for pr in json.loads(completed.stdout or "[]"):
                if pr.get("number") not in {item.get("number") for item in prs}:
                    prs.append(pr)
        matches: list[dict[str, object]] = []
        for pr in prs:
            if not self._valid_slugger_pr(run, branch, identity, pr):
                if self._matching_slugger_pr_collision(run, branch, identity, pr):
                    raise GitHubPublishError(
                        "Matching Slugger-managed pull request is not draft; close it, convert it to draft manually, or regenerate on a new logical request before retrying."
                    )
                continue
            matches.append(pr)
        return matches

    def _matching_slugger_pr_collision(
        self, run: MvpRun, branch: str, identity: str, pr: dict[str, object]
    ) -> bool:
        if bool(pr.get("isDraft", False)):
            return False
        head = str(pr.get("headRefName") or branch)
        marker = parse_publication_marker(str(pr.get("body") or ""))
        if marker:
            return (
                str(marker.get("repository") or "").lower()
                == run.request.github_repository.lower()
                and marker.get("base_branch") == run.request.base_branch
                and marker.get("project_name") == run.request.project_name
                and marker.get("publication_identity") == identity
                and head.startswith("slugger/generated-")
            )
        return (
            head.startswith(f"slugger/generated-{run.request.project_name}-")
            and f"Project name: {run.request.project_name}" in str(pr.get("body") or "")
            and f"Prompt hash: {run.prompt_hash}" in str(pr.get("body") or "")
        )

    def _valid_slugger_pr(
        self, run: MvpRun, branch: str, identity: str, pr: dict[str, object]
    ) -> bool:
        if not bool(pr.get("isDraft", False)):
            return False
        base = str(pr.get("baseRefName") or run.request.base_branch)
        if base != run.request.base_branch and run.request.base_branch != "default":
            return False
        head = str(pr.get("headRefName") or branch)
        marker = parse_publication_marker(str(pr.get("body") or ""))
        if marker:
            return (
                str(marker.get("repository") or "").lower()
                == run.request.github_repository.lower()
                and marker.get("base_branch") == run.request.base_branch
                and marker.get("project_name") == run.request.project_name
                and marker.get("publication_identity") == identity
                and head.startswith("slugger/generated-")
            )
        return (
            head.startswith(f"slugger/generated-{run.request.project_name}-")
            and f"Project name: {run.request.project_name}" in str(pr.get("body") or "")
            and f"Prompt hash: {run.prompt_hash}" in str(pr.get("body") or "")
        )

    def _update_existing_pr(
        self,
        run: MvpRun,
        branch: str,
        identity: str,
        existing_pr: dict[str, object],
        cwd: Path,
        artifact_path: Path,
        validation_results: tuple[CheckResult, ...],
        runner_result: BasicRunnerResult,
        base_branch: str,
    ) -> GitHubPublishResult:
        head = str(existing_pr.get("headRefName") or branch)
        remote_sha = self._remote_branch_sha(run.request.github_repository, head, cwd)
        if remote_sha is None:
            raise GitHubPublishError("Existing Slugger draft PR head branch is missing")
        self._run(
            [
                "git",
                "fetch",
                "origin",
                f"refs/heads/{head}:refs/remotes/origin/{head}",
                "--depth",
                "1",
            ],
            cwd,
        )
        self._run(["git", "checkout", "-B", head, f"origin/{head}"], cwd)
        self._copy_inventory_files(artifact_path, cwd, run.inventory)
        self._remove_stale_inventory_files(cwd, existing_pr, run)
        self._stage_inventory(cwd, run.inventory)
        status = self._run(["git", "status", "--porcelain"], cwd).stdout
        commit_sha = remote_sha
        if status.strip():
            self._run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"Update generated {run.request.project_name} project",
                ],
                cwd,
            )
            commit_sha = self._run(["git", "rev-parse", "HEAD"], cwd).stdout.strip()
            self._run(
                [
                    "git",
                    "push",
                    f"--force-with-lease={head}:{remote_sha}",
                    "origin",
                    f"HEAD:{head}",
                ],
                cwd,
            )
        body = pr_body(run, validation_results, runner_result, identity)
        self._run(
            [
                "gh",
                "pr",
                "edit",
                str(existing_pr["number"]),
                "--repo",
                run.request.github_repository,
                "--title",
                f"Add generated {run.request.project_name} project",
                "--body",
                body,
            ],
            cwd,
        )
        result = GitHubPublishResult(
            branch=head,
            pull_request_url=str(existing_pr["url"]),
            draft=True,
            existing=True,
            commit_sha=commit_sha,
            pull_request_number=int(str(existing_pr["number"])),
        )
        run.github_publish_result = result
        return result

    def _remove_stale_inventory_files(
        self, cwd: Path, existing_pr: dict[str, object], run: MvpRun
    ) -> None:
        marker = parse_publication_marker(str(existing_pr.get("body") or ""))
        raw_old_paths = marker.get("inventory_paths", []) if marker else []
        old_paths = (
            {str(path) for path in raw_old_paths}
            if isinstance(raw_old_paths, list)
            else set()
        )
        new_paths = {
            file.path for file in (run.inventory.files if run.inventory else ())
        }
        for path in sorted(old_paths - new_paths):
            if path.startswith("/") or ".." in Path(path).parts:
                raise GitHubPublishError(
                    "Unsafe stale inventory path in existing PR marker"
                )
            self._run(["git", "rm", "-f", "--", path], cwd, check=False)

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
            "number,url,isDraft,headRefName,baseRefName,body",
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

    def _validate_inventory_artifact(
        self, artifact_path: Path, inventory: GeneratedProjectInventory | None
    ) -> None:
        if inventory is None:
            raise GitHubPublishError(
                "Refusing to publish without a generated-file inventory"
            )
        artifact_root = artifact_path.resolve(strict=True)
        for file in inventory.files:
            relative_path = Path(file.path)
            WorkspaceManager._validate_relative_path(relative_path)
            raw_source = artifact_root / relative_path
            if raw_source.is_symlink():
                raise GitHubPublishError(
                    f"Recorded generated file must not be a symlink: {file.path}"
                )
            source = raw_source.resolve(strict=False)
            if not source.is_relative_to(artifact_root):
                raise GitHubPublishError(
                    f"Recorded generated file path escapes artifact: {file.path}"
                )

    def _copy_inventory_files(
        self,
        artifact_path: Path,
        publication_path: Path,
        inventory: GeneratedProjectInventory | None,
    ) -> None:
        self._validate_inventory_artifact(artifact_path, inventory)
        assert inventory is not None
        artifact_root = artifact_path.resolve(strict=True)
        publication_root = publication_path.resolve(strict=True)
        for file in inventory.files:
            relative_path = Path(file.path)
            raw_source = artifact_root / relative_path
            if raw_source.is_symlink():
                raise GitHubPublishError(
                    f"Recorded generated file must not be a symlink: {file.path}"
                )
            source = raw_source.resolve(strict=False)
            destination = (publication_root / relative_path).resolve(strict=False)
            if not destination.is_relative_to(publication_root):
                raise GitHubPublishError(
                    f"Recorded generated file path escapes publication workspace: {file.path}"
                )
            if not source.is_file():
                raise GitHubPublishError(
                    f"Recorded generated file is missing: {file.path}"
                )
            if destination.exists() and destination.is_dir():
                raise GitHubPublishError(
                    f"Publication destination is a directory: {file.path}"
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    def _stage_inventory(
        self, workspace_path: Path, inventory: GeneratedProjectInventory | None
    ) -> None:
        if inventory is None:
            raise GitHubPublishError(
                "Refusing to publish without a generated-file inventory"
            )
        root = workspace_path.resolve(strict=True)
        paths: list[str] = []
        for file in inventory.files:
            relative_path = Path(file.path)
            WorkspaceManager._validate_relative_path(relative_path)
            generated_path = (root / relative_path).resolve(strict=False)
            if not generated_path.is_relative_to(root):
                raise GitHubPublishError(
                    f"Recorded generated file path escapes publication workspace: {file.path}"
                )
            if generated_path.is_symlink() or not generated_path.is_file():
                raise GitHubPublishError(
                    f"Recorded generated file is missing: {file.path}"
                )
            paths.append(file.path)
        self._run(["git", "add", "--", *paths], workspace_path)

    def _snapshot_inventory_files(
        self,
        workspace_path: Path,
        snapshot_path: Path,
        inventory: GeneratedProjectInventory | None,
    ) -> None:
        if inventory is None:
            raise GitHubPublishError(
                "Refusing to publish without a generated-file inventory"
            )
        for file in inventory.files:
            relative_path = Path(file.path)
            WorkspaceManager._validate_relative_path(relative_path)
            source = self.workspace_manager.resolve_generated_path(
                workspace_path, file.path
            )
            if not source.is_file():
                raise GitHubPublishError(
                    f"Recorded generated file is missing: {file.path}"
                )
            destination = (snapshot_path / relative_path).resolve(strict=False)
            if not destination.is_relative_to(snapshot_path.resolve(strict=True)):
                raise GitHubPublishError(
                    f"Recorded generated file path escapes snapshot: {file.path}"
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    def _restore_inventory_files(
        self,
        workspace_path: Path,
        snapshot_path: Path,
        inventory: GeneratedProjectInventory | None,
    ) -> None:
        if inventory is None:
            raise GitHubPublishError(
                "Refusing to publish without a generated-file inventory"
            )
        for file in inventory.files:
            relative_path = Path(file.path)
            WorkspaceManager._validate_relative_path(relative_path)
            source = (snapshot_path / relative_path).resolve(strict=False)
            if not source.is_relative_to(snapshot_path.resolve(strict=True)):
                raise GitHubPublishError(
                    f"Snapshot generated file path escapes snapshot: {file.path}"
                )
            if not source.is_file():
                raise GitHubPublishError(
                    f"Snapshot of generated file is missing: {file.path}"
                )
            destination = self.workspace_manager.resolve_generated_path(
                workspace_path, file.path
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

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


MARKER_START = "<!-- slugger-publication:"
MARKER_END = "-->"


def _normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def publication_identity(
    request: MvpProjectRequest, prompt_hash: str | None = None
) -> str:
    prompt_component = (
        prompt_hash
        or hashlib.sha256(_normalized(request.idea).encode("utf-8")).hexdigest()
    )
    payload = {
        "repository": request.github_repository.lower(),
        "base_branch": request.base_branch,
        "project_name": request.project_name,
        "template": request.template,
        "prompt": prompt_component,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()


def branch_name(request: MvpProjectRequest, run_id: str | None = None) -> str:
    return f"slugger/generated-{request.project_name}-{publication_identity(request, run_id)[:12]}"


def publication_marker(run: MvpRun, identity: str) -> str:
    marker = {
        "schema": "slugger-publication-v1",
        "repository": run.request.github_repository,
        "base_branch": run.request.base_branch,
        "project_name": run.request.project_name,
        "template": run.request.template,
        "publication_identity": identity,
        "prompt_hash": run.prompt_hash,
        "inventory_hash": run.inventory.inventory_hash if run.inventory else None,
        "inventory_paths": [
            file.path for file in (run.inventory.files if run.inventory else ())
        ],
        "slugger_run_id": run.run_id,
    }
    return f"{MARKER_START}{json.dumps(marker, sort_keys=True)}{MARKER_END}"


def parse_publication_marker(body: str) -> dict[str, object]:
    start = body.find(MARKER_START)
    if start == -1:
        return {}
    start += len(MARKER_START)
    end = body.find(MARKER_END, start)
    if end == -1:
        return {}
    try:
        data = json.loads(body[start:end].strip())
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def pr_body(
    run: MvpRun,
    validation_results: tuple[CheckResult, ...],
    runner_result: BasicRunnerResult,
    identity: str | None = None,
) -> str:
    inventory_lines = []
    if run.inventory is not None:
        inventory_lines = [
            f"- `{file.path}` ({file.size_bytes} bytes)" for file in run.inventory.files
        ]
    identity = identity or publication_identity(run.request, run.prompt_hash)
    return "\n".join(
        [
            publication_marker(run, identity),
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
