"""CICDAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import ConfigArtifact
from models.execution import ExecutionContext


class CICDAgent(BaseAgent):
    """Create CI/CD pipeline artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='ci_cd_agent',
                version='1.0.0',
                description='Create CI/CD pipeline artifacts.',
                category='operations',
                inputs=[],
                outputs=['ci_cd_pipeline'],
                tags=['operations', 'ci_cd'],
                provider='mock',
                external_interface='github_actions',
            ),
            capabilities=[AgentCapability(name='ci_cd', description='Create CI/CD pipeline artifacts.', outputs=('ci_cd_pipeline',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {name: context.artifact_content(name) for name in context.inputs}
        content = f"# CI/CD Pipeline\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n" + "\n\n".join(f"**{name}:**\n{content}" for name, content in input_summaries.items() if content)
        return [self.create_artifact(context, 'ci_cd_pipeline', content, ConfigArtifact)]
