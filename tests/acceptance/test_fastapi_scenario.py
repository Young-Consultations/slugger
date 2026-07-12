"""Offline acceptance scenario: FastAPI service application."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from models.app_manifest import (
    AppManifest,
    AppTemplate,
    FileEntry,
    validate_app_manifest,
)
from models.artifact import DocumentArtifact
from models.artifact_store_sqlite import SQLiteArtifactStore
from orchestrator.orchestrator import _DEFAULT_WORKFLOW


class TestFastAPIScenario:
    """End-to-end offline acceptance for a FastAPI service."""

    def test_default_workflow_is_canonical(self) -> None:
        assert _DEFAULT_WORKFLOW == "full-sdlc-v2"

    def test_app_manifest_validates_fastapi_files(self) -> None:
        manifest = AppManifest(
            app_id="fastapi-demo",
            name="FastAPI Demo",
            template=AppTemplate.FASTAPI,
            schema_version="1.0",
            files=[
                FileEntry(
                    path="pyproject.toml",
                    content='[project]\nname = "fastapi-demo"\nversion = "0.1.0"\ndependencies = ["fastapi", "uvicorn"]\n',
                ),
                FileEntry(path="README.md", content="# FastAPI Demo\n"),
                FileEntry(
                    path="src/main.py",
                    content="from fastapi import FastAPI\n\napp = FastAPI()\n",
                ),
                FileEntry(
                    path="tests/test_api.py",
                    content="def test_placeholder() -> None:\n    assert True\n",
                ),
            ],
        )

        validation = validate_app_manifest(manifest)
        assert validation.valid, f"Validation errors: {validation.errors}"

    def test_app_manifest_rejects_absolute_path(self) -> None:
        with pytest.raises(ValueError):
            FileEntry(path="/etc/passwd", content="evil")

    def test_app_manifest_rejects_traversal(self) -> None:
        with pytest.raises(ValueError):
            FileEntry(path="../outside.py", content="evil")

    def test_canonical_recipe_file_valid_yaml(self) -> None:
        recipe = (
            Path(__file__).resolve().parents[2]
            / "workflow"
            / "recipes"
            / "full-sdlc-v2.yaml"
        )
        with recipe.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        assert data["name"] == "full-sdlc-v2"
        assert "steps" in data
        assert len(data["steps"]) > 5

    def test_sqliteartifactstore_roundtrip(self, tmp_path: Path) -> None:
        store = SQLiteArtifactStore(db_path=tmp_path / "artifacts.db")
        artifact = DocumentArtifact(
            artifact_id="workflow-1:step-1:vision",
            name="vision",
            content="The product vision content",
        )

        store.create(artifact)
        result = store.get("workflow-1:step-1:vision")

        assert result is not None
        assert result.content == "The product vision content"
