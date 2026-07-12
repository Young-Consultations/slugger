"""ADRAgent implementation."""

from __future__ import annotations

import re

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext

_DECISION_ID_PATTERN = re.compile(r'\b(ADR-\d{3,})\b', re.IGNORECASE)


class ADRAgent(BaseAgent):
    """Create ADR artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='adr_agent',
                version='1.0.0',
                description='Create ADR artifacts.',
                category='architecture',
                inputs=[],
                outputs=['adr'],
                tags=['architecture', 'adr'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='adr', description='Create ADR artifacts.', outputs=('adr',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        input_summaries = {name: context.artifact_content(name) for name in context.inputs}
        content = f"# Architecture Decision Record\n\n**Idea:** {idea}\n\nAgent: {self.metadata.name}\n\n" + "\n\n".join(f"**{name}:**\n{content}" for name, content in input_summaries.items() if content)
        artifact = self.create_artifact(context, 'adr', content, DocumentArtifact)
        match = _DECISION_ID_PATTERN.search(content)
        decision_id = match.group(1).upper() if match is not None else 'ADR-001'
        artifact.extra['decision_id'] = decision_id
        artifact.metadata.labels['decision_id'] = decision_id
        return [artifact]
