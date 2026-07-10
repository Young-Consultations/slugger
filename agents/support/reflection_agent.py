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
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Retrospective\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'retrospective', content, DocumentArtifact)]
