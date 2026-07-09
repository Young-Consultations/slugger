"""OpenAI provider implementation.

This module provides a concrete implementation of the AIProvider interface
using the OpenAI API.
"""
import os
from typing import Any, Dict

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from slugger.orchestrator.providers.base import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI GPT-4 and GPT-3.5 provider implementation."""

    name = "openai"

    def __init__(self, api_key: str = None, model: str = "gpt-4", temperature: float = 0.7):
        """Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Sampling temperature (0.0 to 2.0)
        """
        if not HAS_OPENAI:
            raise ImportError("openai package not installed. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY not set")
        
        openai.api_key = self.api_key
        self.model = model
        self.temperature = temperature

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate content using OpenAI API.
        
        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            Dict containing 'response' key with generated text
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", 4096),
            )
            
            return {
                "provider": self.name,
                "model": self.model,
                "response": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except Exception as e:
            return {
                "provider": self.name,
                "error": str(e),
                "response": "",
            }
