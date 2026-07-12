"""DeploymentAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import ConfigArtifact
from models.execution import ExecutionContext


class DeploymentAgent(BaseAgent):
    """Create deployment artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="deployment_agent",
                version="1.0.0",
                description="Create deployment artifacts.",
                category="operations",
                inputs=[],
                outputs=["deployment_plan"],
                tags=["operations", "deployment"],
                provider="mock",
            ),
            capabilities=[
                AgentCapability(
                    name="deployment",
                    description="Create deployment artifacts.",
                    outputs=("deployment_plan",),
                )
            ],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {
            name: context.artifact_content(name) for name in context.inputs
        }
        content = (
            f"# Deployment Plan\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n"
            + "\n\n".join(
                f"**{name}:**\n{content}"
                for name, content in input_summaries.items()
                if content
            )
        )
        return [
            self.create_artifact(context, "deployment_plan", content, ConfigArtifact)
        ]
