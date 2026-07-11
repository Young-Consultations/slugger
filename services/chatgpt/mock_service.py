"""Mock ChatGPT service for testing and offline use."""

from __future__ import annotations

from services.chatgpt.base import IChatGPTService
from services.chatgpt.models import ChatGPTRole, ChatMessage, PromptExecutionResult, PromptReviewResult


class MockChatGPTService(IChatGPTService):
    """In-memory ChatGPT service that requires no network access."""

    def __init__(self, default_response: str = 'mock chatgpt response') -> None:
        self.default_response = default_response
        self.calls: list[dict[str, object]] = []

    def execute(self, prompt: str, *, system: str | None = None, **kwargs: object) -> PromptExecutionResult:
        self.calls.append({'type': 'execute', 'prompt': prompt, 'system': system})
        return PromptExecutionResult(
            prompt=prompt,
            response=self.default_response,
            model='mock-gpt',
            input_tokens=len(prompt.split()),
            output_tokens=len(self.default_response.split()),
        )

    def execute_conversation(self, messages: list[ChatMessage], **kwargs: object) -> PromptExecutionResult:
        last_user = next(
            (msg.content for msg in reversed(messages) if msg.role == ChatGPTRole.USER),
            '',
        )
        self.calls.append({'type': 'conversation', 'messages': len(messages)})
        return PromptExecutionResult(
            prompt=last_user,
            response=self.default_response,
            model='mock-gpt',
            input_tokens=sum(len(msg.content.split()) for msg in messages),
            output_tokens=len(self.default_response.split()),
        )

    def review_prompt(self, prompt: str) -> PromptReviewResult:
        self.calls.append({'type': 'review', 'prompt': prompt})
        return PromptReviewResult(
            prompt=prompt,
            score=8.0,
            feedback='Mock review: prompt is clear and specific.',
            suggestions=['Consider adding examples.'],
            passed=True,
        )
