"""ChatGPT service models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ChatGPTRole(str, Enum):
    """Chat message roles."""

    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'


@dataclass(slots=True)
class ChatMessage:
    """A single message in a ChatGPT conversation."""

    role: ChatGPTRole
    content: str


@dataclass(slots=True)
class PromptExecutionResult:
    """Result of a ChatGPT prompt execution."""

    prompt: str
    response: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str = 'stop'
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class PromptReviewResult:
    """Result of a ChatGPT prompt quality review."""

    prompt: str
    score: float  # 0.0 – 10.0
    feedback: str
    suggestions: list[str] = field(default_factory=list)
    passed: bool = True
