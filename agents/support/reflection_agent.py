"""ReflectionAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class ReflectionAgent(BaseAgent):
    """Create retrospective artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='reflection_agent',
                version='1.0.0',
                description='Create retrospective artifacts.',
                category='support',
                inputs=[],
                outputs=['retrospective'],
                tags=['support', 'reflection'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='reflection', description='Create retrospective artifacts.', outputs=('retrospective',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {name: context.artifact_content(name) for name in context.inputs}
        content = f"# Retrospective\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n" + "\n\n".join(f"**{name}:**\n{content}" for name, content in input_summaries.items() if content)
        return [self.create_artifact(context, 'retrospective', content, DocumentArtifact)]
