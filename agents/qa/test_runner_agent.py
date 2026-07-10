"""TestRunnerAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import TestArtifact
from models.execution import ExecutionContext


class TestRunnerAgent(BaseAgent):
    """Create test execution artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='test_runner_agent',
                version='1.0.0',
                description='Create test execution artifacts.',
                category='qa',
                inputs=[],
                outputs=['test_results'],
                tags=['qa', 'test_execution'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='test_execution', description='Create test execution artifacts.', outputs=('test_results',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Test Results\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'test_results', content, TestArtifact)]
