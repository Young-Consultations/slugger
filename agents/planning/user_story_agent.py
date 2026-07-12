"""UserStoryAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class UserStoryAgent(BaseAgent):
    """Create user story artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='user_story_agent',
                version='1.0.0',
                description='Create user story artifacts.',
                category='planning',
                inputs=[],
                outputs=['user_stories'],
                tags=['planning', 'user_stories'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='user_stories', description='Create user story artifacts.', outputs=('user_stories',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        requirements_content = context.artifact_content('requirements')
        sections = [f"# User Stories\n\n**Idea:** {idea}\n"]
        if requirements_content:
            sections.append(f"**Requirements:**\n{requirements_content}\n")
        content = '\n'.join(sections)
        return [self.create_artifact(context, 'user_stories', content, DocumentArtifact)]
