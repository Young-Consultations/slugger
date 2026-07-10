# providers/

This directory contains AI model provider implementations for the Slugger system.

## Purpose

The provider layer abstracts all communication with external AI services. Swapping or adding an AI provider requires only adding or modifying a provider implementation without changing agent or orchestrator code.

## Conventions

- Every provider implements the `AIProvider` interface defined in `core/interfaces/`.
- Provider configuration is read from `config/providers.yaml`.
- API keys and credentials are read from environment variables, never from code.
- Providers handle retry logic, rate limiting, and error normalization internally.
- Providers emit observability events for all requests and responses.

## Typical Contents

- `openai_provider.py` — OpenAI / Azure OpenAI provider
- `anthropic_provider.py` — Anthropic Claude provider
- `local_provider.py` — local model provider (e.g., Ollama)
- `mock_provider.py` — deterministic mock for testing

## Related

- `core/interfaces/` — the `AIProvider` abstract interface
- `config/` — provider configuration files
- `plugins/providers/` — additional providers registered as plugins
