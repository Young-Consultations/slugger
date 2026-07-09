from typing import Dict, Any, Optional

from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .copilot_provider import CopilotProvider
from slugger.config import ProviderConfig


class ProviderFactory:
    """Factory to create AI provider instances based on configuration.

    The factory prefers explicit provider selection but will fall back to the
    configured default. Providers are initialised with any API key available in
    ProviderConfig. This layer keeps provider selection logic in one place and
    simplifies testing.
    """

    _mapping = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "copilot": CopilotProvider,
    }

    @classmethod
    def create(cls, name: Optional[str] = None, cfg: Optional[ProviderConfig] = None):
        cfg = cfg or ProviderConfig.from_env()
        provider_name = name or cfg.default_provider
        provider_name = provider_name.lower()
        ProviderCls = cls._mapping.get(provider_name)
        if ProviderCls is None:
            raise ValueError(f"Unknown provider '{provider_name}'")

        api_key = None
        if provider_name == "openai":
            api_key = cfg.openai_api_key
        elif provider_name == "anthropic":
            api_key = cfg.anthropic_api_key
        elif provider_name == "copilot":
            api_key = cfg.copilot_api_key

        return ProviderCls(api_key=api_key)
