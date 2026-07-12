"""Secrets management — resolve secrets from environment variables or a vault file.

:class:`SecretsManager` provides a unified interface for fetching sensitive
values.  It first checks a local secrets file (YAML), then falls back to
environment variables, and finally raises :class:`SecretNotFoundError` if the
secret cannot be resolved.

The secrets file should **never** be committed to version control.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


class SecretNotFoundError(KeyError):
    """Raised when a secret cannot be resolved from any configured source."""


class SecretsManager:
    """Resolve secrets from multiple sources in priority order.

    Resolution order (highest to lowest priority):

    1. In-memory overrides (programmatic, useful in tests).
    2. Environment variables — the secret name is uppercased and spaces/hyphens
       replaced with underscores (e.g. ``'openai-api-key'`` → ``OPENAI_API_KEY``).
    3. Secrets file (YAML) at *secrets_path*.

    Parameters
    ----------
    secrets_path:
        Path to the YAML secrets file.  If the file does not exist no error is
        raised — only runtime lookups that fail will raise.
    env_prefix:
        Optional prefix prepended to all environment-variable lookups
        (e.g. ``'SLUGGER_'`` → ``SLUGGER_OPENAI_API_KEY``).

    Examples
    --------
    >>> manager = SecretsManager()
    >>> manager.set('database-url', 'sqlite:///dev.db')
    >>> manager.get('database-url')
    'sqlite:///dev.db'
    """

    def __init__(
        self,
        secrets_path: Path | None = None,
        env_prefix: str = "",
    ) -> None:
        self._env_prefix = env_prefix.upper()
        self._overrides: dict[str, str] = {}
        self._file_secrets: dict[str, Any] = {}

        if secrets_path is not None and secrets_path.exists():
            raw = yaml.safe_load(secrets_path.read_text(encoding="utf-8")) or {}
            self._file_secrets = raw if isinstance(raw, dict) else {}

    # ------------------------------------------------------------------
    # Write API
    # ------------------------------------------------------------------

    def set(self, name: str, value: str) -> None:
        """Set an in-memory override for *name*.  Useful in tests."""
        self._overrides[name] = value

    def unset(self, name: str) -> None:
        """Remove an in-memory override for *name*."""
        self._overrides.pop(name, None)

    # ------------------------------------------------------------------
    # Read API
    # ------------------------------------------------------------------

    def get(self, name: str, default: str | None = None) -> str:
        """Return the resolved value for *name*.

        Raises
        ------
        SecretNotFoundError
            If the secret is not found in any source and *default* is ``None``.

        Returns
        -------
        str
            The resolved secret value.
        """
        # 1. In-memory overrides
        if name in self._overrides:
            return self._overrides[name]

        # 2. Environment variables
        env_name = self._env_prefix + name.upper().replace("-", "_").replace(" ", "_")
        env_value = os.environ.get(env_name)
        if env_value is not None:
            return env_value

        # 3. Secrets file
        file_value = self._file_secrets.get(name)
        if file_value is not None:
            return str(file_value)

        if default is not None:
            return default

        raise SecretNotFoundError(
            f"Secret '{name}' not found in overrides, environment ('{env_name}'), or secrets file."
        )

    def get_optional(self, name: str) -> str | None:
        """Return the resolved value or ``None`` if not found."""
        try:
            return self.get(name)
        except SecretNotFoundError:
            return None

    def as_dict(self) -> dict[str, str]:
        """Return all *currently resolvable* secrets as a dict.

        Does **not** include secrets that require environment lookup.
        """
        result: dict[str, str] = {**{k: str(v) for k, v in self._file_secrets.items()}}
        result.update(self._overrides)
        return result
