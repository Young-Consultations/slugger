"""Tests for the Orchestrator core and provider injection.

These tests verify provider resolution and that the orchestrator injects the
provider into agent execution inputs.
"""
from typing import Dict, Any

from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.ai_providers.factory import ProviderFactory
from slugger.config import ProviderConfig
from slugger.orchestrator.agents.base import Agent


class ProviderAwareAgent(Agent):
    name = "provider_aware"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Expect the orchestrator to inject the provider under '_provider'
        provider = inputs.get("_provider")
        if provider is None:
            return {"status": "no_provider"}
        return {"status": "ok", "provider": getattr(provider, "name", "unknown")}


def test_orchestrator_selects_provider():
    cfg = ProviderConfig(default_provider="copilot")
    orch = Orchestrator(cfg=cfg)
    assert orch.provider.name == "copilot"


def test_orchestrator_injects_provider_into_agent():
    orch = Orchestrator(provider=ProviderFactory.create(name="openai", cfg=ProviderConfig()))
    agent = ProviderAwareAgent()
    orch.register_agent(agent)
    out = orch.run_agent("provider_aware", {})
    assert out["status"] == "ok"
    assert out["provider"] == "openai"
