"""GitHubIssuesAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class GitHubIssuesAgent(BaseAgent):
    """Create GitHub issue artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='github_issues_agent',
                version='1.0.0',
                description='Create GitHub issue artifacts.',
                category='support',
                inputs=[],
                outputs=['github_issue_summary'],
                tags=['support', 'github'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='github', description='Create GitHub issue artifacts.', outputs=('github_issue_summary',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {name: context.artifact_content(name) for name in context.inputs}
        content = f"# GitHub Issue Summary\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n" + "\n\n".join(f"**{name}:**\n{content}" for name, content in input_summaries.items() if content)
        return [self.create_artifact(context, 'github_issue_summary', content, DocumentArtifact)]
