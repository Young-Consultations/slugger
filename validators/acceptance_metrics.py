"""Acceptance metrics — track and evaluate quantitative acceptance criteria.

:class:`AcceptanceMetricsCollector` accumulates numeric metric samples during
a workflow run and evaluates them against declared thresholds.  This enables
data-driven *definition of done* checks beyond binary pass/fail quality gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ThresholdKind(str, Enum):
    """Direction of a threshold comparison."""

    MIN = "min"  # metric value must be >= threshold
    MAX = "max"  # metric value must be <= threshold
    EXACT = "exact"  # metric value must equal threshold


@dataclass
class MetricThreshold:
    """A declared acceptance threshold for a named metric.

    Parameters
    ----------
    metric_name:
        Name of the metric (e.g. ``'test_coverage_pct'``).
    threshold:
        Numeric acceptance boundary.
    kind:
        How to compare the observed value against *threshold*.
    description:
        Human-readable explanation.
    """

    metric_name: str
    threshold: float
    kind: ThresholdKind = ThresholdKind.MIN
    description: str = ""


@dataclass
class MetricEvaluation:
    """Result of evaluating one metric against its threshold."""

    metric_name: str
    observed: float
    threshold: float
    kind: ThresholdKind
    passed: bool
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "observed": self.observed,
            "threshold": self.threshold,
            "kind": self.kind.value,
            "passed": self.passed,
            "description": self.description,
        }


class AcceptanceMetricsCollector:
    """Collect metric samples and evaluate them against thresholds.

    Examples
    --------
    >>> collector = AcceptanceMetricsCollector()
    >>> collector.declare(MetricThreshold('test_coverage_pct', 80.0))
    >>> collector.record('test_coverage_pct', 92.5)
    >>> report = collector.evaluate()
    >>> report['passed']
    True
    """

    def __init__(self) -> None:
        self._thresholds: dict[str, MetricThreshold] = {}
        self._samples: dict[str, list[float]] = {}

    # ------------------------------------------------------------------
    # Declaration / recording
    # ------------------------------------------------------------------

    def declare(self, threshold: MetricThreshold) -> None:
        """Register a threshold.  Replaces any previous threshold for the metric."""
        self._thresholds[threshold.metric_name] = threshold

    def record(self, metric_name: str, value: float) -> None:
        """Append a sample for *metric_name*."""
        self._samples.setdefault(metric_name, []).append(value)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def latest(self, metric_name: str) -> float | None:
        """Return the most recently recorded value for *metric_name*."""
        samples = self._samples.get(metric_name)
        return samples[-1] if samples else None

    def average(self, metric_name: str) -> float | None:
        """Return the mean of all recorded samples for *metric_name*."""
        samples = self._samples.get(metric_name)
        return sum(samples) / len(samples) if samples else None

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, use_average: bool = False) -> dict[str, Any]:
        """Evaluate all declared thresholds against recorded metrics.

        Parameters
        ----------
        use_average:
            When ``True``, compare the *average* of recorded samples;
            otherwise compare the *latest* sample.

        Returns
        -------
        dict
            ``{'passed': bool, 'evaluations': list[dict], 'missing': list[str]}``
        """
        evaluations: list[MetricEvaluation] = []
        missing: list[str] = []

        for name, threshold in self._thresholds.items():
            observed = self.average(name) if use_average else self.latest(name)
            if observed is None:
                missing.append(name)
                continue

            if threshold.kind == ThresholdKind.MIN:
                passed = observed >= threshold.threshold
            elif threshold.kind == ThresholdKind.MAX:
                passed = observed <= threshold.threshold
            else:  # EXACT
                passed = observed == threshold.threshold

            evaluations.append(
                MetricEvaluation(
                    metric_name=name,
                    observed=observed,
                    threshold=threshold.threshold,
                    kind=threshold.kind,
                    passed=passed,
                    description=threshold.description,
                )
            )

        all_passed = not missing and all(e.passed for e in evaluations)
        return {
            "passed": all_passed,
            "evaluations": [e.to_dict() for e in evaluations],
            "missing": missing,
        }
