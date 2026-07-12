"""ProjectPlanAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class ProjectPlanAgent(BaseAgent):
    """Create project planning artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='project_plan_agent',
                version='1.0.0',
                description='Create project planning artifacts.',
                category='planning',
                inputs=[],
                outputs=['project_plan'],
                tags=['planning', 'project_planning'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='project_planning', description='Create project planning artifacts.', outputs=('project_plan',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        requirements_content = context.artifact_content('requirements')
        sections = [f"# Project Plan\n\n**Idea:** {idea}\n"]
        if requirements_content:
            sections.append(f"**Requirements:**\n{requirements_content}\n")
        content = '\n'.join(sections)
        return [self.create_artifact(context, 'project_plan', content, DocumentArtifact)]
