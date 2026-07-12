from pathlib import Path

from agents.base import BaseAgent
from agents.registry import AgentRegistry
from models import AgentCapability, AgentMetadata, DocumentArtifact
from models.execution import ExecutionContext
from validators import ArtifactValidator, QualityGateEvaluator, WorkflowValidator
from workflow import StepExecutor, WorkflowEngine, WorkflowParser


class FakeVisionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="product_vision_agent",
                version="1.0.0",
                description="fake",
                category="planning",
                outputs=["product_vision"],
            ),
            capabilities=[AgentCapability(name="product_vision", description="fake")],
        )

    def _execute(self, context: ExecutionContext):
        return [
            self.create_artifact(
                context, "product_vision", "# Vision", DocumentArtifact
            )
        ]


class FakeRequirementsAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="requirements_agent",
                version="1.0.0",
                description="fake",
                category="planning",
                outputs=["requirements"],
            ),
            capabilities=[AgentCapability(name="requirements", description="fake")],
        )

    def _execute(self, context: ExecutionContext):
        return [
            self.create_artifact(
                context, "requirements", "# Requirements", DocumentArtifact
            )
        ]


def test_workflow_engine_runs_recipe() -> None:
    registry = AgentRegistry()
    registry.register(FakeVisionAgent())
    registry.register(FakeRequirementsAgent())
    executor = StepExecutor(
        registry, QualityGateEvaluator({"artifact_validator": ArtifactValidator()})
    )
    engine = WorkflowEngine(
        Path("workflow/recipes"), WorkflowParser(WorkflowValidator()), executor
    )
    result = engine.run("requirements-gathering", project_id="p1")
    assert result.status == "succeeded"
    assert [artifact.name for artifact in result.artifacts] == [
        "product_vision",
        "requirements",
    ]
