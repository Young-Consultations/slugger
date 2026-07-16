"""Verification service for already-generated MVP projects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
import json
import re
from pathlib import Path
import shutil
import tempfile
from typing import Protocol

from mvp.basic_runner import BasicRunnerResult, BasicRunner
from mvp.container_runner import ContainerPolicy, ContainerizedVerifierRunner
from mvp.inventory_manifest import create_manifest, create_protected_manifest
from mvp.integrations.codex import package_name_for_project
from mvp.models import CheckResult, MvpProjectRequest
from mvp.project_validator import ProjectValidator
from mvp.workspace import WorkspaceManager


class VerificationStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"


class VerificationPhase(StrEnum):
    INTEGRITY = "integrity"
    VALIDATION = "validation"
    EXECUTION = "execution"
    MUTATION = "mutation_check"
    CONTAINER = "container_execution"


@dataclass(frozen=True)
class VerificationResult:
    status: VerificationStatus
    project_name: str
    project_path: Path
    initial_inventory_digest: str
    final_inventory_digest: str | None
    validator_results: tuple[CheckResult, ...]
    runner_results: tuple[CheckResult, ...]
    started_at: datetime
    completed_at: datetime
    failure_phase: VerificationPhase | None
    failure_message: str | None
    generated_source_changed: bool
    evidence_file: Path
    pre_execution_digest: str | None = None
    post_execution_digest: str | None = None
    container_summary: dict[str, object] | None = None


class MvpGeneratedProjectVerifier(Protocol):
    def verify_existing(
        self, *, project_dir: Path, project_name: str
    ) -> VerificationResult: ...


class ExistingProjectVerifier:
    def __init__(
        self,
        workspace_root: Path,
        *,
        timeout_seconds: int = 120,
        use_container: bool = False,
        evidence_file: Path | None = None,
    ) -> None:
        self.workspace_manager = WorkspaceManager(workspace_root)
        self.validator = ProjectValidator(self.workspace_manager, strict_packaging=True)
        self.runner = BasicRunner(
            self.workspace_manager,
            timeout_seconds=timeout_seconds,
        )
        self.use_container = use_container
        self.evidence_file = evidence_file

    def verify_existing(
        self, *, project_dir: Path, project_name: str
    ) -> VerificationResult:
        started = datetime.now(UTC)
        evidence = (
            self.evidence_file
            or (project_dir if project_dir.exists() else self.workspace_manager.root)
            / "verification-evidence.json"
        )
        validator_results: tuple[CheckResult, ...] = ()
        runner_checks: tuple[CheckResult, ...] = ()
        initial_digest = ""
        final_digest: str | None = None
        failure_phase: VerificationPhase | None = None
        failure_message: str | None = None
        changed = False
        pre_execution_digest: str | None = None
        post_execution_digest: str | None = None
        container_summary: dict[str, object] | None = None
        try:
            safe_name = _validate_project_name(project_name)
            workspace = self.workspace_manager.workspace_from_path(project_dir)
            request = MvpProjectRequest(
                "Verify generated CLI", safe_name, "cli", "owner/repo"
            )
            initial_manifest = create_manifest(workspace.path)
            initial_digest = str(initial_manifest["artifact_digest"])
            validator_results = self.validator.validate(request, workspace)
            if not ProjectValidator.passed(validator_results):
                failure_phase = VerificationPhase.VALIDATION
                failure_message = _first_failure(validator_results)
            else:
                with tempfile.TemporaryDirectory(prefix="slugger-verify-") as tmp:
                    exec_copy = Path(tmp) / "project"
                    shutil.copytree(
                        workspace.path,
                        exec_copy,
                        symlinks=False,
                        ignore=shutil.ignore_patterns("verification-evidence.json"),
                    )
                    exec_manager = WorkspaceManager(Path(tmp) / "workspaces")
                    exec_ws = exec_manager.create_workspace("execution")
                    shutil.rmtree(exec_ws.path)
                    shutil.copytree(exec_copy, exec_ws.path)
                    pre_manifest = create_protected_manifest(exec_ws.path)
                    pre_execution_digest = str(pre_manifest["artifact_digest"])
                    if self.use_container:
                        container = ContainerizedVerifierRunner(
                            policy=ContainerPolicy(
                                timeout_seconds=self.runner.timeout_seconds
                            )
                        )
                        command = container.build_command(
                            repo_root=Path(__file__).resolve().parents[1],
                            approved_project=workspace.path,
                            workspace_root=self.workspace_manager.root,
                            project_name=safe_name,
                        )
                        container_summary = command.summary
                        container_completed = container.run(command)
                        runner_checks = (
                            CheckResult(
                                "restricted_container",
                                container_completed.returncode == 0,
                                "Container verifier completed"
                                if container_completed.returncode == 0
                                else f"Container verifier exited with status {container_completed.returncode}",
                                {
                                    "command_summary": command.summary,
                                    "returncode": container_completed.returncode,
                                    "stdout": container_completed.stdout[:4000],
                                    "stderr": container_completed.stderr[:4000],
                                },
                            ),
                        )
                        if container_completed.returncode != 0:
                            failure_phase = VerificationPhase.CONTAINER
                            failure_message = _first_failure(runner_checks)
                    else:
                        runner_result: BasicRunnerResult = BasicRunner(
                            exec_manager,
                            timeout_seconds=self.runner.timeout_seconds,
                        ).run(request, exec_ws)
                        runner_checks = runner_result.checks
                        if not runner_result.passed:
                            failure_phase = VerificationPhase.EXECUTION
                            failure_message = _first_failure(runner_checks)
                    post_manifest = create_protected_manifest(exec_ws.path)
                    post_execution_digest = str(post_manifest["artifact_digest"])
                    changed = pre_manifest["entries"] != post_manifest["entries"]
                    if changed and failure_phase is None:
                        failure_phase = VerificationPhase.MUTATION
                        failure_message = "Protected generated files changed during verification execution copy"
            final_manifest = create_manifest(workspace.path)
            final_digest = str(final_manifest["artifact_digest"])
        except Exception as exc:  # noqa: BLE001 - boundary converts to evidence
            failure_phase = failure_phase or VerificationPhase.INTEGRITY
            failure_message = _sanitize(str(exc))
        status = (
            VerificationStatus.PASSED
            if failure_phase is None
            else VerificationStatus.FAILED
        )
        completed = datetime.now(UTC)
        verification_result = VerificationResult(
            status,
            project_name,
            project_dir,
            initial_digest,
            final_digest,
            validator_results,
            runner_checks,
            started,
            completed,
            failure_phase,
            failure_message,
            changed,
            evidence,
            pre_execution_digest,
            post_execution_digest,
            container_summary,
        )
        _write_evidence(verification_result)
        return verification_result


def _write_evidence(result: VerificationResult) -> None:
    data = asdict(result)
    data["status"] = result.status.value
    data["project_path"] = str(result.project_path)
    data["started_at"] = result.started_at.isoformat()
    data["completed_at"] = result.completed_at.isoformat()
    data["failure_phase"] = result.failure_phase.value if result.failure_phase else None
    data["evidence_file"] = str(result.evidence_file)
    data["schema_version"] = 1
    data["manifest_version"] = 1
    data["final_status"] = result.status.value
    data["manifest_verification_result"] = {
        "passed": result.initial_inventory_digest == result.final_inventory_digest
    }
    data["container_image_identifier"] = (result.container_summary or {}).get("image")
    data["container_execution_command_summary"] = (result.container_summary or {}).get(
        "command"
    )
    data["network_isolation_status"] = (result.container_summary or {}).get(
        "network_disabled"
    )
    data["resource_limit_configuration"] = (result.container_summary or {}).get(
        "resource_limits"
    )
    data["mutation_check_result"] = {"passed": not result.generated_source_changed}
    data["validator_results"] = [_check(c) for c in result.validator_results]
    data["runner_results"] = [_check(c) for c in result.runner_results]
    data["packaging_policy_result"] = next(
        (c for c in data["validator_results"] if c["name"] == "packaging_policy"),
        None,
    )
    result.evidence_file.parent.mkdir(parents=True, exist_ok=True)
    result.evidence_file.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _check(check: CheckResult) -> dict[str, object]:
    details = dict(check.details)
    for key in ("stdout", "stderr"):
        if key in details:
            text = _sanitize(str(details[key]))
            details[key] = text[:4000]
            details[f"{key}_truncated"] = len(text) > 4000
    return {
        "name": check.name,
        "passed": check.passed,
        "message": _sanitize(check.message),
        "details": details,
    }


def _first_failure(checks: tuple[CheckResult, ...]) -> str:
    for check in checks:
        if not check.passed:
            return _sanitize(f"{check.name}: {check.message}")
    return "Unknown failure"


def _sanitize(text: str) -> str:
    return re.sub(
        r"(?i)(api[_-]?key|authorization|token|secret)\s*[:=]\s*\S+",
        r"\1=<redacted>",
        text,
    )[:1000]


def _validate_project_name(name: str) -> str:
    req = MvpProjectRequest("x", name, "cli", "owner/repo")
    package_name_for_project(req.project_name)
    return req.project_name
