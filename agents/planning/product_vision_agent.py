"""ProductVisionAgent implementation."""

from __future__ import annotations

import logging

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext

_LOG = logging.getLogger(__name__)

_VISION_PROMPT = """You are a product strategist. Based on the following idea, write a concise product vision document.

Project idea: {idea}
Platform: {platform}

Write a structured product vision with:
- Vision statement (one sentence)
- Problem being solved
- Target users
- Core value proposition
- Key outcomes
"""


class ProductVisionAgent(BaseAgent):
    """Create product vision artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="product_vision_agent",
                version="1.0.0",
                description="Create product vision artifacts.",
                category="planning",
                inputs=[],
                outputs=["product_vision"],
                tags=["planning", "product_vision"],
                provider="mock",
            ),
            capabilities=[
                AgentCapability(
                    name="product_vision",
                    description="Create product vision artifacts.",
                    outputs=("product_vision",),
                )
            ],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea()
        platform = ""
        if context.project_brief is not None:
            platform = context.project_brief.platform.value
        elif context.metadata.get("platform"):
            platform = context.metadata["platform"]

        content = self._generate_vision(idea, platform, context)
        artifact = self.create_artifact(
            context, "product_vision", content, DocumentArtifact
        )
        artifact.extra["vision_id"] = "VISION-001"
        artifact.metadata.labels["vision_id"] = "VISION-001"
        return [artifact]

    def _generate_vision(
        self, idea: str, platform: str, context: ExecutionContext
    ) -> str:
        svc = context.chatgpt_service
        if svc is not None:
            prompt = _VISION_PROMPT.format(idea=idea, platform=platform or "web")
            try:
                result = svc.execute(
                    prompt,
                    system="You are a product strategist writing clear product vision documents.",
                )
                return f"# Product Vision\n\n{result.response}"
            except Exception as exc:  # noqa: BLE001
                _LOG.warning(
                    "ChatGPT product vision generation failed, using template: %s", exc
                )
        return (
            f"# Product Vision\n\n"
            f"**Idea:** {idea}\n\n"
            f"**Platform:** {platform}\n\n"
            f"Agent: {self.metadata.name}\n"
        )
