"""Provider layer documentation.

This document describes the provider abstraction added to the orchestrator and
how to configure providers for local development and CI.
"""

Overview
--------
The orchestrator uses a provider abstraction (AIProvider) to interact with
multiple AI backends. Concrete adapters are provided for:

- OpenAI (slugger.orchestrator.ai_providers.openai_provider.OpenAIProvider)
- Anthropic (slugger.orchestrator.ai_providers.anthropic_provider.AnthropicProvider)
- GitHub Copilot (slugger.orchestrator.ai_providers.copilot_provider.CopilotProvider)

All adapters currently implement a small, test-friendly stub that returns a
predictable dict shaped response. This keeps unit tests deterministic and
avoids network calls during early development.

Configuration
-------------
Providers may be configured via environment variables. The ProviderConfig class
in slugger.config reads these variables:

- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- COPILOT_API_KEY
- SLUGGER_DEFAULT_PROVIDER (defaults to 'openai')

ProviderFactory
---------------
Use ProviderFactory.create(name=None, cfg=None) to instantiate a provider. If
name is omitted, ProviderFactory will use the default from ProviderConfig.

Example
-------
from slugger.config import ProviderConfig
from slugger.orchestrator.ai_providers.factory import ProviderFactory

cfg = ProviderConfig.from_env()
provider = ProviderFactory.create(cfg=cfg)  # returns configured default provider
result = provider.generate("Write a short spec for a requirements agent")

