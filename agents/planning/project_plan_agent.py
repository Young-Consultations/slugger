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
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Project Plan\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'project_plan', content, DocumentArtifact)]
