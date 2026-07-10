"""CodeReviewAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class CodeReviewAgent(BaseAgent):
    """Create code review artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='code_review_agent',
                version='1.0.0',
                description='Create code review artifacts.',
                category='development',
                inputs=[],
                outputs=['code_review'],
                tags=['development', 'code_review'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='code_review', description='Create code review artifacts.', outputs=('code_review',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Code Review\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'code_review', content, DocumentArtifact)]
