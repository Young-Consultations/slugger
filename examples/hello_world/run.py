"""Hello World — minimal Slugger pipeline example."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from the examples/hello_world directory
sys.path.insert(0, str(Path(__file__).parents[2]))

from agents.base import BaseAgent
from agents.registry import AgentRegistry
from models import AgentCapability, AgentMetadata, DocumentArtifact
from models.execution import ExecutionContext
from validators import ArtifactValidator, QualityGateEvaluator, WorkflowValidator
from workflow import StepExecutor, WorkflowEngine, WorkflowParser


class HelloVisionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="product_vision_agent",
                version="1.0.0",
                description="Generates a product vision",
                category="planning",
                outputs=["product_vision"],
            ),
            capabilities=[
                AgentCapability(
                    name="product_vision", description="Create product vision"
                )
            ],
        )

    def _execute(self, context: ExecutionContext) -> list:
        return [
            self.create_artifact(
                context,
                "product_vision",
                "# Vision\n\nA simple hello-world app.",
                DocumentArtifact,
            )
        ]


class HelloRequirementsAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="requirements_agent",
                version="1.0.0",
                description="Derives requirements from the vision",
                category="planning",
                outputs=["requirements"],
            ),
            capabilities=[
                AgentCapability(
                    name="requirements", description="Generate requirements"
                )
            ],
        )

    def _execute(self, context: ExecutionContext) -> list:
        return [
            self.create_artifact(
                context,
                "requirements",
                '# Requirements\n\n- Print "Hello, World!"',
                DocumentArtifact,
            )
        ]


def main() -> None:
    registry = AgentRegistry()
    registry.register(HelloVisionAgent())
    registry.register(HelloRequirementsAgent())

    evaluator = QualityGateEvaluator({"artifact_validator": ArtifactValidator()})
    executor = StepExecutor(registry, evaluator)
    engine = WorkflowEngine(
        recipe_directory=Path(__file__).parents[2] / "workflow" / "recipes",
        parser=WorkflowParser(WorkflowValidator()),
        executor=executor,
    )

    result = engine.run("requirements-gathering", project_id="hello-world")
    print(f"Status : {result.status}")
    for artifact in result.artifacts:
        print(f"Artifact: {artifact.name}")
        print(artifact.content)
        print("---")


if __name__ == "__main__":
    main()
