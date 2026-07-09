"""Tests for OpenAI and Anthropic provider implementations.

These tests verify that:
- Providers initialize correctly with API keys
- Generate method returns proper response format
- Error handling works for API failures
"""
from unittest.mock import Mock, patch, MagicMock
import pytest

from slugger.orchestrator.providers.openai_provider import OpenAIProvider
from slugger.orchestrator.providers.anthropic_provider import AnthropicProvider


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('slugger.orchestrator.providers.openai_provider.openai')
def test_openai_provider_generate(mock_openai):
    """Test OpenAI provider generation."""
    # Mock the API response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Generated text"))]
    mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    mock_openai.ChatCompletion.create.return_value = mock_response
    
    provider = OpenAIProvider(api_key="test-key")
    result = provider.generate("Test prompt")
    
    assert result["provider"] == "openai"
    assert result["response"] == "Generated text"
    assert result["usage"]["total_tokens"] == 30


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('slugger.orchestrator.providers.openai_provider.openai')
def test_openai_provider_error_handling(mock_openai):
    """Test OpenAI provider error handling."""
    mock_openai.ChatCompletion.create.side_effect = Exception("API Error")
    
    provider = OpenAIProvider(api_key="test-key")
    result = provider.generate("Test prompt")
    
    assert result["provider"] == "openai"
    assert "error" in result
    assert result["response"] == ""


@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
@patch('slugger.orchestrator.providers.anthropic_provider.anthropic')
def test_anthropic_provider_generate(mock_anthropic):
    """Test Anthropic provider generation."""
    # Mock the API response
    mock_response = Mock()
    mock_response.content = [Mock(text="Generated text")]
    mock_response.usage = Mock(input_tokens=10, output_tokens=20)
    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.Anthropic.return_value = mock_client
    
    provider = AnthropicProvider(api_key="test-key")
    result = provider.generate("Test prompt")
    
    assert result["provider"] == "anthropic"
    assert result["response"] == "Generated text"
    assert result["usage"]["input_tokens"] == 10


@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
@patch('slugger.orchestrator.providers.anthropic_provider.anthropic')
def test_anthropic_provider_error_handling(mock_anthropic):
    """Test Anthropic provider error handling."""
    mock_client = Mock()
    mock_client.messages.create.side_effect = Exception("API Error")
    mock_anthropic.Anthropic.return_value = mock_client
    
    provider = AnthropicProvider(api_key="test-key")
    result = provider.generate("Test prompt")
    
    assert result["provider"] == "anthropic"
    assert "error" in result
    assert result["response"] == ""
