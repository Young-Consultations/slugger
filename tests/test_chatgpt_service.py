"""Tests for Epic 1: ChatGPT service."""

from __future__ import annotations

from services.chatgpt import (
    ChatGPTRole,
    ChatMessage,
    IChatGPTService,
    MockChatGPTService,
    PromptExecutionResult,
    PromptReviewResult,
)


def test_mock_implements_interface() -> None:
    assert issubclass(MockChatGPTService, IChatGPTService)


def test_execute_returns_result() -> None:
    svc = MockChatGPTService(default_response='hello world')
    result = svc.execute('write me a greeting')
    assert isinstance(result, PromptExecutionResult)
    assert result.response == 'hello world'
    assert result.prompt == 'write me a greeting'
    assert result.model == 'mock-gpt'


def test_execute_records_call() -> None:
    svc = MockChatGPTService()
    svc.execute('test prompt', system='you are a helper')
    assert len(svc.calls) == 1
    assert svc.calls[0]['type'] == 'execute'
    assert svc.calls[0]['system'] == 'you are a helper'


def test_execute_conversation() -> None:
    svc = MockChatGPTService(default_response='conversation reply')
    messages = [
        ChatMessage(role=ChatGPTRole.SYSTEM, content='You are a helper.'),
        ChatMessage(role=ChatGPTRole.USER, content='Tell me something.'),
    ]
    result = svc.execute_conversation(messages)
    assert result.response == 'conversation reply'
    assert result.prompt == 'Tell me something.'


def test_execute_conversation_token_count() -> None:
    svc = MockChatGPTService()
    messages = [ChatMessage(role=ChatGPTRole.USER, content='one two three')]
    result = svc.execute_conversation(messages)
    assert result.input_tokens == 3  # word count of 'one two three'


def test_review_prompt_returns_result() -> None:
    svc = MockChatGPTService()
    result = svc.review_prompt('Generate a Python class for...')
    assert isinstance(result, PromptReviewResult)
    assert result.passed is True
    assert result.score == 8.0


def test_review_prompt_records_call() -> None:
    svc = MockChatGPTService()
    svc.review_prompt('test')
    assert any(c['type'] == 'review' for c in svc.calls)
