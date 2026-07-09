"""Configuration helpers for Slugger orchestrator.

This module centralises loading provider-related configuration from environment
variables. It intentionally keeps responsibilities small so it can be extended to
support config files or secrets managers later.
"""
from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class ProviderConfig:
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    copilot_api_key: Optional[str] = None
    default_provider: str = "openai"

    @classmethod
    def from_env(cls) -> "ProviderConfig":
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            copilot_api_key=os.getenv("COPILOT_API_KEY"),
            default_provider=os.getenv("SLUGGER_DEFAULT_PROVIDER", "openai"),
        )
