"""SystemDesignAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class SystemDesignAgent(BaseAgent):
    """Create system design artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='system_design_agent',
                version='1.0.0',
                description='Create system design artifacts.',
                category='architecture',
                inputs=[],
                outputs=['system_design'],
                tags=['architecture', 'system_design'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='system_design', description='Create system design artifacts.', outputs=('system_design',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# System Design\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'system_design', content, DocumentArtifact)]
