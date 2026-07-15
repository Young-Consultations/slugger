"""Build-service contract and implementation for the narrow Slugger MVP path."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import hashlib
import json
import os
import uuid

from mvp.basic_runner import BasicRunner, BasicRunnerResult
from mvp.integrations.codex import MvpCodexAdapter
from mvp.integrations.github import MvpGitHubPublisher
from mvp.models import (
    GeneratedProjectInventory,
    MvpBuildResult,
    MvpProjectRequest,
    MvpRun,
    MvpRunStatus,
)
from mvp.project_validator import ProjectValidator
from mvp.run_repository import SQLiteMvpRunRepository
from mvp.runtime_paths import runtime_home, sqlite_path, workspace_root
from mvp.workspace import WorkspaceManager


class MvpBuildService(Protocol):
    """Application service interface for one MVP idea-to-PR build."""

    def build(self, request: MvpProjectRequest) -> MvpBuildResult:
        """Build a generated project for the supplied MVP request."""

    def publish(self, run_id: str) -> MvpBuildResult:
        """Resume or complete GitHub publication for a persisted MVP run."""


@dataclass
class DefaultMvpBuildService(MvpBuildService):
    """Orchestrate the focused MVP dependency flow from request to draft PR."""

    run_repository: SQLiteMvpRunRepository
    workspace_manager: WorkspaceManager
    codex_adapter: MvpCodexAdapter
    project_validator: ProjectValidator
    basic_runner: BasicRunner
    github_publisher: MvpGitHubPublisher
    source_root: Path | None = None

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

            before_source = (
                _source_tree_inventory(self.source_root) if self.source_root else None
            )
            run.source_hash_before_codex = (
                str(before_source["hash"]) if before_source else None
            )
            generation = None
            generation_error: Exception | None = None
            try:
                generation = self.codex_adapter.generate_project(request, workspace)
            except Exception as exc:
                generation_error = exc
            finally:
                if before_source is not None:
                    after_source = _source_tree_inventory(self.source_root)
                    run.source_hash_after_codex = str(after_source["hash"])
                    changed = _changed_source_paths(before_source, after_source)
                    run.changed_source_paths = tuple(changed)
                    run.source_integrity_result = "failed" if changed else "passed"
            if generation_error is not None:
                if run.changed_source_paths:
                    raise MvpBuildPhaseError(
                        f"Codex failed and modified Slugger source tree: {generation_error}; changed: {', '.join(run.changed_source_paths)}"
                    ) from generation_error
                raise generation_error
            if run.changed_source_paths:
                raise MvpBuildPhaseError("Codex modified Slugger source tree")
            assert generation is not None
            run.inventory = generation.inventory
            run.codex_session_id = generation.codex_session_id
            run.slugger_correlation_id = generation.slugger_correlation_id
            run.prompt_version = generation.prompt_version
            run.prompt_hash = generation.prompt_hash
            run.transition_to(MvpRunStatus.VALIDATING)
            self.run_repository.save(run)

            validation_results = self.project_validator.validate(
                request, workspace, generation.inventory
            )
            run.validation_results = validation_results
            if not self.project_validator.passed(validation_results):
                raise MvpBuildPhaseError("Generated project validation failed")
            run.transition_to(MvpRunStatus.TESTING)
            self.run_repository.save(run)

            runner_result = self.basic_runner.run(request, workspace)
            run.test_results = runner_result.checks
            if not runner_result.passed:
                raise MvpBuildPhaseError(
                    "Generated project tests or smoke check failed"
                )
            if _github_publish_disabled():
                run.publication_skipped = True
                run.transition_to(MvpRunStatus.READY_TO_PUBLISH)
                self.run_repository.save(run)
                return MvpBuildResult(run=run)
            run.transition_to(MvpRunStatus.READY_TO_PUBLISH)
            self.run_repository.save(run)
            run.transition_to(MvpRunStatus.PUBLISHING)
            self.run_repository.save(run)

            publish_result = self.github_publisher.publish(
                run, workspace, validation_results, runner_result
            )
            run.github_publish_result = publish_result
            run.transition_to(MvpRunStatus.COMPLETED)
            self.run_repository.save(run)
            return MvpBuildResult(run=run)
        except Exception as exc:
            run.error_details = str(exc)
            if run.status is MvpRunStatus.PUBLISHING:
                run.transition_to(MvpRunStatus.PUBLICATION_FAILED)
            elif run.status not in {MvpRunStatus.FAILED, MvpRunStatus.COMPLETED}:
                run.transition_to(MvpRunStatus.FAILED)
            self.run_repository.save(run)
            return MvpBuildResult(run=run)

    def publish(self, run_id: str) -> MvpBuildResult:
        run = self.run_repository.require(run_id)
        try:
            if (
                run.inventory is None
                or not run.validation_results
                or not run.test_results
            ):
                raise MvpBuildPhaseError(
                    "Cannot publish without inventory, validation, and test evidence"
                )
            if not self.project_validator.passed(run.validation_results):
                raise MvpBuildPhaseError("Cannot publish after failed validation")
            if not all(check.passed for check in run.test_results):
                raise MvpBuildPhaseError(
                    "Cannot publish after failed generated-project checks"
                )
            if run.workspace_path is None:
                raise MvpBuildPhaseError(
                    "Cannot publish without a persisted workspace path"
                )
            workspace = self.workspace_manager.workspace_from_path(
                Path(run.workspace_path)
            )
            if not _inventory_matches_workspace(
                run.inventory, workspace.path, self.workspace_manager
            ):
                raise MvpBuildPhaseError(
                    "Cannot publish changed generated inventory without revalidation"
                )
            validation_results = run.validation_results
            runner_result = BasicRunnerResult(run.test_results)
            if (
                run.status is MvpRunStatus.COMPLETED
                and run.github_publish_result is not None
            ):
                run.error_details = None
                return MvpBuildResult(run=run)
            if run.status not in {
                MvpRunStatus.READY_TO_PUBLISH,
                MvpRunStatus.PUBLICATION_FAILED,
                MvpRunStatus.PUBLISHING,
            }:
                raise MvpBuildPhaseError(
                    f"Cannot publish run in status {run.status.value}"
                )
            if run.status is not MvpRunStatus.PUBLISHING:
                run.transition_to(MvpRunStatus.PUBLISHING)
                self.run_repository.save(run)
            publish_result = self.github_publisher.publish(
                run, workspace, validation_results, runner_result
            )
            run.github_publish_result = publish_result
            run.error_details = None
            run.transition_to(MvpRunStatus.COMPLETED)
            self.run_repository.save(run)
            return MvpBuildResult(run=run)
        except Exception as exc:
            run.error_details = str(exc)
            if run.status is MvpRunStatus.PUBLISHING:
                run.transition_to(MvpRunStatus.PUBLICATION_FAILED)
            self.run_repository.save(run)
            return MvpBuildResult(run=run)


def _inventory_matches_workspace(
    inventory: GeneratedProjectInventory,
    workspace_path: Path,
    workspace_manager: WorkspaceManager,
) -> bool:
    for generated_file in inventory.files:
        path = workspace_manager.resolve_generated_path(
            workspace_path, generated_file.path
        )
        try:
            data = path.read_bytes()
        except OSError:
            return False
        if len(data) != generated_file.size_bytes:
            return False
        if hashlib.sha256(data).hexdigest() != generated_file.sha256:
            return False
    return True


class MvpBuildPhaseError(RuntimeError):
    """Raised internally when a required MVP phase did not pass."""


def production_mvp_build_service(root_path: Path) -> DefaultMvpBuildService:
    """Create production MVP dependencies without legacy workflow initialization."""

    from mvp.integrations.codex import CodexCliMvpAdapter, FakeMvpCodexAdapter
    from mvp.integrations.github import GitHubCliMvpPublisher

    home = runtime_home()
    workspace_manager = WorkspaceManager(workspace_root(home))
    run_repository = SQLiteMvpRunRepository(sqlite_path(home))
    project_validator = ProjectValidator(workspace_manager)
    basic_runner = BasicRunner(workspace_manager)
    return DefaultMvpBuildService(
        run_repository=run_repository,
        workspace_manager=workspace_manager,
        codex_adapter=(
            FakeMvpCodexAdapter(workspace_manager)
            if _use_fake_codex_adapter()
            else CodexCliMvpAdapter(workspace_manager)
        ),
        project_validator=project_validator,
        basic_runner=basic_runner,
        github_publisher=GitHubCliMvpPublisher(workspace_manager),
        source_root=root_path.resolve(strict=False),
    )


def _use_fake_codex_adapter() -> bool:
    return os.environ.get("SLUGGER_MVP_CODEX_ADAPTER", "").lower() in {
        "fake",
        "offline",
    }


def _github_publish_disabled() -> bool:
    import os

    return os.environ.get("SLUGGER_MVP_SKIP_PUBLISH", "").lower() in {
        "1",
        "true",
        "yes",
    }


def _source_tree_inventory(source_root: Path | None) -> dict[str, object]:
    if source_root is None:
        return {"hash": "", "files": {}}
    root = source_root.resolve(strict=True)
    entries: list[dict[str, str | int]] = []
    files: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root)
        parts = set(relative.parts)
        if parts & {
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "dist",
            "build",
        }:
            continue
        if any(part.endswith(".egg-info") for part in relative.parts):
            continue
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        files[relative.as_posix()] = digest
        entries.append(
            {"path": relative.as_posix(), "sha256": digest, "size": len(data)}
        )
    inventory_hash = hashlib.sha256(
        json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {"hash": inventory_hash, "files": files}


def _changed_source_paths(
    before: dict[str, object], after: dict[str, object]
) -> list[str]:
    before_files = before.get("files", {})
    after_files = after.get("files", {})
    if not isinstance(before_files, dict) or not isinstance(after_files, dict):
        return []
    paths = set(before_files) | set(after_files)
    return sorted(
        path for path in paths if before_files.get(path) != after_files.get(path)
    )
