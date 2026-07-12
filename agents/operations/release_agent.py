"""ReleaseAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class ReleaseAgent(BaseAgent):
    """Create release artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='release_agent',
                version='1.0.0',
                description='Create release artifacts.',
                category='operations',
                inputs=[],
                outputs=['release_notes'],
                tags=['operations', 'release'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='release', description='Create release artifacts.', outputs=('release_notes',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {name: context.artifact_content(name) for name in context.inputs}
        content = f"# Release Notes\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n" + "\n\n".join(f"**{name}:**\n{content}" for name, content in input_summaries.items() if content)
        return [self.create_artifact(context, 'release_notes', content, DocumentArtifact)]
