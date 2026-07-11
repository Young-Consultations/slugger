"""Tests for TASK-065: Release Automation."""

from __future__ import annotations

import pytest

from scripts.release import bump_version, parse_version, ReleaseAutomation


def test_parse_version_basic() -> None:
    assert parse_version('1.2.3') == (1, 2, 3)
    assert parse_version('v0.1.0') == (0, 1, 0)
    assert parse_version('10.20.300') == (10, 20, 300)


def test_parse_version_invalid() -> None:
    with pytest.raises(ValueError):
        parse_version('not-a-version')


def test_bump_patch() -> None:
    assert bump_version('1.2.3', 'patch') == '1.2.4'


def test_bump_minor() -> None:
    assert bump_version('1.2.3', 'minor') == '1.3.0'


def test_bump_major() -> None:
    assert bump_version('1.2.3', 'major') == '2.0.0'


def test_bump_unknown_raises() -> None:
    with pytest.raises(ValueError, match='Unknown bump type'):
        bump_version('1.0.0', 'nano')


def test_current_version(tmp_path) -> None:
    pyproject = tmp_path / 'pyproject.toml'
    pyproject.write_text('[project]\nname = "slugger"\nversion = "0.5.0"\n', encoding='utf-8')
    automation = ReleaseAutomation(tmp_path, pyproject_path=pyproject)
    assert automation.current_version() == '0.5.0'


def test_update_version(tmp_path) -> None:
    pyproject = tmp_path / 'pyproject.toml'
    pyproject.write_text('[project]\nname = "slugger"\nversion = "0.5.0"\n', encoding='utf-8')
    automation = ReleaseAutomation(tmp_path, pyproject_path=pyproject)
    previous = automation.update_version('0.6.0')
    assert previous == '0.5.0'
    assert automation.current_version() == '0.6.0'


def test_generate_release_notes(tmp_path) -> None:
    pyproject = tmp_path / 'pyproject.toml'
    pyproject.write_text('[project]\nname = "slugger"\nversion = "0.5.0"\n', encoding='utf-8')
    automation = ReleaseAutomation(tmp_path, pyproject_path=pyproject)
    notes = automation.generate_release_notes('0.6.0', previous_version='0.5.0')
    assert notes.version == '0.6.0'
    assert '0.6.0' in notes.notes
    assert notes.previous_version == '0.5.0'


def test_prepare_release_bumps_and_generates(tmp_path) -> None:
    pyproject = tmp_path / 'pyproject.toml'
    pyproject.write_text('[project]\nname = "slugger"\nversion = "0.5.0"\n', encoding='utf-8')
    # Initialise a git repo so recent_commits doesn't error
    import subprocess
    subprocess.run(['git', 'init', str(tmp_path)], capture_output=True)
    automation = ReleaseAutomation(tmp_path, pyproject_path=pyproject)
    release_notes = automation.prepare_release('minor')
    assert release_notes.version == '0.6.0'
    assert automation.current_version() == '0.6.0'
