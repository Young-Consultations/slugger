"""Tests for TASK-057: Secrets Management."""

from __future__ import annotations

import os

import pytest

from config.secrets import SecretsManager, SecretNotFoundError


def test_set_and_get_override() -> None:
    manager = SecretsManager()
    manager.set('my-key', 'my-value')
    assert manager.get('my-key') == 'my-value'


def test_unset_removes_override() -> None:
    manager = SecretsManager()
    manager.set('k', 'v')
    manager.unset('k')
    assert manager.get_optional('k') is None


def test_get_from_env(monkeypatch) -> None:
    monkeypatch.setenv('MY_SECRET', 'env-value')
    manager = SecretsManager()
    assert manager.get('my-secret') == 'env-value'


def test_env_prefix(monkeypatch) -> None:
    monkeypatch.setenv('SLUGGER_MY_SECRET', 'prefixed-value')
    manager = SecretsManager(env_prefix='SLUGGER_')
    assert manager.get('my-secret') == 'prefixed-value'


def test_missing_secret_raises() -> None:
    manager = SecretsManager()
    with pytest.raises(SecretNotFoundError):
        manager.get('absolutely-missing-key')


def test_missing_secret_with_default() -> None:
    manager = SecretsManager()
    value = manager.get('absent', default='fallback')
    assert value == 'fallback'


def test_get_optional_returns_none_when_missing() -> None:
    manager = SecretsManager()
    assert manager.get_optional('absent') is None


def test_from_file(tmp_path) -> None:
    secrets_file = tmp_path / 'secrets.yaml'
    secrets_file.write_text('db-url: postgres://localhost/dev\n', encoding='utf-8')
    manager = SecretsManager(secrets_path=secrets_file)
    assert manager.get('db-url') == 'postgres://localhost/dev'


def test_override_beats_env(monkeypatch) -> None:
    monkeypatch.setenv('MY_KEY', 'env')
    manager = SecretsManager()
    manager.set('my-key', 'override')
    assert manager.get('my-key') == 'override'


def test_as_dict_includes_overrides_and_file(tmp_path) -> None:
    secrets_file = tmp_path / 'secrets.yaml'
    secrets_file.write_text('file-key: file-val\n', encoding='utf-8')
    manager = SecretsManager(secrets_path=secrets_file)
    manager.set('override-key', 'override-val')
    d = manager.as_dict()
    assert d['file-key'] == 'file-val'
    assert d['override-key'] == 'override-val'
