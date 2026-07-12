"""ChatGPT service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from services.chatgpt.models import (
    ChatMessage,
    PromptExecutionResult,
    PromptReviewResult,
)


class IChatGPTService(ABC):
    """Abstract interface for ChatGPT prompt execution and review."""

    @abstractmethod
    def execute(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> PromptExecutionResult:
        """Execute a user *prompt* and return the result."""

    @abstractmethod
    def execute_conversation(
        self, messages: list[ChatMessage], **kwargs: object
    ) -> PromptExecutionResult:
        """Execute a multi-turn conversation and return the final result."""

    @abstractmethod
    def review_prompt(self, prompt: str) -> PromptReviewResult:
        """Review the quality of *prompt* and return structured feedback."""
