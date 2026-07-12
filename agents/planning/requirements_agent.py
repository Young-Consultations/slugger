"""RequirementsAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class RequirementsAgent(BaseAgent):
    """Create requirements artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='requirements_agent',
                version='1.0.0',
                description='Create requirements artifacts.',
                category='planning',
                inputs=[],
                outputs=['requirements'],
                tags=['planning', 'requirements'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='requirements', description='Create requirements artifacts.', outputs=('requirements',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        vision_content = context.artifact_content('product_vision')
        sections = [f"# Requirements\n\n**Idea:** {idea}\n"]
        if vision_content:
            sections.append(f"**Vision:**\n{vision_content}\n")
        content = '\n'.join(sections)
        return [self.create_artifact(context, 'requirements', content, DocumentArtifact)]
