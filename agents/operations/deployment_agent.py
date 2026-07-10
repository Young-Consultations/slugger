"""DeploymentAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import ConfigArtifact
from models.execution import ExecutionContext


class DeploymentAgent(BaseAgent):
    """Create deployment artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='deployment_agent',
                version='1.0.0',
                description='Create deployment artifacts.',
                category='operations',
                inputs=[],
                outputs=['deployment_plan'],
                tags=['operations', 'deployment'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='deployment', description='Create deployment artifacts.', outputs=('deployment_plan',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Deployment Plan\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'deployment_plan', content, ConfigArtifact)]
