"""Tests for Epic 7: engineering standards repository."""

from __future__ import annotations

import pytest

from knowledge.standards import (
    EngineeringStandard,
    Pattern,
    StandardCategory,
    StandardsRepository,
)


@pytest.fixture()
def repo() -> StandardsRepository:
    return StandardsRepository()


# ---------------------------------------------------------------------------
# Standards
# ---------------------------------------------------------------------------


def test_add_and_get_standard(repo: StandardsRepository) -> None:
    std = EngineeringStandard(
        standard_id='SEC-001',
        title='Input Validation',
        description='Always validate all external inputs.',
        category=StandardCategory.SECURITY,
        mandatory=True,
    )
    repo.add_standard(std)
    result = repo.get_standard('SEC-001')
    assert result is std


def test_get_unknown_standard_returns_none(repo: StandardsRepository) -> None:
    assert repo.get_standard('UNKNOWN') is None


def test_standards_by_category(repo: StandardsRepository) -> None:
    repo.add_standard(EngineeringStandard('SEC-001', 'Validation', 'desc', StandardCategory.SECURITY))
    repo.add_standard(EngineeringStandard('COD-001', 'Type hints', 'desc', StandardCategory.CODING))
    security_stds = repo.standards_by_category(StandardCategory.SECURITY)
    assert len(security_stds) == 1
    assert security_stds[0].standard_id == 'SEC-001'


def test_mandatory_standards(repo: StandardsRepository) -> None:
    repo.add_standard(EngineeringStandard('M1', 'Mandatory', 'desc', mandatory=True))
    repo.add_standard(EngineeringStandard('A1', 'Advisory', 'desc', mandatory=False))
    mandatory = repo.mandatory_standards()
    assert len(mandatory) == 1
    assert mandatory[0].standard_id == 'M1'


def test_search_standards_by_title(repo: StandardsRepository) -> None:
    repo.add_standard(EngineeringStandard('S1', 'Input Validation', 'Always validate.'))
    repo.add_standard(EngineeringStandard('S2', 'Code Formatting', 'Use black.'))
    results = repo.search_standards('validation')
    assert len(results) == 1
    assert results[0].standard_id == 'S1'


def test_search_standards_by_tags(repo: StandardsRepository) -> None:
    repo.add_standard(
        EngineeringStandard('S1', 'Logging', 'Use structured logging.', tags=['observability', 'logging'])
    )
    results = repo.search_standards('observability')
    assert len(results) == 1


def test_all_standards(repo: StandardsRepository) -> None:
    repo.add_standard(EngineeringStandard('S1', 'T1', 'D1'))
    repo.add_standard(EngineeringStandard('S2', 'T2', 'D2'))
    assert len(repo.all_standards()) == 2


def test_standard_to_dict(repo: StandardsRepository) -> None:
    std = EngineeringStandard('S1', 'T1', 'D1', mandatory=True)
    data = std.to_dict()
    assert data['standard_id'] == 'S1'
    assert data['mandatory'] is True


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------


def test_add_and_get_pattern(repo: StandardsRepository) -> None:
    pat = Pattern('PAT-001', 'Repository Pattern', 'Abstraction layer for data access.', StandardCategory.ARCHITECTURE)
    repo.add_pattern(pat)
    result = repo.get_pattern('PAT-001')
    assert result is pat


def test_get_unknown_pattern_returns_none(repo: StandardsRepository) -> None:
    assert repo.get_pattern('UNKNOWN') is None


def test_search_patterns_by_name(repo: StandardsRepository) -> None:
    repo.add_pattern(Pattern('P1', 'Repository Pattern', 'desc'))
    repo.add_pattern(Pattern('P2', 'Factory Pattern', 'desc'))
    results = repo.search_patterns('repository')
    assert len(results) == 1
    assert results[0].pattern_id == 'P1'


def test_patterns_by_category(repo: StandardsRepository) -> None:
    repo.add_pattern(Pattern('P1', 'Singleton', 'desc', StandardCategory.ARCHITECTURE))
    repo.add_pattern(Pattern('P2', 'Prompt Chain', 'desc', StandardCategory.PROMPT_ENGINEERING))
    arch = repo.patterns_by_category(StandardCategory.ARCHITECTURE)
    assert len(arch) == 1


def test_pattern_to_dict(repo: StandardsRepository) -> None:
    pat = Pattern('P1', 'Observer', 'Event handling.', template='# template code')
    data = pat.to_dict()
    assert data['pattern_id'] == 'P1'
    assert data['has_template'] is True


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def test_summary(repo: StandardsRepository) -> None:
    repo.add_standard(EngineeringStandard('S1', 'T1', 'D1', StandardCategory.SECURITY, mandatory=True))
    repo.add_pattern(Pattern('P1', 'T1', 'D1', StandardCategory.ARCHITECTURE))
    summary = repo.summary()
    assert summary['standards_count'] == 1
    assert summary['patterns_count'] == 1
    assert summary['mandatory_standards'] == 1
    assert 'security' in summary['categories']
