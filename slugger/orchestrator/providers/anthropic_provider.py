"""Anthropic Claude provider implementation.

This module provides a concrete implementation of the AIProvider interface
using the Anthropic Claude API.
"""
import os
from typing import Any, Dict

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from slugger.orchestrator.providers.base import AIProvider


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider implementation."""

    name = "anthropic"

    def __init__(self, api_key: str = None, model: str = "claude-3-opus-20240229", temperature: float = 0.7):
        """Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use (claude-3-opus, claude-3-sonnet, etc.)
            temperature: Sampling temperature (0.0 to 1.0)
        """
        if not HAS_ANTHROPIC:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and ANTHROPIC_API_KEY not set")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
        self.temperature = temperature

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate content using Anthropic Claude API.
        
        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            Dict containing 'response' key with generated text
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", self.temperature),
                messages=[{"role": "user", "content": prompt}],
            )
            
            return {
                "provider": self.name,
                "model": self.model,
                "response": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            }
        except Exception as e:
            return {
                "provider": self.name,
                "error": str(e),
                "response": "",
            }
