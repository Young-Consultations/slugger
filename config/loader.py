"""Configuration loader."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from config.settings import AgentSettings, CanvaSettings, GitHubSettings, MemorySettings, ObservabilitySettings, ProviderSettings, Settings, WorkflowSettings
from core.exceptions import ConfigurationError
from models.provider import ProviderConfig, ProviderType


class ConfigLoader:
    """Loads configuration from YAML files and environment variables."""

    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path

    def load(self, config_path: str | None = None) -> Settings:
        defaults = self._load_yaml(self.root_path / 'config' / 'defaults.yaml')
        overrides = self._load_yaml(self.root_path / config_path) if config_path else {}
        secrets = self._load_yaml(self.root_path / 'config' / 'secrets.yaml')
        merged = self._deep_merge(defaults, overrides)
        merged = self._deep_merge(merged, secrets)
        merged = self._apply_environment(merged)
        return self._to_settings(merged)

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        if not isinstance(data, dict):
            raise ConfigurationError(f'Configuration file must contain a mapping: {path}')
        return data

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        result = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _apply_environment(self, config: dict[str, Any]) -> dict[str, Any]:
        config['environment'] = os.getenv('SLUGGER_ENV', config.get('environment', 'development'))
        workflow = dict(config.get('workflow', {}))
        workflow['recipe_directory'] = os.getenv('SLUGGER_WORKFLOW_DIR', workflow.get('recipe_directory', 'workflow/recipes'))
        config['workflow'] = workflow
        github = dict(config.get('github', {}))
        env_token = os.getenv(github.get('token_env', 'GITHUB_TOKEN'), '')
        if env_token:
            github['token'] = env_token
        config['github'] = github
        canva = dict(config.get('canva', {}))
        env_canva_token = os.getenv(canva.get('access_token_env', 'CANVA_API_TOKEN'), '')
        if env_canva_token:
            canva['access_token'] = env_canva_token
        config['canva'] = canva
        return config

    def _to_settings(self, data: dict[str, Any]) -> Settings:
        provider_configs_raw = data.get('providers', {}).get('configs', {})
        provider_configs = {
            name: ProviderConfig(
                name=name,
                provider_type=ProviderType(details.get('provider_type', name)),
                model=details.get('model', 'stub-model'),
                api_key=details.get('api_key'),
                api_key_env=details.get('api_key_env'),
                base_url=details.get('base_url'),
                timeout_seconds=int(details.get('timeout_seconds', 30)),
                metadata=details.get('metadata', {}),
            )
            for name, details in provider_configs_raw.items()
        }
        providers = ProviderSettings(default_provider=data.get('providers', {}).get('default_provider', 'mock'), configs=provider_configs or ProviderSettings().configs)
        github_data = data.get('github', {})
        github = GitHubSettings(
            owner=github_data.get('owner', ''),
            repo=github_data.get('repo', ''),
            token=github_data.get('token', ''),
            token_env=github_data.get('token_env', 'GITHUB_TOKEN'),
        )
        canva_data = data.get('canva', {})
        canva = CanvaSettings(
            access_token=canva_data.get('access_token', ''),
            access_token_env=canva_data.get('access_token_env', 'CANVA_API_TOKEN'),
            base_url=canva_data.get('base_url', 'https://api.canva.com/rest/v1'),
        )
        return Settings(
            environment=data.get('environment', 'development'),
            providers=providers,
            agents=AgentSettings(**data.get('agents', {})),
            workflow=WorkflowSettings(**data.get('workflow', {})),
            observability=ObservabilitySettings(**data.get('observability', {})),
            memory=MemorySettings(**data.get('memory', {})),
            github=github,
            canva=canva,
            plugin_directories=data.get('plugin_directories', ['plugins']),
        )
