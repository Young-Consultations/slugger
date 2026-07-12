"""DocumentationAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class DocumentationAgent(BaseAgent):
    """Create documentation artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="documentation_agent",
                version="1.0.0",
                description="Create documentation artifacts.",
                category="development",
                inputs=[],
                outputs=["documentation"],
                tags=["development", "documentation"],
                provider="mock",
            ),
            capabilities=[
                AgentCapability(
                    name="documentation",
                    description="Create documentation artifacts.",
                    outputs=("documentation",),
                )
            ],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {
            name: context.artifact_content(name) for name in context.inputs
        }
        content = (
            f"# Documentation\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n"
            + "\n\n".join(
                f"**{name}:**\n{content}"
                for name, content in input_summaries.items()
                if content
            )
        )
        return [
            self.create_artifact(context, "documentation", content, DocumentArtifact)
        ]
