"""RefactorAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import CodeArtifact
from models.execution import ExecutionContext


class RefactorAgent(BaseAgent):
    """Create refactoring proposals."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='refactor_agent',
                version='1.0.0',
                description='Create refactoring proposals.',
                category='development',
                inputs=[],
                outputs=['refactor_plan'],
                tags=['development', 'refactoring'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='refactoring', description='Create refactoring proposals.', outputs=('refactor_plan',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Refactor Plan\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'refactor_plan', content, CodeArtifact)]
