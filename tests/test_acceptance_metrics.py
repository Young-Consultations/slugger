"""Tests for TASK-049: Acceptance Metrics."""

from __future__ import annotations

from validators.acceptance_metrics import AcceptanceMetricsCollector, MetricThreshold, ThresholdKind


def test_min_threshold_pass() -> None:
    collector = AcceptanceMetricsCollector()
    collector.declare(MetricThreshold('coverage', 80.0))
    collector.record('coverage', 92.5)
    report = collector.evaluate()
    assert report['passed'] is True
    assert report['evaluations'][0]['passed'] is True


def test_min_threshold_fail() -> None:
    collector = AcceptanceMetricsCollector()
    collector.declare(MetricThreshold('coverage', 80.0))
    collector.record('coverage', 70.0)
    report = collector.evaluate()
    assert report['passed'] is False


def test_max_threshold_pass() -> None:
    collector = AcceptanceMetricsCollector()
    collector.declare(MetricThreshold('error_rate', 5.0, kind=ThresholdKind.MAX))
    collector.record('error_rate', 3.0)
    assert collector.evaluate()['passed'] is True


def test_max_threshold_fail() -> None:
    collector = AcceptanceMetricsCollector()
    collector.declare(MetricThreshold('error_rate', 5.0, kind=ThresholdKind.MAX))
    collector.record('error_rate', 7.0)
    assert collector.evaluate()['passed'] is False


def test_missing_metric_fails_evaluation() -> None:
    collector = AcceptanceMetricsCollector()
    collector.declare(MetricThreshold('coverage', 80.0))
    report = collector.evaluate()
    assert report['passed'] is False
    assert 'coverage' in report['missing']


def test_average_evaluation() -> None:
    collector = AcceptanceMetricsCollector()
    collector.declare(MetricThreshold('latency', 100.0, kind=ThresholdKind.MAX))
    collector.record('latency', 90.0)
    collector.record('latency', 110.0)
    # Latest = 110 → fail
    assert collector.evaluate(use_average=False)['passed'] is False
    # Average = 100 → pass (boundary)
    assert collector.evaluate(use_average=True)['passed'] is True


def test_latest_and_average_helpers() -> None:
    collector = AcceptanceMetricsCollector()
    collector.record('x', 10.0)
    collector.record('x', 20.0)
    assert collector.latest('x') == 20.0
    assert collector.average('x') == 15.0


def test_no_thresholds_passes() -> None:
    collector = AcceptanceMetricsCollector()
    report = collector.evaluate()
    assert report['passed'] is True
    assert report['evaluations'] == []
