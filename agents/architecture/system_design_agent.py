"""SystemDesignAgent implementation."""

from __future__ import annotations

import re

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext

_REQUIREMENT_ID_PATTERN = re.compile(r'\b(REQ-\d{3,})\b', re.IGNORECASE)


class SystemDesignAgent(BaseAgent):
    """Create system design artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='system_design_agent',
                version='1.0.0',
                description='Create system design artifacts.',
                category='architecture',
                inputs=[],
                outputs=['system_design'],
                tags=['architecture', 'system_design'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='system_design', description='Create system design artifacts.', outputs=('system_design',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {name: context.artifact_content(name) for name in context.inputs}
        content = f"# System Design\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n" + "\n\n".join(f"**{name}:**\n{content}" for name, content in input_summaries.items() if content)
        artifact = self.create_artifact(context, 'system_design', content, DocumentArtifact)
        requirement_source = ''.join(input_summaries.values()) or content
        match = _REQUIREMENT_ID_PATTERN.search(requirement_source)
        requirement_id = match.group(1).upper() if match is not None else 'REQ-001'
        artifact.extra['requirement_id'] = requirement_id
        artifact.metadata.labels['requirement_id'] = requirement_id
        return [artifact]
