"""RefactorAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import CodeArtifact
from models.execution import ExecutionContext


class RefactorAgent(BaseAgent):
    """Create refactoring proposals."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='refactor_agent',
                version='1.0.0',
                description='Create refactoring proposals.',
                category='development',
                inputs=[],
                outputs=['refactor_plan'],
                tags=['development', 'refactoring'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='refactoring', description='Create refactoring proposals.', outputs=('refactor_plan',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {name: context.artifact_content(name) for name in context.inputs}
        content = f"# Refactor Plan\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n" + "\n\n".join(f"**{name}:**\n{content}" for name, content in input_summaries.items() if content)
        return [self.create_artifact(context, 'refactor_plan', content, CodeArtifact)]
