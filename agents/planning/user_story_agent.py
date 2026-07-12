"""UserStoryAgent implementation."""

from __future__ import annotations

import logging
import re

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext

_LOG = logging.getLogger(__name__)
_REQUIREMENT_ID_PATTERN = re.compile(r"\b(REQ-\d{3,})\b", re.IGNORECASE)
_STORY_ID_PATTERN = re.compile(r"\b((?:STORY|US)-\d{3,})\b", re.IGNORECASE)

_USER_STORY_PROMPT = """You are a product owner. Based on the project idea and requirements, generate detailed user stories.

Project idea: {idea}
Requirements:
{requirements}

Write user stories in "As a [user], I want [action] so that [benefit]" format.
For each story include:
- Acceptance criteria (Given/When/Then)
- Priority (High/Medium/Low)
- Estimated complexity (S/M/L)
Cite the requirement IDs from the requirements artifact.
"""


class UserStoryAgent(BaseAgent):
    """Create user story artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="user_story_agent",
                version="1.0.0",
                description="Create user story artifacts.",
                category="planning",
                inputs=[],
                outputs=["user_stories"],
                tags=["planning", "user_stories"],
                provider="mock",
            ),
            capabilities=[
                AgentCapability(
                    name="user_stories",
                    description="Create user story artifacts.",
                    outputs=("user_stories",),
                )
            ],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        requirements_content = context.artifact_content("requirements")
        content = self._generate_stories(idea, requirements_content, context)
        artifact = self.create_artifact(
            context, "user_stories", content, DocumentArtifact
        )
        requirement_id = _first_match(
            _REQUIREMENT_ID_PATTERN, requirements_content or content, "REQ-001"
        )
        story_id = _first_match(_STORY_ID_PATTERN, content, "STORY-001")
        artifact.extra["requirement_id"] = requirement_id
        artifact.extra["story_id"] = story_id
        artifact.metadata.labels["requirement_id"] = requirement_id
        artifact.metadata.labels["story_id"] = story_id
        return [artifact]

    def _generate_stories(
        self, idea: str, requirements: str, context: ExecutionContext
    ) -> str:
        svc = context.chatgpt_service
        if svc is not None:
            prompt = _USER_STORY_PROMPT.format(
                idea=idea, requirements=requirements or "(not available)"
            )
            try:
                result = svc.execute(
                    prompt,
                    system="You are a product owner writing detailed user stories.",
                )
                return f"# User Stories\n\n{result.response}"
            except Exception as exc:  # noqa: BLE001
                _LOG.warning(
                    "ChatGPT user story generation failed, using template: %s", exc
                )
        sections = [f"# User Stories\n\n**Idea:** {idea}\n"]
        if requirements:
            sections.append(f"**Requirements:**\n{requirements}\n")
        return "\n".join(sections)


def _first_match(pattern: re.Pattern[str], content: str, default: str) -> str:
    match = pattern.search(content)
    if match is not None:
        return match.group(1).upper()
    return default
