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
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Requirements\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'requirements', content, DocumentArtifact)]
