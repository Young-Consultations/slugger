"""Tests for TASK-060: Marketplace Packaging."""

from __future__ import annotations

from pathlib import Path

from plugins.packaging import MarketplacePackager
from plugins.sdk import PluginManifest


def _make_manifest(name: str = 'my-plugin', version: str = '1.0.0') -> PluginManifest:
    return PluginManifest(name=name, version=version, description='Test plugin', author='Tester')


def _create_plugin_dir(tmp_path: Path) -> Path:
    plugin_dir = tmp_path / 'src'
    plugin_dir.mkdir()
    (plugin_dir / 'main.py').write_text('def run(): pass\n', encoding='utf-8')
    (plugin_dir / 'README.md').write_text('# My Plugin\n', encoding='utf-8')
    (plugin_dir / '__pycache__').mkdir()
    (plugin_dir / '__pycache__' / 'main.cpython-311.pyc').write_bytes(b'fake')
    return plugin_dir


def test_package_creates_archive(tmp_path) -> None:
    plugin_dir = _create_plugin_dir(tmp_path)
    packager = MarketplacePackager(output_dir=tmp_path / 'dist')
    manifest = _make_manifest()
    result = packager.package(manifest, plugin_dir)
    assert result.archive_path.exists()
    assert result.archive_path.suffix == '.slugger-plugin'


def test_archive_name_includes_version(tmp_path) -> None:
    plugin_dir = _create_plugin_dir(tmp_path)
    packager = MarketplacePackager(output_dir=tmp_path / 'dist')
    result = packager.package(_make_manifest('cool-plugin', '2.3.0'), plugin_dir)
    assert 'cool-plugin-2.3.0' in result.archive_path.name


def test_pycache_excluded(tmp_path) -> None:
    plugin_dir = _create_plugin_dir(tmp_path)
    packager = MarketplacePackager(output_dir=tmp_path / 'dist')
    result = packager.package(_make_manifest(), plugin_dir)
    assert not any('__pycache__' in f for f in result.included_files)
    assert not any('.pyc' in f for f in result.included_files)


def test_source_files_included(tmp_path) -> None:
    plugin_dir = _create_plugin_dir(tmp_path)
    packager = MarketplacePackager(output_dir=tmp_path / 'dist')
    result = packager.package(_make_manifest(), plugin_dir)
    assert 'main.py' in result.included_files
    assert 'README.md' in result.included_files


def test_inspect_extracts_manifest(tmp_path) -> None:
    plugin_dir = _create_plugin_dir(tmp_path)
    packager = MarketplacePackager(output_dir=tmp_path / 'dist')
    manifest = _make_manifest('inspect-me', '3.1.0')
    result = packager.package(manifest, plugin_dir)
    extracted = MarketplacePackager.inspect(result.archive_path)
    assert extracted.name == 'inspect-me'
    assert extracted.version == '3.1.0'


def test_result_size_bytes(tmp_path) -> None:
    plugin_dir = _create_plugin_dir(tmp_path)
    packager = MarketplacePackager(output_dir=tmp_path / 'dist')
    result = packager.package(_make_manifest(), plugin_dir)
    assert result.size_bytes > 0
