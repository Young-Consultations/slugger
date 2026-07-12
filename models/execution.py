"""Execution context models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from models.artifact import Artifact

if TYPE_CHECKING:
    from agents.messaging import MessageBus
    from models.project import ProjectBrief
    from prompts.catalog import SdlcPromptCatalog
    from services.chatgpt.base import IChatGPTService


class ExecutionState(str, Enum):
    """State of a runtime execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(slots=True)
class ExecutionEvent:
    """Structured event generated during execution."""

    name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionContext:
    """Runtime context supplied to agents and engines."""

    project_id: str
    workflow_name: str
    step_name: str
    inputs: dict[str, Any] = field(default_factory=dict)
    artifacts: list[Artifact] = field(default_factory=list)
    state: ExecutionState = ExecutionState.PENDING
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    events: list[ExecutionEvent] = field(default_factory=list)
    message_bus: MessageBus | None = field(default=None)
    project_brief: ProjectBrief | None = field(default=None)
    chatgpt_service: IChatGPTService | None = field(default=None)
    """ChatGPT service for planning-agent prompt execution and prompt review."""
    codex_agent_client: object | None = field(default=None)
    """Codex coding-agent client for workspace-level code generation (CC-005)."""
    knowledge_context: list[str] = field(default_factory=list)
    """Relevant knowledge snippets injected by the knowledge indexer (CC-013)."""
    prompt_id: str | None = field(default=None)
    """Approved prompt ID used by the agent for this execution step."""
    prompt_version: str | None = field(default=None)
    """Approved prompt version used by the agent for this execution step."""
    prompt_content_hash: str | None = field(default=None)
    """SHA-256 hash of the prompt content for tamper detection."""
    prompt_catalog: SdlcPromptCatalog | None = field(default=None)
    """SdlcPromptCatalog instance for resolving managed prompts."""

    def add_event(self, event: ExecutionEvent) -> None:
        """Attach an execution event to the context."""

        self.events.append(event)

    def get_idea(self) -> str:
        """Return the project idea from the brief or metadata, never empty for a valid run."""

        if self.project_brief is not None and self.project_brief.idea:
            return self.project_brief.idea
        return self.metadata.get("idea", "")

    def artifact_content(self, name: str) -> str:
        """Return the content of a named input artifact without producing a Python repr."""

        artifact = self.inputs.get(name)
        if artifact is None:
            return ""
        content = getattr(artifact, "content", None)
        if content is None:
            return str(artifact)
        return content

    def record_prompt(self, prompt_id: str, version: str, content_hash: str) -> None:
        """Record the prompt used for this execution step."""

        self.prompt_id = prompt_id
        self.prompt_version = version
        self.prompt_content_hash = content_hash
