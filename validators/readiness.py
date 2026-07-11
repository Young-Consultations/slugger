"""Production Readiness Engine.

Aggregates quality signals from multiple sources — test coverage, security
scans, documentation completeness, and quality gate results — into a single
:class:`ReadinessReport` with a numeric readiness score.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReadinessLevel(str, Enum):
    """Production readiness verdict."""

    NOT_READY = 'not_ready'
    NEEDS_WORK = 'needs_work'
    READY = 'ready'
    EXCELLENT = 'excellent'


@dataclass
class CoverageGate:
    """Minimum test-coverage threshold gate.

    Parameters
    ----------
    threshold:
        Minimum required coverage percentage (0–100).
    actual:
        Measured coverage percentage.  Set to ``None`` if not yet measured.
    """

    threshold: float = 80.0
    actual: float | None = None

    @property
    def passed(self) -> bool:
        return self.actual is not None and self.actual >= self.threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            'threshold': self.threshold,
            'actual': self.actual,
            'passed': self.passed,
        }


@dataclass
class SecurityGate:
    """Security scan result gate.

    Parameters
    ----------
    findings_count:
        Number of HIGH or CRITICAL security findings.
    max_allowed:
        Maximum number of HIGH/CRITICAL findings permitted.
    """

    findings_count: int = 0
    max_allowed: int = 0

    @property
    def passed(self) -> bool:
        return self.findings_count <= self.max_allowed

    def to_dict(self) -> dict[str, Any]:
        return {
            'findings_count': self.findings_count,
            'max_allowed': self.max_allowed,
            'passed': self.passed,
        }


@dataclass
class DocumentationGate:
    """Documentation completeness gate.

    Parameters
    ----------
    required_artifacts:
        Names of documentation artifacts that must be present.
    present_artifacts:
        Names of documentation artifacts that were actually produced.
    """

    required_artifacts: list[str] = field(default_factory=list)
    present_artifacts: list[str] = field(default_factory=list)

    @property
    def missing(self) -> list[str]:
        return [a for a in self.required_artifacts if a not in self.present_artifacts]

    @property
    def passed(self) -> bool:
        return len(self.missing) == 0

    @property
    def completeness_pct(self) -> float:
        if not self.required_artifacts:
            return 100.0
        present = sum(1 for a in self.required_artifacts if a in self.present_artifacts)
        return round(present / len(self.required_artifacts) * 100, 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            'required': list(self.required_artifacts),
            'present': list(self.present_artifacts),
            'missing': self.missing,
            'completeness_pct': self.completeness_pct,
            'passed': self.passed,
        }


@dataclass
class ReadinessReport:
    """Aggregated production readiness report.

    Parameters
    ----------
    score:
        Numeric readiness score 0–100.
    level:
        Qualitative readiness verdict.
    coverage:
        Coverage gate result.
    security:
        Security gate result.
    documentation:
        Documentation completeness gate result.
    quality_gates_passed:
        Number of workflow quality gates that passed.
    quality_gates_total:
        Total number of workflow quality gates evaluated.
    notes:
        Human-readable notes and recommendations.
    """

    score: float
    level: ReadinessLevel
    coverage: CoverageGate
    security: SecurityGate
    documentation: DocumentationGate
    quality_gates_passed: int = 0
    quality_gates_total: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'score': self.score,
            'level': self.level.value,
            'coverage': self.coverage.to_dict(),
            'security': self.security.to_dict(),
            'documentation': self.documentation.to_dict(),
            'quality_gates_passed': self.quality_gates_passed,
            'quality_gates_total': self.quality_gates_total,
            'notes': list(self.notes),
        }


class ProductionReadinessEngine:
    """Compute a production readiness score from multiple quality signals.

    Each gate contributes a weighted portion to the overall score:

    * Coverage gate: 30 points
    * Security gate: 30 points
    * Documentation gate: 20 points
    * Quality gates: 20 points

    Examples
    --------
    >>> engine = ProductionReadinessEngine()
    >>> coverage = CoverageGate(threshold=80.0, actual=90.0)
    >>> security = SecurityGate(findings_count=0, max_allowed=0)
    >>> docs = DocumentationGate(required_artifacts=['README'], present_artifacts=['README'])
    >>> report = engine.evaluate(coverage=coverage, security=security, documentation=docs)
    >>> report.score
    100.0
    >>> report.level
    <ReadinessLevel.EXCELLENT: 'excellent'>
    """

    def evaluate(
        self,
        coverage: CoverageGate,
        security: SecurityGate,
        documentation: DocumentationGate,
        quality_gates_passed: int = 0,
        quality_gates_total: int = 0,
    ) -> ReadinessReport:
        """Compute the readiness report from individual gate results.

        Returns
        -------
        ReadinessReport
            A fully populated readiness report.
        """
        notes: list[str] = []
        score = 0.0

        # Coverage gate — 30 points
        if coverage.passed:
            score += 30.0
        elif coverage.actual is not None:
            # Partial credit proportional to how close actual is to threshold
            partial = min(coverage.actual / coverage.threshold, 1.0) * 30.0
            score += partial
            notes.append(
                f'Test coverage {coverage.actual:.1f}% is below threshold {coverage.threshold:.1f}%.'
            )
        else:
            notes.append('Test coverage has not been measured.')

        # Security gate — 30 points
        if security.passed:
            score += 30.0
        else:
            excess = security.findings_count - security.max_allowed
            notes.append(f'{excess} unresolved HIGH/CRITICAL security finding(s) detected.')

        # Documentation gate — 20 points
        doc_score = (documentation.completeness_pct / 100.0) * 20.0
        score += doc_score
        if not documentation.passed:
            notes.append(f'Missing documentation: {", ".join(documentation.missing)}.')

        # Quality gates — 20 points
        if quality_gates_total > 0:
            gate_score = (quality_gates_passed / quality_gates_total) * 20.0
            score += gate_score
            if quality_gates_passed < quality_gates_total:
                failed = quality_gates_total - quality_gates_passed
                notes.append(f'{failed} quality gate(s) failed.')
        else:
            # No gates configured — award full points (no evidence of failure)
            score += 20.0

        score = round(min(score, 100.0), 1)
        level = self._level(score)
        return ReadinessReport(
            score=score,
            level=level,
            coverage=coverage,
            security=security,
            documentation=documentation,
            quality_gates_passed=quality_gates_passed,
            quality_gates_total=quality_gates_total,
            notes=notes,
        )

    @staticmethod
    def _level(score: float) -> ReadinessLevel:
        if score >= 95.0:
            return ReadinessLevel.EXCELLENT
        if score >= 75.0:
            return ReadinessLevel.READY
        if score >= 50.0:
            return ReadinessLevel.NEEDS_WORK
        return ReadinessLevel.NOT_READY
