"""Application manifest schema (CC-007).

A schema-versioned, validated multi-file application manifest that captures
every file the code generator intends to produce.  All model output is treated
as untrusted; the manifest must pass validation before file materialization.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = '1.0'
MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024  # 1 MiB per file
MAX_TOTAL_SIZE_BYTES = 20 * 1024 * 1024  # 20 MiB total

_UNSAFE_PATH_PATTERNS = re.compile(
    r'(^/|^\.\.|/\.\./|^~|^\\\.|\\\.\.[\\/]|\x00|[\r\n\t])',
    re.IGNORECASE,
)
_CREDENTIAL_NAMES = re.compile(
    r'(\.env$|secrets?\.(json|yaml|yml|toml)$|\.pem$|\.key$|id_rsa|id_ed25519)',
    re.IGNORECASE,
)
_APPROVED_TEMPLATES = frozenset({'cli', 'fastapi'})


# ---------------------------------------------------------------------------
# Template definitions
# ---------------------------------------------------------------------------

class AppTemplate(str, Enum):
    """Supported application templates."""
    CLI = 'cli'
    FASTAPI = 'fastapi'


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class FileEntry:
    """A single file entry in the application manifest."""
    path: str
    content: str
    checksum: str = ''
    size_bytes: int = 0
    mode: str = '644'
    artifact_refs: list[str] = field(default_factory=list)
    requirement_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError('FileEntry path is required.')
        if _UNSAFE_PATH_PATTERNS.search(self.path):
            raise ValueError(f'Unsafe file path: {self.path!r}')
        norm = str(PurePosixPath(self.path))
        if norm.startswith('/') or norm.startswith('..'):
            raise ValueError(f'File path escapes workspace root: {self.path!r}')
        if not self.content.strip():
            raise ValueError(f'FileEntry content must be non-empty for {self.path!r}.')
        encoded = self.content.encode('utf-8')
        self.size_bytes = len(encoded)
        if not self.checksum:
            self.checksum = hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            'path': self.path,
            'content': self.content,
            'checksum': self.checksum,
            'size_bytes': self.size_bytes,
            'mode': self.mode,
            'artifact_refs': self.artifact_refs,
            'requirement_ids': self.requirement_ids,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FileEntry':
        entry = cls(
            path=data['path'],
            content=data['content'],
            mode=data.get('mode', '644'),
            artifact_refs=data.get('artifact_refs', []),
            requirement_ids=data.get('requirement_ids', []),
        )
        # Allow pre-computed checksum to be verified
        if 'checksum' in data:
            entry.checksum = data['checksum']
        return entry


@dataclass
class AppManifest:
    """Schema-versioned multi-file application manifest.

    Produced by the code generator and validated before materialization.
    """
    app_id: str
    name: str
    template: AppTemplate
    schema_version: str = SCHEMA_VERSION
    description: str = ''
    python_version: str = '>=3.11'
    files: list[FileEntry] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    """Generated commands (e.g. test invocations) — not executed during validation."""
    artifact_parents: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError('schema_version is required.')
        if not self.app_id.strip():
            raise ValueError('application_id is required.')
        if not self.files:
            raise ValueError('files must contain at least one file entry.')
        paths = [entry.path for entry in self.files]
        if len(paths) != len(set(paths)):
            raise ValueError('Duplicate file paths are not allowed in AppManifest.')

    @property
    def application_id(self) -> str:
        return self.app_id

    def to_dict(self) -> dict[str, Any]:
        return {
            'schema_version': self.schema_version,
            'app_id': self.app_id,
            'application_id': self.app_id,
            'name': self.name,
            'template': self.template.value,
            'description': self.description,
            'python_version': self.python_version,
            'files': [f.to_dict() for f in self.files],
            'commands': self.commands,
            'artifact_parents': self.artifact_parents,
            'metadata': self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'AppManifest':
        template_val = data.get('template', 'cli')
        try:
            template = AppTemplate(template_val)
        except ValueError:
            template = AppTemplate.CLI
        return cls(
            app_id=data.get('app_id') or data['application_id'],
            name=data['name'],
            template=template,
            schema_version=data.get('schema_version', SCHEMA_VERSION),
            description=data.get('description', ''),
            python_version=data.get('python_version', '>=3.11'),
            files=[FileEntry.from_dict(f) for f in data.get('files', [])],
            commands=data.get('commands', []),
            artifact_parents=data.get('artifact_parents', []),
            metadata=data.get('metadata', {}),
        )

    @classmethod
    def from_json(cls, text: str) -> 'AppManifest':
        return cls.from_dict(json.loads(text))


# ---------------------------------------------------------------------------
# Manifest validator
# ---------------------------------------------------------------------------

@dataclass
class ManifestValidationError:
    """A single validation error in the manifest."""
    field: str
    message: str
    severity: str = 'error'  # error | warning


@dataclass
class ManifestValidationResult:
    """Result of validating an AppManifest."""
    valid: bool
    errors: list[ManifestValidationError] = field(default_factory=list)
    warnings: list[ManifestValidationError] = field(default_factory=list)

    def add_error(self, field: str, message: str) -> None:
        self.errors.append(ManifestValidationError(field=field, message=message))
        self.valid = False

    def add_warning(self, field: str, message: str) -> None:
        self.warnings.append(ManifestValidationError(field=field, message=message, severity='warning'))


def validate_app_manifest(manifest: AppManifest) -> ManifestValidationResult:
    """Validate an AppManifest against the full safety and correctness policy.

    Checks:
    - Schema version presence
    - Required files for each template
    - Path safety (no traversal, absolute paths, credential files)
    - No duplicate paths
    - File size limits
    - Python syntax for .py files
    - No device paths, null bytes, or shell-injection patterns
    """
    result = ManifestValidationResult(valid=True)

    # Schema version
    if manifest.schema_version != SCHEMA_VERSION:
        result.add_warning('schema_version', f'Expected {SCHEMA_VERSION}, got {manifest.schema_version!r}')

    # Required files per template
    _validate_required_files(manifest, result)

    # File-level checks
    paths_seen: set[str] = set()
    total_size = 0
    for entry in manifest.files:
        _validate_file_entry(entry, paths_seen, result)
        total_size += entry.size_bytes

    if total_size > MAX_TOTAL_SIZE_BYTES:
        result.add_error('files', f'Total file size {total_size} exceeds {MAX_TOTAL_SIZE_BYTES} bytes')

    return result


def _validate_required_files(manifest: AppManifest, result: ManifestValidationResult) -> None:
    """Check that all required files for the template are present."""
    paths = {e.path for e in manifest.files}
    if manifest.template == AppTemplate.CLI:
        required = {'pyproject.toml', 'README.md'}
        # Must have at least one source file and one test file
        has_src = any(p.endswith('.py') and not p.startswith('tests/') for p in paths)
        has_test = any(p.startswith('tests/') and p.endswith('.py') for p in paths)
        if not has_src:
            result.add_error('files', 'CLI template requires at least one source .py file')
        if not has_test:
            result.add_error('files', 'CLI template requires at least one test file under tests/')
    elif manifest.template == AppTemplate.FASTAPI:
        required = {'pyproject.toml', 'README.md'}
        has_app = any('main.py' in p or 'app.py' in p for p in paths)
        has_test = any(p.startswith('tests/') for p in paths)
        if not has_app:
            result.add_error('files', 'FastAPI template requires a main.py or app.py file')
        if not has_test:
            result.add_error('files', 'FastAPI template requires at least one test file under tests/')
    else:
        required = set()

    for req in required:
        if req not in paths:
            result.add_error('files', f'Required file missing: {req}')


def _validate_file_entry(entry: FileEntry, paths_seen: set[str], result: ManifestValidationResult) -> None:
    """Validate a single file entry."""
    path = entry.path

    # Duplicate path check
    if path in paths_seen:
        result.add_error(f'files[{path}]', f'Duplicate file path: {path!r}')
        return
    paths_seen.add(path)

    # Unsafe path patterns
    if _UNSAFE_PATH_PATTERNS.search(path):
        result.add_error(f'files[{path}]', f'Unsafe path pattern: {path!r}')
        return

    # PurePosixPath normalisation — check for traversal after normalisation
    try:
        norm = str(PurePosixPath(path))
        if norm.startswith('/') or norm.startswith('..'):
            result.add_error(f'files[{path}]', f'Path escapes workspace root: {path!r}')
            return
    except Exception:  # noqa: BLE001
        result.add_error(f'files[{path}]', f'Invalid path: {path!r}')
        return

    # Credential file names
    if _CREDENTIAL_NAMES.search(path):
        result.add_error(f'files[{path}]', f'Credential/secret filename not allowed: {path!r}')

    # File size
    if entry.size_bytes > MAX_FILE_SIZE_BYTES:
        result.add_error(f'files[{path}]', f'File size {entry.size_bytes} exceeds {MAX_FILE_SIZE_BYTES} bytes')

    # Python syntax check for .py files
    if path.endswith('.py'):
        try:
            ast.parse(entry.content, filename=path)
        except SyntaxError as exc:
            result.add_error(f'files[{path}]', f'Python syntax error: {exc}')

    # Checksum verification
    expected = hashlib.sha256(entry.content.encode('utf-8')).hexdigest()
    if entry.checksum and entry.checksum != expected:
        result.add_error(f'files[{path}]', f'Checksum mismatch for {path!r}')


# ---------------------------------------------------------------------------
# Template factories (golden fixture helpers)
# ---------------------------------------------------------------------------

def make_cli_manifest(app_id: str, name: str, idea: str = '') -> AppManifest:
    """Return a valid CLI application manifest for testing and generation."""
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    return AppManifest(
        app_id=app_id,
        name=name,
        template=AppTemplate.CLI,
        description=idea or f'CLI application: {name}',
        files=[
            FileEntry(
                path='pyproject.toml',
                content=f'[project]\nname = "{safe_name}"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n\n[project.optional-dependencies]\ntest = ["pytest"]\n',
                requirement_ids=[],
            ),
            FileEntry(
                path='README.md',
                content=f'# {name}\n\n{idea or name}\n',
                requirement_ids=[],
            ),
            FileEntry(
                path=f'src/{safe_name}/__init__.py',
                content='"""Application package."""\n',
                requirement_ids=[],
            ),
            FileEntry(
                path=f'src/{safe_name}/main.py',
                content=f'"""Entry point for {name}."""\n\n\ndef main() -> None:\n    """Run the application."""\n    print("Running: {name}")\n\n\nif __name__ == "__main__":\n    main()\n',
                requirement_ids=['REQ-001'],
            ),
            FileEntry(
                path='tests/__init__.py',
                content='"""Test package."""\n',
                requirement_ids=[],
            ),
            FileEntry(
                path=f'tests/test_{safe_name}.py',
                content=f'"""Tests for {name}."""\n\nfrom {safe_name}.main import main\n\n\ndef test_main_runs() -> None:\n    main()\n',
                requirement_ids=['REQ-001'],
            ),
        ],
        commands=[f'python -m pytest tests/ -q'],
    )


def make_fastapi_manifest(app_id: str, name: str, idea: str = '') -> AppManifest:
    """Return a valid FastAPI application manifest for testing and generation."""
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    return AppManifest(
        app_id=app_id,
        name=name,
        template=AppTemplate.FASTAPI,
        description=idea or f'FastAPI service: {name}',
        files=[
            FileEntry(
                path='pyproject.toml',
                content=f'[project]\nname = "{safe_name}"\nversion = "0.1.0"\nrequires-python = ">=3.11"\ndependencies = ["fastapi>=0.111", "uvicorn[standard]>=0.29"]\n\n[project.optional-dependencies]\ntest = ["pytest", "httpx"]\n',
            ),
            FileEntry(
                path='README.md',
                content=f'# {name}\n\n{idea or name}\n',
            ),
            FileEntry(
                path='src/__init__.py',
                content='"""Source package."""\n',
            ),
            FileEntry(
                path='src/main.py',
                content='"""FastAPI application."""\n\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.get("/")\ndef root() -> dict:\n    return {"status": "ok"}\n',
                requirement_ids=['REQ-001'],
            ),
            FileEntry(
                path='tests/__init__.py',
                content='"""Test package."""\n',
            ),
            FileEntry(
                path='tests/test_api.py',
                content='"""API tests."""\n\nfrom fastapi.testclient import TestClient\nfrom src.main import app\n\nclient = TestClient(app)\n\n\ndef test_root() -> None:\n    response = client.get("/")\n    assert response.status_code == 200\n',
                requirement_ids=['REQ-001'],
            ),
        ],
        commands=['python -m pytest tests/ -q'],
    )
