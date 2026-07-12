"""Tests for Epic 1: Codex provider."""

from __future__ import annotations

import pytest

from config.settings import Settings
from core.exceptions import CodexNotAvailableError
from models.provider import ProviderConfig
from orchestrator.bootstrap import Bootstrap
from providers.codex_provider import CodexProvider


@pytest.fixture()
def config() -> ProviderConfig:
    return ProviderConfig(
        name="codex",
        provider_type="codex",
        model="gpt-4o",
        api_key="test-key",
        timeout_seconds=30,
    )


def test_codex_is_available_with_key(config: ProviderConfig) -> None:
    provider = CodexProvider(config)
    assert provider.is_available() is True


def test_codex_not_available_without_key() -> None:
    cfg = ProviderConfig(name="codex", provider_type="codex", model="gpt-4o")
    provider = CodexProvider(cfg)
    assert provider.is_available() is False


def test_codex_metadata(config: ProviderConfig) -> None:
    provider = CodexProvider(config)
    meta = provider.get_metadata()
    assert meta["provider"] == "codex"
    assert meta["model"] == "gpt-4o"
    assert meta["status"] == "ready"


def test_codex_metadata_no_key_shows_no_key() -> None:
    cfg = ProviderConfig(name="codex", provider_type="codex", model="gpt-4o")
    provider = CodexProvider(cfg)
    assert provider.get_metadata()["status"] == "no_key"


def test_codex_complete_raises_without_key() -> None:
    from core.exceptions import ProviderError

    cfg = ProviderConfig(name="codex", provider_type="codex", model="gpt-4o")
    provider = CodexProvider(cfg)
    with pytest.raises(ProviderError, match="API key"):
        provider.complete("write a hello world")


def test_codex_review_raises_without_key() -> None:
    from core.exceptions import ProviderError

    cfg = ProviderConfig(name="codex", provider_type="codex", model="gpt-4o")
    provider = CodexProvider(cfg)
    with pytest.raises(ProviderError, match="API key"):
        provider._review_raw('print("hello")')


def test_codex_refactor_raises_without_key() -> None:
    from core.exceptions import ProviderError

    cfg = ProviderConfig(name="codex", provider_type="codex", model="gpt-4o")
    provider = CodexProvider(cfg)
    with pytest.raises(ProviderError, match="API key"):
        provider._refactor_raw("x = 1", "rename to counter")


def test_codex_embed_raises_without_key() -> None:
    from core.exceptions import ProviderError

    cfg = ProviderConfig(name="codex", provider_type="codex", model="gpt-4o")
    provider = CodexProvider(cfg)
    with pytest.raises(ProviderError, match="API key"):
        provider.embed(["hello"])


def test_bootstrap_production_codex_requires_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CODEX_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    bootstrap = Bootstrap.__new__(Bootstrap)
    bootstrap.root_path = None
    settings = Settings(environment="production")
    with pytest.raises(CodexNotAvailableError):
        bootstrap._build_codex_agent_client(settings, "production")
