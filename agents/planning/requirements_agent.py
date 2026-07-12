"""RequirementsAgent implementation."""

from __future__ import annotations

import logging
import re

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext

_LOG = logging.getLogger(__name__)
_REQUIREMENT_ID_PATTERN = re.compile(r'\b(REQ-\d{3,})\b', re.IGNORECASE)

_REQUIREMENTS_PROMPT = """You are a business analyst. Based on the project idea and vision, generate structured software requirements.

Project idea: {idea}
Product vision:
{vision}

Write a requirements document with:
- Functional requirements (REQ-001, REQ-002, ...) with clear acceptance criteria
- Non-functional requirements (performance, security, scalability)
- Constraints and assumptions
Use stable requirement IDs and cite the vision artifact.
"""


class RequirementsAgent(BaseAgent):
    """Create requirements artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='requirements_agent',
                version='1.0.0',
                description='Create requirements artifacts.',
                category='planning',
                inputs=[],
                outputs=['requirements'],
                tags=['planning', 'requirements'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='requirements', description='Create requirements artifacts.', outputs=('requirements',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        vision_content = context.artifact_content('product_vision')
        content = self._generate_requirements(idea, vision_content, context)
        artifact = self.create_artifact(context, 'requirements', content, DocumentArtifact)
        requirement_id = _first_requirement_id(content)
        artifact.extra['requirement_id'] = requirement_id
        artifact.metadata.labels['requirement_id'] = requirement_id
        return [artifact]

    def _generate_requirements(self, idea: str, vision: str, context: ExecutionContext) -> str:
        svc = context.chatgpt_service
        if svc is not None:
            prompt = _REQUIREMENTS_PROMPT.format(idea=idea, vision=vision or '(not available)')
            try:
                result = svc.execute(prompt, system='You are a business analyst writing precise software requirements.')
                return f"# Requirements\n\n{result.response}"
            except Exception as exc:  # noqa: BLE001
                _LOG.warning('ChatGPT requirements generation failed, using template: %s', exc)
        sections = [f"# Requirements\n\n**Idea:** {idea}\n"]
        if vision:
            sections.append(f"**Vision:**\n{vision}\n")
        return '\n'.join(sections)


def _first_requirement_id(content: str) -> str:
    match = _REQUIREMENT_ID_PATTERN.search(content)
    if match is not None:
        return match.group(1).upper()
    return 'REQ-001'
