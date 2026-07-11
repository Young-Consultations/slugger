"""Tests for TASK-058: Configuration Profiles."""

from __future__ import annotations

from pathlib import Path

import pytest

from config.profiles import Profile, ProfileManager
from config.settings import Settings


def _make_manager(tmp_path: Path) -> ProfileManager:
    return ProfileManager(root_path=tmp_path)


def test_register_and_activate(tmp_path) -> None:
    manager = _make_manager(tmp_path)
    manager.register(Profile('ci', overrides={'environment': 'ci'}))
    settings = manager.activate('ci')
    assert settings.environment == 'ci'


def test_unknown_profile_raises(tmp_path) -> None:
    manager = _make_manager(tmp_path)
    with pytest.raises(KeyError, match='staging'):
        manager.activate('staging')


def test_active_profile_tracked(tmp_path) -> None:
    manager = _make_manager(tmp_path)
    manager.register(Profile('dev', overrides={}))
    manager.activate('dev')
    assert manager.active_profile == 'dev'


def test_available_profiles(tmp_path) -> None:
    manager = _make_manager(tmp_path)
    manager.register(Profile('dev'))
    manager.register(Profile('prod'))
    assert set(manager.available) == {'dev', 'prod'}


def test_profile_inheritance(tmp_path) -> None:
    manager = _make_manager(tmp_path)
    manager.register(Profile('base', overrides={'environment': 'test'}))
    manager.register(Profile('ci', extends='base', overrides={'observability.log_level': 'WARNING'}))
    settings = manager.activate('ci')
    assert settings.environment == 'test'
    assert settings.observability.log_level == 'WARNING'


def test_child_overrides_parent(tmp_path) -> None:
    manager = _make_manager(tmp_path)
    manager.register(Profile('base', overrides={'environment': 'base'}))
    manager.register(Profile('child', extends='base', overrides={'environment': 'child'}))
    settings = manager.activate('child')
    assert settings.environment == 'child'


def test_profiles_yaml_round_trip(tmp_path) -> None:
    manager = _make_manager(tmp_path)
    manager.register(Profile('staging', overrides={'environment': 'staging'}, description='Staging env'))
    path = tmp_path / 'profiles.yaml'
    manager.save(path)
    manager2 = ProfileManager(root_path=tmp_path, profiles_path=path)
    assert 'staging' in manager2.available


def test_activate_applies_to_provided_base(tmp_path) -> None:
    manager = _make_manager(tmp_path)
    manager.register(Profile('prod', overrides={'environment': 'production'}))
    base = Settings(environment='development')
    settings = manager.activate('prod', base=base)
    assert settings.environment == 'production'
