"""CC-007 and CC-008: App manifest validation and workspace materialization tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from models.app_manifest import (
    AppManifest,
    AppTemplate,
    FileEntry,
    make_cli_manifest,
    make_fastapi_manifest,
    validate_app_manifest,
)
from materializer import MaterializationResult, ProjectMaterializer, WorkspaceState


# ---------------------------------------------------------------------------
# CC-007: AppManifest schema and validation tests
# ---------------------------------------------------------------------------

class TestAppManifestSchema:
    def test_file_entry_computes_checksum(self) -> None:
        entry = FileEntry(path='main.py', content='print("hello")\n')
        import hashlib
        expected = hashlib.sha256(b'print("hello")\n').hexdigest()
        assert entry.checksum == expected

    def test_file_entry_computes_size(self) -> None:
        content = 'hello world'
        entry = FileEntry(path='foo.txt', content=content)
        assert entry.size_bytes == len(content.encode('utf-8'))

    def test_manifest_to_json_roundtrip(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp', 'task tracker')
        json_str = manifest.to_json()
        restored = AppManifest.from_json(json_str)
        assert restored.app_id == manifest.app_id
        assert len(restored.files) == len(manifest.files)

    def test_manifest_schema_version_preserved(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp')
        assert manifest.schema_version == '1.0'

    def test_manifest_has_commands(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp')
        assert len(manifest.commands) >= 1

    def test_fastapi_manifest_valid(self) -> None:
        manifest = make_fastapi_manifest('app-2', 'MyAPI', 'REST API')
        result = validate_app_manifest(manifest)
        assert result.valid, result.errors

    def test_cli_manifest_valid(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp', 'task tracker')
        result = validate_app_manifest(manifest)
        assert result.valid, result.errors


class TestManifestValidation:
    def test_rejects_absolute_path(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp')
        manifest.files.append(FileEntry(path='/etc/passwd', content='root:x:0:0'))
        result = validate_app_manifest(manifest)
        assert not result.valid
        assert any('/etc/passwd' in e.message for e in result.errors)

    def test_rejects_traversal_path(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp')
        manifest.files.append(FileEntry(path='../../evil.sh', content='rm -rf /'))
        result = validate_app_manifest(manifest)
        assert not result.valid

    def test_rejects_duplicate_paths(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp')
        manifest.files.append(FileEntry(path='pyproject.toml', content='[project]\nname="dup"\n'))
        result = validate_app_manifest(manifest)
        assert not result.valid
        assert any('Duplicate' in e.message for e in result.errors)

    def test_rejects_credential_filename(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp')
        manifest.files.append(FileEntry(path='secrets.json', content='{"key": "val"}'))
        result = validate_app_manifest(manifest)
        assert not result.valid
        assert any('credential' in e.message.lower() for e in result.errors)

    def test_rejects_python_syntax_error(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp')
        bad_file = FileEntry(path='src/bad.py', content='def broken(:\n    pass\n')
        manifest.files.append(bad_file)
        result = validate_app_manifest(manifest)
        assert not result.valid
        assert any('syntax' in e.message.lower() for e in result.errors)

    def test_rejects_missing_test_files(self) -> None:
        manifest = AppManifest(
            app_id='app-1',
            name='NoTests',
            template=AppTemplate.CLI,
            files=[
                FileEntry(path='pyproject.toml', content='[project]\nname = "notests"\n'),
                FileEntry(path='README.md', content='# NoTests\n'),
                FileEntry(path='src/main.py', content='def main(): pass\n'),
                # No tests/ directory
            ],
        )
        result = validate_app_manifest(manifest)
        assert not result.valid
        assert any('test' in e.message.lower() for e in result.errors)

    def test_rejects_checksum_mismatch(self) -> None:
        manifest = make_cli_manifest('app-1', 'MyApp')
        # Tamper with checksum
        entry = manifest.files[0]
        entry.checksum = 'deadbeef' * 8  # wrong checksum
        result = validate_app_manifest(manifest)
        assert not result.valid
        assert any('Checksum' in e.message for e in result.errors)


# ---------------------------------------------------------------------------
# CC-008: ProjectMaterializer workspace tests
# ---------------------------------------------------------------------------

class TestProjectMaterializer:
    def test_materializes_valid_manifest(self, tmp_path: Path) -> None:
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        manifest = make_cli_manifest('app-1', 'MyApp', 'task tracker')
        result = mat.materialize(manifest)
        assert result.success
        assert result.workspace is not None
        assert result.workspace.state == WorkspaceState.ACTIVE

    def test_all_files_written(self, tmp_path: Path) -> None:
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        manifest = make_cli_manifest('app-1', 'MyApp')
        result = mat.materialize(manifest)
        assert result.success
        ws_root = result.workspace.root
        for entry in manifest.files:
            assert (ws_root / entry.path).exists(), f'{entry.path!r} not found'

    def test_checksums_verified(self, tmp_path: Path) -> None:
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        manifest = make_cli_manifest('app-1', 'MyApp')
        result = mat.materialize(manifest)
        assert result.success
        # Inventory checksums match file content
        for inv in result.workspace.inventory:
            file_path = result.workspace.root / inv.path
            import hashlib
            actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
            assert actual == inv.checksum

    def test_slugger_marker_written(self, tmp_path: Path) -> None:
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        manifest = make_cli_manifest('app-1', 'MyApp')
        result = mat.materialize(manifest)
        assert (result.workspace.root / '.slugger').exists()

    def test_rejects_invalid_manifest(self, tmp_path: Path) -> None:
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        manifest = AppManifest(
            app_id='bad',
            name='Bad',
            template=AppTemplate.CLI,
            files=[FileEntry(path='/etc/passwd', content='root:x:0:0')],
        )
        result = mat.materialize(manifest)
        assert not result.success
        assert result.errors

    def test_idempotent_resume(self, tmp_path: Path) -> None:
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        manifest = make_cli_manifest('app-1', 'MyApp')
        mat.materialize(manifest)
        # Resume should succeed and not corrupt files
        result = mat.resume(manifest)
        assert result.success
        ws_root = result.workspace.root
        for entry in manifest.files:
            assert (ws_root / entry.path).exists()

    def test_cleanup_removes_workspace(self, tmp_path: Path) -> None:
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        manifest = make_cli_manifest('app-1', 'MyApp')
        result = mat.materialize(manifest)
        ws_root = result.workspace.root
        assert ws_root.exists()
        mat.cleanup('app-1')
        assert not ws_root.exists()

    def test_path_traversal_denied(self, tmp_path: Path) -> None:
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        manifest = AppManifest(
            app_id='app-1',
            name='Traversal',
            template=AppTemplate.CLI,
            files=[
                FileEntry(path='pyproject.toml', content='[project]\nname = "t"\n'),
                FileEntry(path='README.md', content='# T\n'),
                FileEntry(path='src/main.py', content='def main(): pass\n'),
                FileEntry(path='tests/__init__.py', content=''),
                FileEntry(path='tests/test_t.py', content='def test_x(): pass\n'),
                FileEntry(path='../../evil.txt', content='boom'),
            ],
        )
        result = mat.materialize(manifest)
        # Validation should block this before materialization
        assert not result.success

    def test_existing_non_slugger_dir_rejected(self, tmp_path: Path) -> None:
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        # Manually create an active dir without the .slugger marker
        active_dir = tmp_path / 'workspaces' / 'active' / 'app-1'
        active_dir.mkdir(parents=True)
        (active_dir / 'user_file.txt').write_text('important')
        manifest = make_cli_manifest('app-1', 'MyApp')
        result = mat.materialize(manifest)
        assert not result.success
        # User's file must not be overwritten
        assert (active_dir / 'user_file.txt').read_text() == 'important'


class TestGoldenFixtures:
    """Tests using golden fixture manifests (valid and invalid)."""

    def test_task_tracker_cli_manifest(self) -> None:
        manifest = make_cli_manifest('task-tracker-1', 'Task Tracker', 'CLI task tracking app')
        result = validate_app_manifest(manifest)
        assert result.valid

    def test_fastapi_service_manifest(self) -> None:
        manifest = make_fastapi_manifest('api-svc-1', 'Task API', 'REST API for task management')
        result = validate_app_manifest(manifest)
        assert result.valid

    def test_malformed_no_files(self) -> None:
        manifest = AppManifest(
            app_id='empty',
            name='Empty',
            template=AppTemplate.CLI,
            files=[],
        )
        result = validate_app_manifest(manifest)
        assert not result.valid

    def test_malformed_no_pyproject(self) -> None:
        manifest = AppManifest(
            app_id='nopyproject',
            name='NoPyProject',
            template=AppTemplate.CLI,
            files=[
                FileEntry(path='src/main.py', content='def main(): pass\n'),
                FileEntry(path='tests/test_main.py', content='def test_x(): pass\n'),
            ],
        )
        result = validate_app_manifest(manifest)
        assert not result.valid
        assert any('pyproject.toml' in e.message for e in result.errors)
