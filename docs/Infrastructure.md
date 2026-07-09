# Memory Persistence, Error Recovery, and Real Providers

This document describes the infrastructure layer enhancements for the orchestrator.

## Memory Persistence

**Purpose**: Persist artifacts, conversations, and workflow state to durable storage.

**Components**:
- **MemoryStore**: SQLite-based persistent storage
  - Artifact storage and retrieval
  - Workflow execution tracking
  - Pipeline execution history
  - Automatic cleanup of old records

**Usage**:
```python
from slugger.orchestrator.storage.memory_store import MemoryStore

store = MemoryStore("slugger.db")
store.save_artifact("req_001", "requirements_v1", "requirements", content)
artifact = store.get_artifact("req_001")
pipeline = store.get_pipeline_execution("pipe_001")
```

## Error Handling and Recovery

**Purpose**: Provide resilient execution with automatic retries and recovery strategies.

**Components**:
- **RetryConfig**: Configuration for retry behavior
  - Exponential backoff
  - Configurable max attempts
  - Custom retry exceptions

- **retry_with_backoff**: Decorator for automatic retries
  ```python
  config = RetryConfig(max_attempts=3, base_delay=1.0)
  @retry_with_backoff(config)
  def risky_operation():
      pass
  ```

- **ErrorRecovery**: Recovery strategy registry
  ```python
  recovery = ErrorRecovery()
  recovery.register_recovery(ProviderError, retry_handler)
  recovery.recover(exception)
  ```

**Features**:
- Automatic retry with exponential backoff
- Custom recovery strategies per exception type
- Configurable max attempts and delays
- Structured error logging

## Real Provider Implementations

**OpenAI Provider**:
- Uses GPT-4, GPT-3.5-turbo, and other OpenAI models
- API key from environment or parameter
- Token usage tracking
- Error handling for API failures

```python
from slugger.orchestrator.providers.openai_provider import OpenAIProvider

provider = OpenAIProvider(api_key="sk-...", model="gpt-4")
result = provider.generate("Your prompt here")
print(result["response"])
print(result["usage"]["total_tokens"])
```

**Anthropic Provider**:
- Uses Claude 3 Opus, Sonnet, and Haiku models
- API key from environment or parameter
- Token usage tracking
- Error handling for API failures

```python
from slugger.orchestrator.providers.anthropic_provider import AnthropicProvider

provider = AnthropicProvider(api_key="sk-ant-...", model="claude-3-opus-20240229")
result = provider.generate("Your prompt here")
print(result["response"])
print(result["usage"]["input_tokens"])
```

## Integration with Orchestrator

**Updated Orchestrator**:
```python
from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.providers.openai_provider import OpenAIProvider
from slugger.orchestrator.storage.memory_store import MemoryStore
from slugger.orchestrator.error_handling.recovery import (
    RetryConfig, ErrorRecovery, create_default_error_recovery
)

# Initialize with real provider
provider = OpenAIProvider(model="gpt-4")
store = MemoryStore("slugger.db")
error_recovery = create_default_error_recovery()

# Create orchestrator
orth = Orchestrator(provider=provider, memory_store=store, error_recovery=error_recovery)

# Run pipeline with persistence and error recovery
result = orch.run_pipeline(
    ["requirements", "business_analyst", "architecture", "planning", "coding", "testing", "documentation", "deployment"],
    context={"request": "Build a collaborative document editor"},
)

# All artifacts and execution records are now persisted
```

## Installation

**OpenAI**:
```bash
pip install openai
export OPENAI_API_KEY="sk-..."
```

**Anthropic**:
```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Error Recovery Strategies

- **ProviderError**: Automatically retry with backoff
- **AgentExecutionError**: Fallback to default handling
- **TimeoutError**: Retry with increased timeout
- Custom strategies: Register via `ErrorRecovery.register_recovery()`

## Future Enhancements

1. **Cohere Provider** — Add Cohere AI integration
2. **HuggingFace Provider** — Add HuggingFace Inference API
3. **PostgreSQL Backend** — Production-grade persistence
4. **Redis Caching** — Cache generated artifacts
5. **Distributed Tracing** — OpenTelemetry integration
