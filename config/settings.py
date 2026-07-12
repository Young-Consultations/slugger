"""Configuration settings models."""

from __future__ import annotations

from dataclasses import dataclass, field

from models.provider import ProviderConfig, ProviderType


@dataclass(slots=True)
class ProviderSettings:
    """Provider configuration section."""

    default_provider: str = 'mock'
    configs: dict[str, ProviderConfig] = field(default_factory=lambda: {'mock': ProviderConfig(name='mock', provider_type=ProviderType.MOCK, model='mock-model')})


@dataclass(slots=True)
class AgentSettings:
    """Agent configuration section."""

    default_timeout_seconds: int = 60
    enabled_categories: list[str] = field(default_factory=lambda: ['planning', 'architecture', 'development', 'qa', 'operations', 'support'])


@dataclass(slots=True)
class WorkflowSettings:
    """Workflow configuration section."""

    recipe_directory: str = 'workflow/recipes'
    default_workflow: str = 'full-sdlc-v2'  # Fallback when defaults.yaml is not loaded.
    max_retries: int = 2
    state_store: str = 'workflow/state.json'


@dataclass(slots=True)
class ObservabilitySettings:
    """Observability configuration section."""

    enabled: bool = True
    log_level: str = 'INFO'
    json_logs: bool = True


@dataclass(slots=True)
class MemorySettings:
    """Memory configuration section."""

    backend: str = 'in_memory'
    storage_path: str = 'memory/store.json'


@dataclass(slots=True)
class GitHubSettings:
    """GitHub integration configuration section."""

    owner: str = ''
    repo: str = ''
    token: str = ''
    token_env: str = 'GITHUB_TOKEN'


@dataclass(slots=True)
class CanvaSettings:
    """Canva Connect API configuration section."""

    access_token: str = ''
    access_token_env: str = 'CANVA_API_TOKEN'
    base_url: str = 'https://api.canva.com/rest/v1'


@dataclass(slots=True)
class ChatGPTSettings:
    """ChatGPT / OpenAI chat-completions configuration section."""

    api_key: str = ''
    api_key_env: str = 'OPENAI_API_KEY'
    model: str = 'gpt-4o'
    base_url: str = 'https://api.openai.com/v1'
    timeout_seconds: int = 30
    mock_mode: bool = False


@dataclass(slots=True)
class Settings:
    """Root application settings."""

    environment: str = 'development'
    providers: ProviderSettings = field(default_factory=ProviderSettings)
    agents: AgentSettings = field(default_factory=AgentSettings)
    workflow: WorkflowSettings = field(default_factory=WorkflowSettings)
    observability: ObservabilitySettings = field(default_factory=ObservabilitySettings)
    memory: MemorySettings = field(default_factory=MemorySettings)
    github: GitHubSettings = field(default_factory=GitHubSettings)
    canva: CanvaSettings = field(default_factory=CanvaSettings)
    chatgpt: ChatGPTSettings = field(default_factory=ChatGPTSettings)
    plugin_directories: list[str] = field(default_factory=lambda: ['plugins'])
