"""Tests for TASK-056: Dependency Updates."""

from __future__ import annotations

from services.dependency_checker import DependencyChecker


def _checker(versions: dict[str, str]) -> DependencyChecker:
    return DependencyChecker(version_map=versions)


def test_up_to_date() -> None:
    checker = _checker({"requests": "2.31.0"})
    statuses = checker.check({"requests": "2.31.0"})
    assert len(statuses) == 1
    assert statuses[0].up_to_date


def test_outdated() -> None:
    checker = _checker({"requests": "2.32.0"})
    statuses = checker.check({"requests": "2.31.0"})
    assert not statuses[0].up_to_date
    assert statuses[0].latest_version == "2.32.0"


def test_missing_package_error() -> None:
    checker = _checker({})
    statuses = checker.check({"requests": "2.31.0"})
    assert statuses[0].error != ""
    assert statuses[0].latest_version is None


def test_outdated_filter() -> None:
    checker = _checker({"a": "2.0", "b": "1.5"})
    outdated = checker.outdated({"a": "1.0", "b": "1.5"})
    assert len(outdated) == 1
    assert outdated[0].name == "a"


def test_summary_structure() -> None:
    checker = _checker({"req": "2.0", "pytest": "8.0"})
    summary = checker.summary({"req": "1.0", "pytest": "8.0"})
    assert summary["total"] == 2
    assert summary["outdated"] == 1
    assert summary["up_to_date"] == 1
    assert summary["errors"] == 0


def test_multiple_packages() -> None:
    checker = _checker({"a": "2.0", "b": "3.0", "c": "1.0"})
    statuses = checker.check({"a": "2.0", "b": "2.9", "c": "1.0"})
    names = {s.name for s in statuses}
    assert names == {"a", "b", "c"}
    up_to_date = {s.name for s in statuses if s.up_to_date}
    assert up_to_date == {"a", "c"}
