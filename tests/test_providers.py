"""Tests for provider adapters and factory.

These tests verify that ProviderFactory returns the expected provider
instances and that the adapters return the expected response shape. No
network calls are made; providers are stubs suitable for unit testing.
"""
import os
from slugger.config import ProviderConfig
from slugger.orchestrator.ai_providers.factory import ProviderFactory


def test_factory_default_env(monkeypatch):
    # ensure environment default provider selection works
    monkeypatch.setenv("SLUGGER_DEFAULT_PROVIDER", "anthropic")
    cfg = ProviderConfig.from_env()
    provider = ProviderFactory.create(cfg=cfg)
    assert provider is not None
    assert provider.name == "anthropic"


def test_factory_explicit_name(monkeypatch):
    monkeypatch.delenv("SLUGGER_DEFAULT_PROVIDER", raising=False)
    cfg = ProviderConfig.from_env()
    provider = ProviderFactory.create(name="copilot", cfg=cfg)
    assert provider.name == "copilot"


def test_provider_generate_shape():
    cfg = ProviderConfig(openai_api_key=None)
    p = ProviderFactory.create(name="openai", cfg=cfg)
    out = p.generate("hello world")
    assert isinstance(out, dict)
    assert out.get("provider") == "openai"
    assert "response" in out
