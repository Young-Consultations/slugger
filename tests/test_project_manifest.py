"""Tests for TASK-041: Project Manifest."""

from __future__ import annotations

import pytest

from models.manifest import ManifestBuildConfig, ManifestDependency, ProjectManifest


def _sample_manifest() -> ProjectManifest:
    return ProjectManifest(
        project_id='p-123',
        name='MyApp',
        version='1.2.3',
        description='A test project',
        dependencies=[ManifestDependency(name='requests', version='2.31.0')],
        dev_dependencies=[ManifestDependency(name='pytest', version='8.0.0')],
        build=ManifestBuildConfig(coding_agent='codex', platform='web'),
        tags=['demo'],
        metadata={'owner': 'alice'},
    )


def test_manifest_round_trip_dict() -> None:
    manifest = _sample_manifest()
    data = manifest.to_dict()
    restored = ProjectManifest.from_dict(data)
    assert restored.project_id == manifest.project_id
    assert restored.name == manifest.name
    assert restored.version == manifest.version
    assert len(restored.dependencies) == 1
    assert restored.dependencies[0].name == 'requests'
    assert restored.tags == ['demo']
    assert restored.metadata == {'owner': 'alice'}


def test_manifest_file_round_trip(tmp_path) -> None:
    manifest = _sample_manifest()
    path = tmp_path / 'manifest.yaml'
    manifest.save(path)
    loaded = ProjectManifest.load(path)
    assert loaded.project_id == manifest.project_id
    assert loaded.build.platform == 'web'


def test_manifest_defaults() -> None:
    manifest = ProjectManifest(project_id='x', name='X')
    assert manifest.version == '0.1.0'
    assert manifest.dependencies == []
    assert manifest.build.coding_agent == 'codex'


def test_dependency_extras() -> None:
    dep = ManifestDependency(name='pandas', version='2.0.0', extras=['sql', 'excel'])
    manifest = ProjectManifest(project_id='q', name='Q', dependencies=[dep])
    data = manifest.to_dict()
    assert data['dependencies'][0]['extras'] == ['sql', 'excel']
    restored = ProjectManifest.from_dict(data)
    assert restored.dependencies[0].extras == ['sql', 'excel']
