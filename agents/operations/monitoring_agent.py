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
        idea = context.get_idea()
        input_summaries = {name: context.artifact_content(name) for name in context.inputs}
        content = f"# Monitoring Plan\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n" + "\n\n".join(f"**{name}:**\n{content}" for name, content in input_summaries.items() if content)
        return [self.create_artifact(context, 'monitoring_plan', content, ConfigArtifact)]
