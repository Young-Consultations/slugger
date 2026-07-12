"""ProjectPlanAgent implementation."""

from __future__ import annotations

import logging

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext

_LOG = logging.getLogger(__name__)

_PROJECT_PLAN_PROMPT = """You are a project manager. Based on the project idea, requirements, and user stories, create a project plan.

Project idea: {idea}
Requirements:
{requirements}

Create a detailed project plan with:
- Milestones and deliverables
- Sprint/iteration breakdown with tasks
- Dependencies and critical path
- Risk register with mitigation strategies
- Definition of Done for each phase
Reference requirement IDs to maintain traceability.
"""


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
        content = self._generate_plan(idea, requirements_content, context)
        return [self.create_artifact(context, 'project_plan', content, DocumentArtifact)]

    def _generate_plan(self, idea: str, requirements: str, context: ExecutionContext) -> str:
        svc = context.chatgpt_service
        if svc is not None:
            prompt = _PROJECT_PLAN_PROMPT.format(idea=idea, requirements=requirements or '(not available)')
            try:
                result = svc.execute(prompt, system='You are a project manager writing structured project plans.')
                return f"# Project Plan\n\n{result.response}"
            except Exception as exc:  # noqa: BLE001
                _LOG.warning('ChatGPT project plan generation failed, using template: %s', exc)
        sections = [f"# Project Plan\n\n**Idea:** {idea}\n"]
        if requirements:
            sections.append(f"**Requirements:**\n{requirements}\n")
        return '\n'.join(sections)
