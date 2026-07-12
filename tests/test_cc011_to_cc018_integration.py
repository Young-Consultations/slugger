"""CC-011 through CC-018: Persistence, approvals, knowledge, telemetry, recipes, readiness, GitHub, and acceptance tests."""

from __future__ import annotations

from pathlib import Path


# ---------------------------------------------------------------------------
# CC-011: Durable artifact store
# ---------------------------------------------------------------------------


class TestSQLiteArtifactStore:
    def test_create_and_get(self, tmp_path: Path) -> None:
        from models.artifact_store_sqlite import SQLiteArtifactStore
        from models.artifact import DocumentArtifact

        store = SQLiteArtifactStore(tmp_path / "artifacts.db")
        art = DocumentArtifact(artifact_id="a1", name="vision", content="# Vision")
        store.create(art)
        retrieved = store.get("a1")
        assert retrieved is not None
        assert retrieved.artifact_id == "a1"
        assert retrieved.content == "# Vision"

    def test_survives_restart(self, tmp_path: Path) -> None:
        from models.artifact_store_sqlite import SQLiteArtifactStore
        from models.artifact import DocumentArtifact

        db = tmp_path / "artifacts.db"
        store = SQLiteArtifactStore(db)
        store.create(DocumentArtifact(artifact_id="a1", name="req", content="REQ-001"))
        # Simulate restart by creating a new store instance
        store2 = SQLiteArtifactStore(db)
        retrieved = store2.get("a1")
        assert retrieved is not None
        assert retrieved.content == "REQ-001"

    def test_update_appends_version(self, tmp_path: Path) -> None:
        from models.artifact_store_sqlite import SQLiteArtifactStore
        from models.artifact import DocumentArtifact

        store = SQLiteArtifactStore(tmp_path / "artifacts.db")
        art = DocumentArtifact(artifact_id="a1", name="req", content="v1")
        store.create(art)
        art2 = DocumentArtifact(artifact_id="a1", name="req", content="v2")
        store.update(art2)
        # Latest version should be v2
        assert store.get("a1").content == "v2"
        # Version history has 2 entries
        history = store.history("a1")
        assert len(history) == 2

    def test_find_by_name(self, tmp_path: Path) -> None:
        from models.artifact_store_sqlite import SQLiteArtifactStore
        from models.artifact import DocumentArtifact

        store = SQLiteArtifactStore(tmp_path / "artifacts.db")
        store.create(DocumentArtifact(artifact_id="a1", name="vision", content="V1"))
        store.create(
            DocumentArtifact(artifact_id="a2", name="requirements", content="R1")
        )
        results = store.find_by_name("vision")
        assert len(results) == 1
        assert results[0].artifact_id == "a1"

    def test_list_returns_all(self, tmp_path: Path) -> None:
        from models.artifact_store_sqlite import SQLiteArtifactStore
        from models.artifact import DocumentArtifact, CodeArtifact

        store = SQLiteArtifactStore(tmp_path / "artifacts.db")
        store.create(DocumentArtifact(artifact_id="a1", name="d1", content="c1"))
        store.create(CodeArtifact(artifact_id="a2", name="c1", content="c2"))
        all_arts = store.list()
        assert len(all_arts) == 2


# ---------------------------------------------------------------------------
# CC-012: Durable approval persistence
# ---------------------------------------------------------------------------


class TestDurableApprovalStore:
    def test_save_and_retrieve(self, tmp_path: Path) -> None:
        from workflow.durable_approvals import DurableApprovalStore
        from workflow.approvals import ApprovalRecord, ApprovalDecision

        store = DurableApprovalStore(tmp_path / "approvals.db")
        record = ApprovalRecord(
            record_id="r1",
            checkpoint_name="pre-deploy",
            run_id="run-1",
            decision=ApprovalDecision.APPROVED,
            approver="alice",
        )
        store.save(record)
        records = store.get_by_run("run-1")
        assert len(records) == 1
        assert records[0].approver == "alice"

    def test_survives_restart(self, tmp_path: Path) -> None:
        from workflow.durable_approvals import DurableApprovalStore
        from workflow.approvals import ApprovalRecord, ApprovalDecision

        db = tmp_path / "approvals.db"
        store = DurableApprovalStore(db)
        store.save(
            ApprovalRecord(
                record_id="r1",
                checkpoint_name="cp",
                run_id="run-1",
                decision=ApprovalDecision.APPROVED,
                approver="bob",
            )
        )
        store2 = DurableApprovalStore(db)
        assert store2.has_approval("run-1", "cp")

    def test_has_approval_false_when_pending(self, tmp_path: Path) -> None:
        from workflow.durable_approvals import DurableApprovalStore
        from workflow.approvals import ApprovalRecord, ApprovalDecision

        store = DurableApprovalStore(tmp_path / "approvals.db")
        store.save(
            ApprovalRecord(
                record_id="r1",
                checkpoint_name="cp",
                run_id="run-1",
                decision=ApprovalDecision.PENDING,
            )
        )
        assert store.has_approval("run-1", "cp") is False

    def test_pending_approvals_returned_on_resume(self, tmp_path: Path) -> None:
        from workflow.durable_approvals import DurableApprovalStore
        from workflow.approvals import ApprovalRecord, ApprovalDecision

        store = DurableApprovalStore(tmp_path / "approvals.db")
        store.save(
            ApprovalRecord(
                record_id="r1",
                checkpoint_name="deploy",
                run_id="run-1",
                decision=ApprovalDecision.PENDING,
            )
        )
        pending = store.get_pending_records("run-1")
        assert len(pending) == 1
        assert pending[0].record_id == "r1"


# ---------------------------------------------------------------------------
# CC-013: Knowledge context injection
# ---------------------------------------------------------------------------


class TestKnowledgeContextInjection:
    def test_execution_context_has_knowledge_context_field(self) -> None:
        from models.execution import ExecutionContext

        ctx = ExecutionContext(project_id="p1", workflow_name="wf", step_name="s")
        assert hasattr(ctx, "knowledge_context")
        assert isinstance(ctx.knowledge_context, list)

    def test_knowledge_context_is_injectable(self) -> None:
        from models.execution import ExecutionContext

        ctx = ExecutionContext(
            project_id="p1",
            workflow_name="wf",
            step_name="s",
            knowledge_context=["Use FastAPI for REST APIs.", "Use pytest for testing."],
        )
        assert "Use FastAPI for REST APIs." in ctx.knowledge_context

    def test_executor_injects_knowledge_context(self) -> None:
        """StepExecutor can pass knowledge_context via ExecutionContext."""
        from workflow.executor import StepExecutor
        from workflow.models import WorkflowStepDefinition, StepInstance
        from validators import QualityGateEvaluator, ArtifactValidator
        from unittest.mock import MagicMock

        captured = []

        class CapturingAgent:
            metadata = MagicMock()
            metadata.name = "test"

            def execute(self, context):
                captured.append(context)
                return []

        registry = MagicMock()
        registry.resolve.return_value = CapturingAgent()
        step_def = WorkflowStepDefinition(name="s", agent="test", inputs=[], outputs=[])
        step_inst = StepInstance(definition=step_def)
        executor = StepExecutor(
            agent_registry=registry,
            quality_gate_evaluator=QualityGateEvaluator(
                {"artifact_validator": ArtifactValidator()}
            ),
        )
        executor.execute("wf", "p1", step_inst, {})
        assert len(captured) == 1
        # knowledge_context is empty by default
        assert captured[0].knowledge_context == []


# ---------------------------------------------------------------------------
# CC-014: Telemetry and token budget instrumentation
# ---------------------------------------------------------------------------


class TestTelemetryInstrumentation:
    def test_telemetry_collector_exists(self) -> None:
        from observability.telemetry import TelemetryCollector

        tc = TelemetryCollector()
        assert tc is not None

    def test_cost_tracker_exists(self) -> None:
        from observability.cost_tracker import CostTracker

        ct = CostTracker()
        assert ct is not None

    def test_token_budget_exists(self) -> None:
        from observability.token_budget import TokenBudget

        tb = TokenBudget()
        assert tb is not None

    def test_execution_context_has_events(self) -> None:
        from models.execution import ExecutionContext

        ctx = ExecutionContext(project_id="p1", workflow_name="wf", step_name="s")
        assert hasattr(ctx, "events")
        assert isinstance(ctx.events, list)


# ---------------------------------------------------------------------------
# CC-015: Full AI-SDLC recipe
# ---------------------------------------------------------------------------


class TestFullSDLCRecipe:
    def test_v2_recipe_exists(self) -> None:
        from pathlib import Path

        recipe_path = (
            Path(__file__).parent.parent / "workflow" / "recipes" / "full-sdlc-v2.yaml"
        )
        assert recipe_path.exists(), f"full-sdlc-v2.yaml not found at {recipe_path}"

    def test_v2_recipe_is_parseable(self) -> None:
        import yaml
        from pathlib import Path

        recipe_path = (
            Path(__file__).parent.parent / "workflow" / "recipes" / "full-sdlc-v2.yaml"
        )
        data = yaml.safe_load(recipe_path.read_text())
        assert data["name"] == "full-sdlc-v2"
        assert data["version"] == "2.0.0"
        assert len(data["steps"]) > 8

    def test_v2_recipe_covers_all_phases(self) -> None:
        import yaml
        from pathlib import Path

        recipe_path = (
            Path(__file__).parent.parent / "workflow" / "recipes" / "full-sdlc-v2.yaml"
        )
        data = yaml.safe_load(recipe_path.read_text())
        agents = [step["agent"] for step in data["steps"]]
        # Must cover: planning, architecture, dev, QA, operations
        assert "product_vision_agent" in agents
        assert "requirements_agent" in agents
        assert "code_generator_agent" in agents
        assert "test_runner_agent" in agents
        assert "security_review_agent" in agents
        assert "deployment_agent" in agents
        assert "release_agent" in agents

    def test_v2_recipe_has_approval_gates(self) -> None:
        import yaml
        from pathlib import Path

        recipe_path = (
            Path(__file__).parent.parent / "workflow" / "recipes" / "full-sdlc-v2.yaml"
        )
        data = yaml.safe_load(recipe_path.read_text())
        steps_with_approval = [s for s in data["steps"] if "approval_policy" in s]
        assert len(steps_with_approval) >= 2

    def test_workflow_parser_validates_v2_recipe(self) -> None:
        from workflow import WorkflowParser
        from validators import WorkflowValidator

        parser = WorkflowParser(WorkflowValidator())
        from pathlib import Path

        recipe_path = (
            Path(__file__).parent.parent / "workflow" / "recipes" / "full-sdlc-v2.yaml"
        )
        wf = parser.parse_file(recipe_path)
        assert wf.name == "full-sdlc-v2"
        assert len(wf.steps) > 8


# ---------------------------------------------------------------------------
# CC-016: Release gate collector
# ---------------------------------------------------------------------------


class TestReleaseGateCollector:
    def test_all_gates_pass_gives_release_candidate(self) -> None:
        from validators.readiness import ReleaseGateCollector

        collector = ReleaseGateCollector("app-1", "run-1")
        collector.record_passed("build", "ev1", "Build OK")
        collector.record_passed("tests", "ev2", "All tests passed")
        collector.record_passed("security", "ev3", "No blocking findings")
        report = collector.collect()
        assert report.release_candidate is True
        assert report.blocking_gates == []

    def test_failed_gate_blocks_release(self) -> None:
        from validators.readiness import ReleaseGateCollector

        collector = ReleaseGateCollector("app-1", "run-1")
        collector.record_passed("build", "ev1")
        collector.record_failed("tests", "Test failures in test_api.py")
        collector.record_passed("security", "ev3")
        report = collector.collect()
        assert report.release_candidate is False
        assert "tests" in report.blocking_gates

    def test_missing_mandatory_gate_blocks_release(self) -> None:
        from validators.readiness import ReleaseGateCollector

        collector = ReleaseGateCollector("app-1", "run-1")
        collector.record_passed("build", "ev1")
        # Tests gate not recorded
        collector.record_passed("security", "ev3")
        report = collector.collect()
        assert report.release_candidate is False
        assert "tests" in report.blocking_gates

    def test_file_change_invalidates_readiness(self) -> None:
        from validators.readiness import ReleaseGateCollector

        collector = ReleaseGateCollector("app-1", "run-1")
        collector.record_passed("build", "ev1")
        collector.record_passed("tests", "ev2")
        collector.record_passed("security", "ev3")
        collector.invalidate_on_change("hash-v1")
        report1 = collector.collect()
        assert report1.release_candidate is True
        # File changes — new hash
        collector.invalidate_on_change("hash-v2")
        report2 = collector.collect()
        # Evidence was cleared; all mandatory gates now missing
        assert report2.release_candidate is False

    def test_report_to_dict(self) -> None:
        from validators.readiness import ReleaseGateCollector

        collector = ReleaseGateCollector("app-1", "run-1")
        collector.record_passed("build", "ev1")
        collector.record_passed("tests", "ev2")
        collector.record_passed("security", "ev3")
        report = collector.collect()
        d = report.to_dict()
        assert d["app_id"] == "app-1"
        assert d["release_candidate"] is True
        assert len(d["gates"]) >= 3


# ---------------------------------------------------------------------------
# CC-017: GitHub automation
# ---------------------------------------------------------------------------


class TestGitHubAutomation:
    def test_mock_github_service_creates_issue(self) -> None:
        from services.github import MockGitHubService

        svc = MockGitHubService()
        issue = svc.create_issue("Test issue", body="Description")
        assert issue is not None

    def test_mock_github_service_creates_pr(self) -> None:
        from services.github import MockGitHubService

        svc = MockGitHubService()
        pr = svc.create_pull_request(
            "Feature branch", "main", "feature/test", "Test PR"
        )
        assert pr is not None

    def test_mock_github_service_creates_release(self) -> None:
        from services.github import MockGitHubService

        svc = MockGitHubService()
        release = svc.create_release("v0.1.0", "Release notes", draft=True)
        assert release is not None

    def test_github_service_in_bootstrap_context(self) -> None:
        from orchestrator.bootstrap import Bootstrap
        from pathlib import Path

        bootstrap = Bootstrap(Path(__file__).parent.parent)
        ctx = bootstrap.build()
        # MockGitHubService is the default when no token is configured
        assert ctx.github is not None


# ---------------------------------------------------------------------------
# CC-018: Acceptance scenarios
# ---------------------------------------------------------------------------


class TestAcceptanceScenarios:
    def test_idea_to_artifacts_pipeline(self) -> None:
        """An idea flows through planning agents to produce structured artifacts."""
        from agents.planning.product_vision_agent import ProductVisionAgent
        from agents.planning.requirements_agent import RequirementsAgent
        from agents.planning.user_story_agent import UserStoryAgent
        from models.execution import ExecutionContext

        idea = "Build a command-line task tracker"
        ctx = ExecutionContext(
            project_id="acc-1",
            workflow_name="sdlc",
            step_name="vision",
            metadata={"idea": idea},
        )

        vision_artifacts = ProductVisionAgent().execute(ctx)
        assert len(vision_artifacts) == 1
        assert vision_artifacts[0].name == "product_vision"

        ctx2 = ExecutionContext(
            project_id="acc-1",
            workflow_name="sdlc",
            step_name="req",
            metadata={"idea": idea},
            inputs={"product_vision": vision_artifacts[0]},
        )
        req_artifacts = RequirementsAgent().execute(ctx2)
        assert len(req_artifacts) == 1
        assert "Requirements" in req_artifacts[0].content

        ctx3 = ExecutionContext(
            project_id="acc-1",
            workflow_name="sdlc",
            step_name="stories",
            metadata={"idea": idea},
            inputs={"requirements": req_artifacts[0]},
        )
        story_artifacts = UserStoryAgent().execute(ctx3)
        assert len(story_artifacts) == 1

    def test_manifest_to_workspace_pipeline(self, tmp_path: Path) -> None:
        """A validated manifest materializes to a real workspace."""
        from models.app_manifest import make_cli_manifest, validate_app_manifest
        from materializer import ProjectMaterializer

        manifest = make_cli_manifest(
            "acc-cli-1", "TaskTracker", "CLI task tracking app"
        )
        val = validate_app_manifest(manifest)
        assert val.valid, val.errors

        mat = ProjectMaterializer(tmp_path / "workspaces")
        result = mat.materialize(manifest)
        assert result.success
        assert (result.workspace.root / "pyproject.toml").exists()

    def test_readiness_gate_blocks_broken_fixture(self) -> None:
        """A fixture with failing tests cannot reach release-candidate state."""
        from validators.readiness import ReleaseGateCollector

        collector = ReleaseGateCollector("broken-app", "run-1")
        collector.record_passed("build", "ev1")
        collector.record_failed("tests", "pytest found 3 failures")
        collector.record_passed("security", "ev3")
        report = collector.collect()
        assert report.release_candidate is False

    def test_remediation_loop_with_seeded_defect(self) -> None:
        """A seeded code defect is flagged and can be remediated."""
        from validators.remediation import (
            BoundedRemediationLoop,
            Finding,
            FindingCategory,
            FindingSeverity,
        )

        loop = BoundedRemediationLoop()
        findings = [
            Finding(
                "f1",
                FindingSeverity.HIGH,
                FindingCategory.CODE_REVIEW,
                "Missing null check",
            ),
        ]
        remediation_count = {"n": 0}

        def fix_on_second_attempt(f):
            remediation_count["n"] += 1
            return remediation_count["n"] >= 2

        result = loop.process(findings, attempt_fn=fix_on_second_attempt)
        assert result.resolved_findings[0].finding_id == "f1"

    def test_full_bootstrap_produces_working_context(self) -> None:
        """The bootstrapped ApplicationContext is valid and has all required services."""
        from orchestrator.bootstrap import Bootstrap
        from pathlib import Path

        bootstrap = Bootstrap(Path(__file__).parent.parent)
        ctx = bootstrap.build()
        assert ctx.workflow_engine is not None
        assert ctx.chatgpt is not None
        assert ctx.canva is not None
        assert ctx.github is not None
        assert ctx.capability_resolver is not None
