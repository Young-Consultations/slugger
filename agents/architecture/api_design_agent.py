"""APIDesignAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class APIDesignAgent(BaseAgent):
    """Create API design artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='api_design_agent',
                version='1.0.0',
                description='Create API design artifacts.',
                category='architecture',
                inputs=[],
                outputs=['api_design'],
                tags=['architecture', 'api_design'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='api_design', description='Create API design artifacts.', outputs=('api_design',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# API Design\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'api_design', content, DocumentArtifact)]
