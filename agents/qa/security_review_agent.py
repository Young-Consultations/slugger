"""SecurityReviewAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class SecurityReviewAgent(BaseAgent):
    """Create security review artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='security_review_agent',
                version='1.0.0',
                description='Create security review artifacts.',
                category='qa',
                inputs=[],
                outputs=['security_review'],
                tags=['qa', 'security_review'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='security_review', description='Create security review artifacts.', outputs=('security_review',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Security Review\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'security_review', content, DocumentArtifact)]
