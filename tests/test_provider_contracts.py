"""Tests for Epic 1: typed provider contracts and health checks (WP-001, WP-008)."""

from __future__ import annotations

import pytest

from models.provider import (
    EmbeddingRequest,
    EmbeddingResult,
    GenerationRequest,
    GenerationResult,
    HealthResult,
    ProviderConfig,
    ProviderType,
    RefactorRequest,
    RefactorResult,
    ReviewRequest,
    ReviewResult,
)
from providers.base import UnsupportedCapabilityError
from providers.mock_provider import MockProvider


# ---------------------------------------------------------------------------
# MockProvider typed contract tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_config() -> ProviderConfig:
    return ProviderConfig(name='test-mock', provider_type=ProviderType.MOCK, model='mock-v1')


@pytest.fixture()
def mock_provider(mock_config: ProviderConfig) -> MockProvider:
    return MockProvider(mock_config)


class TestMockProviderTypedContracts:
    def test_generate_returns_generation_result(self, mock_provider: MockProvider) -> None:
        request = GenerationRequest(prompt='Write a hello world function', language='Python')
        result = mock_provider.generate(request)
        assert isinstance(result, GenerationResult)
        assert result.content
        assert result.model == 'mock-v1'

    def test_review_returns_review_result(self, mock_provider: MockProvider) -> None:
        request = ReviewRequest(code='def hello(): pass', language='Python')
        result = mock_provider.review(request)
        assert isinstance(result, ReviewResult)
        assert result.summary
        assert result.score >= 0

    def test_refactor_returns_refactor_result(self, mock_provider: MockProvider) -> None:
        request = RefactorRequest(code='x = 1', instruction='rename to counter', language='Python')
        result = mock_provider.refactor(request)
        assert isinstance(result, RefactorResult)
        assert result.refactored_code == 'x = 1'

    def test_embed_typed_returns_embedding_result(self, mock_provider: MockProvider) -> None:
        request = EmbeddingRequest(texts=['hello', 'world'])
        result = mock_provider.embed_typed(request)
        assert isinstance(result, EmbeddingResult)
        assert len(result.embeddings) == 2

    def test_health_check_returns_health_result(self, mock_provider: MockProvider) -> None:
        health = mock_provider.health_check()
        assert isinstance(health, HealthResult)
        assert health.available is True
        assert health.provider == 'test-mock'
        assert health.has_credentials is True

    def test_supports_capability_complete(self, mock_provider: MockProvider) -> None:
        assert mock_provider.supports_capability('complete') is True

    def test_supports_capability_embed(self, mock_provider: MockProvider) -> None:
        assert mock_provider.supports_capability('embed') is True

    def test_supports_capability_unknown(self, mock_provider: MockProvider) -> None:
        # Unknown capabilities may not be supported
        result = mock_provider.supports_capability('nonexistent_capability_xyz')
        assert isinstance(result, bool)


class TestProviderTypeEnum:
    def test_codex_type_exists(self) -> None:
        assert ProviderType.CODEX.value == 'codex'

    def test_all_expected_types(self) -> None:
        types = {t.value for t in ProviderType}
        assert 'openai' in types
        assert 'anthropic' in types
        assert 'codex' in types
        assert 'mock' in types
        assert 'custom' in types


class TestUnsupportedCapabilityError:
    def test_is_provider_error_subclass(self) -> None:
        from core.exceptions import ProviderError
        err = UnsupportedCapabilityError('test')
        assert isinstance(err, ProviderError)

    def test_error_message(self) -> None:
        err = UnsupportedCapabilityError("Provider 'x' does not support review.")
        assert 'review' in str(err)
