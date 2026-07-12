"""DiagramAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DiagramArtifact
from models.execution import ExecutionContext


class DiagramAgent(BaseAgent):
    """Create diagram artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="diagram_agent",
                version="1.0.0",
                description="Create diagram artifacts.",
                category="architecture",
                inputs=[],
                outputs=["architecture_diagram"],
                tags=["architecture", "diagram"],
                provider="mock",
                external_interface="canva",
            ),
            capabilities=[
                AgentCapability(
                    name="diagram",
                    description="Create diagram artifacts.",
                    outputs=("architecture_diagram",),
                )
            ],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {
            name: context.artifact_content(name) for name in context.inputs
        }
        content = (
            f"# Architecture Diagram\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n"
            + "\n\n".join(
                f"**{name}:**\n{content}"
                for name, content in input_summaries.items()
                if content
            )
        )
        return [
            self.create_artifact(
                context, "architecture_diagram", content, DiagramArtifact
            )
        ]
