"""PerformanceAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class PerformanceAgent(BaseAgent):
    """Create performance review artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='performance_agent',
                version='1.0.0',
                description='Create performance review artifacts.',
                category='qa',
                inputs=[],
                outputs=['performance_review'],
                tags=['qa', 'performance_analysis'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='performance_analysis', description='Create performance review artifacts.', outputs=('performance_review',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {name: context.artifact_content(name) for name in context.inputs}
        content = f"# Performance Review\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n" + "\n\n".join(f"**{name}:**\n{content}" for name, content in input_summaries.items() if content)
        return [self.create_artifact(context, 'performance_review', content, DocumentArtifact)]
