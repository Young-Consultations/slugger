"""ProductVisionAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class ProductVisionAgent(BaseAgent):
    """Create product vision artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='product_vision_agent',
                version='1.0.0',
                description='Create product vision artifacts.',
                category='planning',
                inputs=[],
                outputs=['product_vision'],
                tags=['planning', 'product_vision'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='product_vision', description='Create product vision artifacts.', outputs=('product_vision',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        platform = ''
        if context.project_brief is not None:
            platform = context.project_brief.platform.value
        elif context.metadata.get('platform'):
            platform = context.metadata['platform']
        content = (
            f"# Product Vision\n\n"
            f"**Idea:** {idea}\n\n"
            f"**Platform:** {platform}\n\n"
            f"Agent: {self.metadata.name}\n"
        )
        return [self.create_artifact(context, 'product_vision', content, DocumentArtifact)]
