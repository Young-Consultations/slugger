"""Offline acceptance scenario: Task-tracker CLI application."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from materializer.workspace import ProjectMaterializer
from models.project import AppType, CodingAgent, Platform, ProjectBrief
from orchestrator import Bootstrap, Slugger
from orchestrator.orchestrator import _DEFAULT_WORKFLOW
from core.exceptions import WorkflowError
from validators.readiness import ReleaseGateCollector
from validators.remediation import (
    BoundedRemediationLoop,
    Finding,
    FindingCategory,
    FindingSeverity,
    FindingStatus,
)
from workflow.durable_approvals import DurableApprovalStore


class TestTaskTrackerScenario:
    """End-to-end offline acceptance for a task-tracker CLI app."""

    def test_build_produces_workflow_instance(self) -> None:
        bootstrap = Bootstrap(Path(__file__).resolve().parents[2])
        ctx = bootstrap.build()
        slugger = Slugger(ctx)
        project = ProjectBrief(
            idea="A CLI task tracker with add, list, done commands",
            platform=Platform.WEB,
            app_type=AppType.CLI,
            coding_agent=CodingAgent.CODEX,
        )
        persistence = ctx.workflow_engine.persistence
        assert persistence is not None
        before_runs = set(persistence.list_runs())

        with pytest.raises(WorkflowError):
            slugger.build(project)

        new_runs = set(persistence.list_runs()) - before_runs
        assert len(new_runs) == 1
        persisted = persistence.load(new_runs.pop())
        assert persisted is not None
        assert persisted.definition.name == _DEFAULT_WORKFLOW
        assert persisted.status == "failed"

    def test_workflow_is_full_sdlc_v2(self) -> None:
        assert _DEFAULT_WORKFLOW == "full-sdlc-v2"

    def test_canonical_workflow_recipe_exists(self) -> None:
        recipe = Path(__file__).resolve().parents[2] / "workflow" / "recipes" / "full-sdlc-v2.yaml"
        assert recipe.exists(), f"Canonical recipe missing: {recipe}"

    def test_old_workflow_recipe_archived(self) -> None:
        active = Path(__file__).resolve().parents[2] / "workflow" / "recipes" / "full-sdlc.yaml"
        assert not active.exists(), "full-sdlc.yaml must be archived, not in active recipes"

    def test_materialization_rejects_traversal(self, tmp_path: Path) -> None:
        materializer = ProjectMaterializer(workspace_root=tmp_path)
        with pytest.raises(ValueError):
            materializer._resolve_workspace_file(tmp_path, "../outside.py")

    def test_bounded_remediation_exhaustion(self) -> None:
        loop = BoundedRemediationLoop(max_attempts=2)
        finding = Finding(
            finding_id="tracker-tests",
            severity=FindingSeverity.HIGH,
            category=FindingCategory.TEST_FAILURE,
            message="Tests keep failing",
        )

        result = loop.process([finding], attempt_fn=lambda _: False)

        assert result.requires_manual_intervention is True
        assert result.exhausted_error is not None
        assert finding.status == FindingStatus.MANUAL_REQUIRED
        assert len(result.attempts) == 2

    def test_readiness_mandatory_gate_blocks(self) -> None:
        collector = ReleaseGateCollector("task-tracker", "run-001")
        collector.record_passed("build", evidence_id="ev-build")
        collector.record_failed("tests", reason="pytest failed")
        collector.record_passed("security", evidence_id="ev-security")

        report = collector.evaluate()

        assert report.passed is False
        assert "tests" in report.mandatory_gates_failed

    def test_approval_persists_and_invalidates(self, tmp_path: Path) -> None:
        artifact = tmp_path / "artifact.txt"
        artifact.write_text("approved", encoding="utf-8")
        checksum = hashlib.sha256(artifact.read_bytes()).hexdigest()
        store = DurableApprovalStore(db_path=tmp_path / "approvals.db")

        store.request_approval(
            request_id="req-001",
            policy={"checkpoint": "release"},
            artifact_ids=[str(artifact)],
            checksums={str(artifact): checksum},
            required_roles=[],
            quorum=1,
        )

        assert store.is_valid("req-001") is True
        artifact.write_text("changed!", encoding="utf-8")
        assert store.is_valid("req-001") is False
