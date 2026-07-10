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
                name='diagram_agent',
                version='1.0.0',
                description='Create diagram artifacts.',
                category='architecture',
                inputs=[],
                outputs=['architecture_diagram'],
                tags=['architecture', 'diagram'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='diagram', description='Create diagram artifacts.', outputs=('architecture_diagram',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Architecture Diagram\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'architecture_diagram', content, DiagramArtifact)]
