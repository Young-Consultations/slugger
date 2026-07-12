"""Tests for Epic 2: MessageBus wiring into runtime execution (WP-009)."""

from __future__ import annotations


from agents.messaging import AgentMessage, MessageBus
from models.artifact_lineage import LineageGraph, SdlcStage
from models.execution import ExecutionContext
from validators.quality_gate import QualityGateEvaluator
from workflow.executor import StepExecutor
from workflow.models import WorkflowStepDefinition, StepInstance


# ---------------------------------------------------------------------------
# ExecutionContext message_bus field
# ---------------------------------------------------------------------------


class TestExecutionContextMessageBus:
    def test_message_bus_defaults_to_none(self) -> None:
        ctx = ExecutionContext(
            project_id="p1",
            workflow_name="wf",
            step_name="step",
        )
        assert ctx.message_bus is None

    def test_message_bus_can_be_set(self) -> None:
        bus = MessageBus()
        ctx = ExecutionContext(
            project_id="p1",
            workflow_name="wf",
            step_name="step",
            message_bus=bus,
        )
        assert ctx.message_bus is bus


# ---------------------------------------------------------------------------
# StepExecutor publishes messages on artifact.ready
# ---------------------------------------------------------------------------


class _DummyArtifact:
    def __init__(self) -> None:
        self.artifact_id = "art-1"
        self.name = "dummy_artifact"


class _DummyAgent:
    def __init__(self) -> None:
        from models.agent import AgentMetadata

        self.metadata = AgentMetadata(
            name="dummy_agent",
            version="1.0.0",
            description="stub",
            category="test",
        )

    def execute(self, context: ExecutionContext):
        return [_DummyArtifact()]


class _DummyRegistry:
    def resolve(self, name: str):
        return _DummyAgent()


class TestStepExecutorMessageBusIntegration:
    def test_publishes_artifact_ready_event(self) -> None:
        bus = MessageBus()
        received: list[AgentMessage] = []
        bus.subscribe("*", lambda msg: received.append(msg))

        step_def = WorkflowStepDefinition(name="code_generation", agent="dummy_agent")
        step_instance = StepInstance(definition=step_def)
        executor = StepExecutor(
            _DummyRegistry(),
            QualityGateEvaluator({}),
            message_bus=bus,
        )
        executor.execute("wf", "proj-1", step_instance, {})
        assert any(msg.subject == "artifact.ready" for msg in received)

    def test_no_error_without_message_bus(self) -> None:
        step_def = WorkflowStepDefinition(name="code_generation", agent="dummy_agent")
        step_instance = StepInstance(definition=step_def)
        executor = StepExecutor(_DummyRegistry(), QualityGateEvaluator({}))
        artifacts, results = executor.execute("wf", "proj-1", step_instance, {})
        assert artifacts


# ---------------------------------------------------------------------------
# Lineage capture in StepExecutor
# ---------------------------------------------------------------------------


class TestStepExecutorLineageCapture:
    def test_lineage_node_recorded(self) -> None:
        graph = LineageGraph()
        step_def = WorkflowStepDefinition(name="code_generation", agent="dummy_agent")
        step_instance = StepInstance(definition=step_def)
        executor = StepExecutor(
            _DummyRegistry(),
            QualityGateEvaluator({}),
            lineage_graph=graph,
        )
        executor.execute("wf", "proj-1", step_instance, {})
        nodes = graph.all_nodes()
        assert len(nodes) == 1
        assert nodes[0].project_id == "proj-1"
        assert nodes[0].agent_name == "dummy_agent"

    def test_lineage_stage_inferred_from_step_name(self) -> None:
        graph = LineageGraph()
        step_def = WorkflowStepDefinition(name="test_runner_step", agent="dummy_agent")
        step_instance = StepInstance(definition=step_def)
        executor = StepExecutor(
            _DummyRegistry(),
            QualityGateEvaluator({}),
            lineage_graph=graph,
        )
        executor.execute("wf", "proj-1", step_instance, {})
        assert graph.all_nodes()[0].stage == SdlcStage.TESTS
