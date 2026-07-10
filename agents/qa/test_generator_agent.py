"""TestGeneratorAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import TestArtifact
from models.execution import ExecutionContext


class TestGeneratorAgent(BaseAgent):
    """Create test artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='test_generator_agent',
                version='1.0.0',
                description='Create test artifacts.',
                category='qa',
                inputs=[],
                outputs=['test_suite'],
                tags=['qa', 'test_generation'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='test_generation', description='Create test artifacts.', outputs=('test_suite',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Test Suite\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'test_suite', content, TestArtifact)]
