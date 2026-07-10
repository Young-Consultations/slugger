"""KnowledgeAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class KnowledgeAgent(BaseAgent):
    """Create knowledge lookup artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='knowledge_agent',
                version='1.0.0',
                description='Create knowledge lookup artifacts.',
                category='support',
                inputs=[],
                outputs=['knowledge_response'],
                tags=['support', 'knowledge'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='knowledge', description='Create knowledge lookup artifacts.', outputs=('knowledge_response',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Knowledge Response\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'knowledge_response', content, DocumentArtifact)]
