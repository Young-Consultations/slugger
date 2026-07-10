"""MonitoringAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import ConfigArtifact
from models.execution import ExecutionContext


class MonitoringAgent(BaseAgent):
    """Create monitoring artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='monitoring_agent',
                version='1.0.0',
                description='Create monitoring artifacts.',
                category='operations',
                inputs=[],
                outputs=['monitoring_plan'],
                tags=['operations', 'monitoring'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='monitoring', description='Create monitoring artifacts.', outputs=('monitoring_plan',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Monitoring Plan\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'monitoring_plan', content, ConfigArtifact)]
