"""Tests for Epic 5: production readiness engine."""

from __future__ import annotations

import pytest

from validators.readiness import (
    CoverageGate,
    DocumentationGate,
    ProductionReadinessEngine,
    ReadinessLevel,
    ReleaseGateCollector,
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


def test_coverage_gate_non_positive_threshold_auto_passes() -> None:
    gate = CoverageGate(threshold=0.0, actual=-1.0)
    assert gate.passed is True


def test_security_gate_passed() -> None:
    gate = SecurityGate(findings_count=0, max_allowed=0)
    assert gate.passed is True


def test_security_gate_failed() -> None:
    gate = SecurityGate(findings_count=2, max_allowed=0)
    assert gate.passed is False


def test_doc_gate_completeness() -> None:
    gate = DocumentationGate(
        required_artifacts=["README", "CHANGELOG", "API_DOCS"],
        present_artifacts=["README", "CHANGELOG"],
    )
    assert gate.missing == ["API_DOCS"]
    assert gate.passed is False
    assert gate.completeness_pct == pytest.approx(66.7, abs=0.1)


def test_doc_gate_all_present() -> None:
    gate = DocumentationGate(
        required_artifacts=["README"],
        present_artifacts=["README"],
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
        documentation=DocumentationGate(
            required_artifacts=["README"], present_artifacts=["README"]
        ),
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
        documentation=DocumentationGate(
            required_artifacts=["README"], present_artifacts=["README"]
        ),
    )
    # Security gate (30 pts) fails — score at most 70
    assert report.score <= 70.0
    assert any("security" in n.lower() for n in report.notes)


def test_low_coverage_lowers_score(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=40.0),
        security=SecurityGate(findings_count=0, max_allowed=0),
        documentation=DocumentationGate(required_artifacts=[], present_artifacts=[]),
    )
    assert report.score < 100.0
    assert any("coverage" in n.lower() for n in report.notes)


def test_missing_docs_adds_note(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=85.0),
        security=SecurityGate(findings_count=0),
        documentation=DocumentationGate(
            required_artifacts=["README", "CHANGELOG"],
            present_artifacts=["README"],
        ),
    )
    assert any("Missing" in n for n in report.notes)


def test_readiness_level_not_ready(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=0.0),
        security=SecurityGate(findings_count=10, max_allowed=0),
        documentation=DocumentationGate(
            required_artifacts=["README"], present_artifacts=[]
        ),
        quality_gates_passed=0,
        quality_gates_total=10,
    )
    assert report.level == ReadinessLevel.NOT_READY


def test_readiness_level_needs_work(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=60.0),
        security=SecurityGate(findings_count=1, max_allowed=0),
        documentation=DocumentationGate(
            required_artifacts=["README"], present_artifacts=["README"]
        ),
        quality_gates_passed=3,
        quality_gates_total=5,
    )
    assert report.level in (
        ReadinessLevel.NEEDS_WORK,
        ReadinessLevel.READY,
        ReadinessLevel.NOT_READY,
    )


def test_report_to_dict(engine: ProductionReadinessEngine) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=80.0, actual=85.0),
        security=SecurityGate(findings_count=0),
        documentation=DocumentationGate(required_artifacts=[], present_artifacts=[]),
    )
    data = report.to_dict()
    assert "score" in data
    assert "level" in data
    assert "coverage" in data
    assert "security" in data
    assert "documentation" in data


def test_zero_coverage_threshold_does_not_divide_by_zero(
    engine: ProductionReadinessEngine,
) -> None:
    report = engine.evaluate(
        coverage=CoverageGate(threshold=0.0, actual=-10.0),
        security=SecurityGate(findings_count=0),
        documentation=DocumentationGate(required_artifacts=[], present_artifacts=[]),
    )
    assert report.score == 100.0


def test_failed_mandatory_gate_blocks_release() -> None:
    collector = ReleaseGateCollector("app-1", "run-1")
    collector.record_failed("build", "build failed")
    collector.record_passed("tests", "ev-tests")
    collector.record_passed("security", "ev-security")
    collector.record_passed("coverage", "ev-coverage")
    collector.record_passed("lint", "ev-lint")
    collector.record_passed("type", "ev-type")
    collector.record_passed("approvals", "ev-approvals")

    report = collector.evaluate()

    assert report.score > 80.0
    assert report.passed is False
    assert report.release_candidate is False
    assert report.mandatory_gates_failed == ["build"]


def test_readiness_invalidated_on_file_change() -> None:
    collector = ReleaseGateCollector("app-1", "run-1")
    collector.record_passed("build", "ev-build")
    collector.record_passed("tests", "ev-tests")
    collector.record_passed("security", "ev-security")
    collector.freeze_candidate({"src/app.py": "abc123"})

    report = collector.evaluate({"src/app.py": "def456"})

    assert report.invalidated is True
    assert report.passed is False
    assert "candidate_state" in report.blocking_gates


def test_all_gates_passing_produces_release_candidate() -> None:
    collector = ReleaseGateCollector("app-1", "run-1")
    collector.record_passed("build", "ev-build")
    collector.record_passed("tests", "ev-tests")
    collector.record_passed("security", "ev-security")
    collector.record_passed("coverage", "ev-coverage")
    collector.record_passed("lint", "ev-lint")
    collector.record_passed("type", "ev-type")
    collector.record_passed("approvals", "ev-approvals")
    checksums = {"src/app.py": "abc123"}
    collector.freeze_candidate(checksums)

    report = collector.evaluate(dict(checksums))

    assert report.passed is True
    assert report.release_candidate is True
    assert report.mandatory_gates_failed == []
    assert report.score == 100.0
