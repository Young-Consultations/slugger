"""CC-003 regression tests: capability-based runtime provider resolution."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from providers.capabilities import (
    Capability,
    CapabilityNotAvailableError,
    CapabilityResolution,
    CapabilityResolver,
    DEFAULT_CAPABILITY_PROVIDERS,
)
from models.provider import HealthResult, ProviderConfig, ProviderType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_provider(name: str = 'mock', available: bool = True, model: str = 'stub') -> MagicMock:
    provider = MagicMock()
    provider.config = ProviderConfig(name=name, provider_type=ProviderType.MOCK)
    provider.health_check.return_value = HealthResult(
        provider=name,
        available=available,
        model=model,
        has_credentials=False,
    )
    return provider


def _make_registry(*provider_tuples: tuple[str, MagicMock]) -> MagicMock:
    """Build a fake ProviderRegistry from (name, provider) pairs."""
    store = dict(provider_tuples)

    def _resolve(name: str):
        if name not in store:
            raise KeyError(f'Unknown provider: {name!r}')
        return store[name]

    def _list():
        return sorted(store)

    reg = MagicMock()
    reg.resolve.side_effect = _resolve
    reg.list.return_value = _list()
    return reg


# ---------------------------------------------------------------------------
# Capability enum
# ---------------------------------------------------------------------------

class TestCapabilityEnum:
    def test_all_capabilities_have_string_values(self) -> None:
        for cap in Capability:
            assert isinstance(cap.value, str)
            assert cap.value

    def test_expected_capabilities_present(self) -> None:
        names = {c.value for c in Capability}
        for expected in [
            'planning_generation',
            'prompt_review',
            'code_agent',
            'code_review',
            'refactor',
            'embeddings',
            'design',
            'repository_management',
            'workflow_management',
        ]:
            assert expected in names


# ---------------------------------------------------------------------------
# CapabilityResolver
# ---------------------------------------------------------------------------

class TestCapabilityResolver:
    def test_resolves_to_first_available_provider(self) -> None:
        reg = _make_registry(('mock', _make_provider('mock', available=True)))
        resolver = CapabilityResolver(reg)
        result = resolver.resolve(Capability.PLANNING_GENERATION)
        assert result.available

    def test_prefers_preferred_provider(self) -> None:
        mock_p = _make_provider('mock')
        openai_p = _make_provider('openai')
        reg = _make_registry(('mock', mock_p), ('openai', openai_p))
        resolver = CapabilityResolver(reg)
        result = resolver.resolve(Capability.EMBEDDINGS, preferred_provider='openai')
        assert result.provider_name == 'openai'

    def test_falls_back_when_preferred_unavailable(self) -> None:
        openai_p = _make_provider('openai', available=False)
        mock_p = _make_provider('mock', available=True)
        reg = _make_registry(('openai', openai_p), ('mock', mock_p))
        resolver = CapabilityResolver(reg, capability_map={
            Capability.PLANNING_GENERATION: ['openai', 'mock'],
        })
        result = resolver.resolve(Capability.PLANNING_GENERATION)
        assert result.provider_name == 'mock'
        assert result.used_fallback

    def test_strict_mode_rejects_mock(self) -> None:
        reg = _make_registry(('mock', _make_provider('mock')))
        resolver = CapabilityResolver(
            reg,
            capability_map={Capability.CODE_AGENT: ['mock']},
            strict_mode=True,
        )
        with pytest.raises(CapabilityNotAvailableError) as exc_info:
            resolver.resolve(Capability.CODE_AGENT)
        assert 'code_agent' in str(exc_info.value)

    def test_non_strict_mode_accepts_mock(self) -> None:
        reg = _make_registry(('mock', _make_provider('mock')))
        resolver = CapabilityResolver(reg, strict_mode=False)
        result = resolver.resolve(Capability.CODE_AGENT)
        assert result.provider_name == 'mock'
        assert result.available

    def test_resolution_returns_correct_capability(self) -> None:
        reg = _make_registry(('mock', _make_provider()))
        resolver = CapabilityResolver(reg)
        result = resolver.resolve(Capability.DESIGN)
        assert result.capability == Capability.DESIGN

    def test_resolution_records_model(self) -> None:
        p = _make_provider('openai', model='gpt-4o')
        reg = _make_registry(('openai', p), ('mock', _make_provider()))
        resolver = CapabilityResolver(reg, capability_map={
            Capability.PLANNING_GENERATION: ['openai', 'mock'],
        })
        result = resolver.resolve(Capability.PLANNING_GENERATION)
        assert result.model == 'gpt-4o'

    def test_health_check_failure_skips_to_next(self) -> None:
        bad = MagicMock()
        bad.config = ProviderConfig(name='bad', provider_type=ProviderType.OPENAI)
        bad.health_check.side_effect = RuntimeError('network error')
        mock_p = _make_provider('mock')
        reg = _make_registry(('bad', bad), ('mock', mock_p))
        resolver = CapabilityResolver(reg, capability_map={
            Capability.PLANNING_GENERATION: ['bad', 'mock'],
        })
        result = resolver.resolve(Capability.PLANNING_GENERATION)
        assert result.provider_name == 'mock'

    def test_diagnostics_returns_all_capabilities(self) -> None:
        reg = _make_registry(('mock', _make_provider()))
        resolver = CapabilityResolver(reg)
        diag = resolver.diagnostics()
        for cap in Capability:
            assert cap.value in diag

    def test_validate_mandatory_returns_empty_for_available_caps(self) -> None:
        reg = _make_registry(('mock', _make_provider()))
        resolver = CapabilityResolver(reg)
        errors = resolver.validate_mandatory([Capability.PLANNING_GENERATION])
        assert errors == []

    def test_validate_mandatory_returns_errors_in_strict_mode(self) -> None:
        reg = _make_registry(('mock', _make_provider()))
        resolver = CapabilityResolver(
            reg,
            capability_map={Capability.CODE_AGENT: ['mock']},
            strict_mode=True,
        )
        errors = resolver.validate_mandatory([Capability.CODE_AGENT])
        assert len(errors) > 0


# ---------------------------------------------------------------------------
# Default capability map completeness
# ---------------------------------------------------------------------------

class TestDefaultCapabilityProviders:
    def test_all_capabilities_have_default_providers(self) -> None:
        for cap in Capability:
            assert cap in DEFAULT_CAPABILITY_PROVIDERS, f'Missing default for: {cap}'

    def test_all_defaults_include_mock_fallback(self) -> None:
        for cap, providers in DEFAULT_CAPABILITY_PROVIDERS.items():
            assert 'mock' in providers, f'No mock fallback for: {cap}'


# ---------------------------------------------------------------------------
# CapabilityResolution
# ---------------------------------------------------------------------------

class TestCapabilityResolution:
    def test_to_dict_contains_required_fields(self) -> None:
        res = CapabilityResolution(
            capability=Capability.CODE_AGENT,
            provider_name='codex',
            provider_type='codex',
            model='codex-1',
        )
        d = res.to_dict()
        assert d['capability'] == 'code_agent'
        assert d['provider_name'] == 'codex'
        assert d['model'] == 'codex-1'
        assert 'used_fallback' in d
