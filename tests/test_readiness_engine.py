"""Tests for Epic 5: production readiness engine."""

from __future__ import annotations

import pytest

from validators.readiness import (
    CoverageGate,
    DocumentationGate,
    ProductionReadinessEngine,
    ReadinessLevel,
    SecurityGate,
)


@pytest.fixture()
def engine() -> ProductionReadinessEngine:
    return ProductionReadinessEngine()


# ---------------------------------------------------------------------------
# Individual gates
# ---------------------------------------------------------------------------


def test_coverage_gate_passed() -> None:
    gate = CoverageGate(threshold=80.0, actual=90.0)
    assert gate.passed is True


def test_coverage_gate_failed() -> None:
    gate = CoverageGate(threshold=80.0, actual=60.0)
    assert gate.passed is False


def test_coverage_gate_not_measured() -> None:
    gate = CoverageGate(threshold=80.0)
    assert gate.passed is False


def test_security_gate_passed() -> None:
    gate = SecurityGate(findings_count=0, max_allowed=0)
    assert gate.passed is True


def test_security_gate_failed() -> None:
    gate = SecurityGate(findings_count=2, max_allowed=0)
    assert gate.passed is False


def test_doc_gate_completeness() -> None:
    gate = DocumentationGate(
        required_artifacts=['README', 'CHANGELOG', 'API_DOCS'],
        present_artifacts=['README', 'CHANGELOG'],
    )
    assert gate.missing == ['API_DOCS']
    assert gate.passed is False
    assert gate.completeness_pct == pytest.approx(66.7, abs=0.1)


def test_doc_gate_all_present() -> None:
    gate = DocumentationGate(
        required_artifacts=['README'],
        present_artifacts=['README'],
    )
    assert gate.passed is True
    assert gate.completeness_pct == 100.0


def test_doc_gate_no_requirements() -> None:
    gate = DocumentationGate()
    assert gate.passed is True
    assert gate.completeness_pct == 100.0


# ---------------------------------------------------------------------------
# Engine evaluation
# ---------------------------------------------------------------------------


def test_perfect_readiness_score(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=100.0),
        security=SecurityGate(findings_count=0, max_allowed=0),
        documentation=DocumentationGate(required_artifacts=['README'], present_artifacts=['README']),
        quality_gates_passed=5,
        quality_gates_total=5,
    )
    assert report.score == 100.0
    assert report.level == ReadinessLevel.EXCELLENT
    assert report.notes == []


def test_failed_security_lowers_score(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=90.0),
        security=SecurityGate(findings_count=3, max_allowed=0),
        documentation=DocumentationGate(required_artifacts=['README'], present_artifacts=['README']),
    )
    # Security gate (30 pts) fails — score at most 70
    assert report.score <= 70.0
    assert any('security' in n.lower() for n in report.notes)


def test_low_coverage_lowers_score(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=40.0),
        security=SecurityGate(findings_count=0, max_allowed=0),
        documentation=DocumentationGate(required_artifacts=[], present_artifacts=[]),
    )
    assert report.score < 100.0
    assert any('coverage' in n.lower() for n in report.notes)


def test_missing_docs_adds_note(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=85.0),
        security=SecurityGate(findings_count=0),
        documentation=DocumentationGate(
            required_artifacts=['README', 'CHANGELOG'],
            present_artifacts=['README'],
        ),
    )
    assert any('Missing' in n for n in report.notes)


def test_readiness_level_not_ready(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=0.0),
        security=SecurityGate(findings_count=10, max_allowed=0),
        documentation=DocumentationGate(required_artifacts=['README'], present_artifacts=[]),
        quality_gates_passed=0,
        quality_gates_total=10,
    )
    assert report.level == ReadinessLevel.NOT_READY


def test_readiness_level_needs_work(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=60.0),
        security=SecurityGate(findings_count=1, max_allowed=0),
        documentation=DocumentationGate(required_artifacts=['README'], present_artifacts=['README']),
        quality_gates_passed=3,
        quality_gates_total=5,
    )
    assert report.level in (ReadinessLevel.NEEDS_WORK, ReadinessLevel.READY, ReadinessLevel.NOT_READY)


def test_report_to_dict(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=85.0),
        security=SecurityGate(findings_count=0),
        documentation=DocumentationGate(required_artifacts=[], present_artifacts=[]),
    )
    data = report.to_dict()
    assert 'score' in data
    assert 'level' in data
    assert 'coverage' in data
    assert 'security' in data
    assert 'documentation' in data
