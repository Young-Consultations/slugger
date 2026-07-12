"""CC-002 regression tests: managed prompts and structured artifact contracts."""

from __future__ import annotations

import hashlib

import pytest

from prompts.catalog import (
    ARTIFACT_SCHEMAS,
    ArtifactSchema,
    PromptFrontmatter,
    SdlcPromptCatalog,
    build_default_catalog,
)
from prompts.lifecycle import PromptApprovalStatus
from validators import ArtifactSchemaValidator
from models.artifact import DocumentArtifact, ArtifactMetadata


# ---------------------------------------------------------------------------
# PromptFrontmatter
# ---------------------------------------------------------------------------


class TestPromptFrontmatter:
    def test_to_dict_contains_required_fields(self) -> None:
        fm = PromptFrontmatter(
            prompt_id="test.prompt.v1",
            version="1.0.0",
            inputs=["idea", "platform"],
            output_schema_id="requirements_v1",
        )
        d = fm.to_dict()
        assert d["prompt_id"] == "test.prompt.v1"
        assert d["version"] == "1.0.0"
        assert "idea" in d["inputs"]
        assert d["output_schema_id"] == "requirements_v1"

    def test_content_hash_deterministic(self) -> None:
        fm = PromptFrontmatter(prompt_id="x", version="1.0.0")
        content = "Test prompt content"
        h1 = fm.content_hash(content)
        h2 = fm.content_hash(content)
        expected = hashlib.sha256(content.encode()).hexdigest()
        assert h1 == h2 == expected

    def test_content_hash_changes_with_content(self) -> None:
        fm = PromptFrontmatter(prompt_id="x", version="1.0.0")
        assert fm.content_hash("v1") != fm.content_hash("v2")


# ---------------------------------------------------------------------------
# ArtifactSchema
# ---------------------------------------------------------------------------


class TestArtifactSchema:
    def test_validate_passes_when_sections_present(self) -> None:
        schema = ArtifactSchema(
            schema_id="test_v1",
            required_sections=["Idea", "Platform"],
        )
        errors = schema.validate("# Document\n\n**Idea:** x\n\n**Platform:** web")
        assert errors == []

    def test_validate_fails_when_section_missing(self) -> None:
        schema = ArtifactSchema(
            schema_id="test_v1",
            required_sections=["Idea", "Budget"],
        )
        errors = schema.validate("# Document\n\n**Idea:** x")
        assert len(errors) == 1
        assert "Budget" in errors[0]

    def test_empty_required_sections_always_passes(self) -> None:
        schema = ArtifactSchema(schema_id="empty_v1", required_sections=[])
        assert schema.validate("anything") == []


# ---------------------------------------------------------------------------
# SdlcPromptCatalog
# ---------------------------------------------------------------------------


class TestSdlcPromptCatalog:
    def test_all_sdlc_prompts_registered(self) -> None:
        catalog = SdlcPromptCatalog()
        for prompt_id in [
            "sdlc.product_vision.v1",
            "sdlc.requirements.v1",
            "sdlc.user_stories.v1",
            "sdlc.system_design.v1",
            "sdlc.adr.v1",
            "sdlc.project_plan.v1",
            "sdlc.code_manifest.v1",
            "sdlc.code_review.v1",
            "sdlc.qa_remediation.v1",
            "sdlc.security_remediation.v1",
            "sdlc.documentation.v1",
            "sdlc.release_readiness.v1",
        ]:
            pv = catalog.get(prompt_id)
            assert pv is not None, f"Prompt not found: {prompt_id}"

    def test_all_catalog_prompts_are_approved(self) -> None:
        catalog = SdlcPromptCatalog()
        for pv in catalog.all_approved():
            assert pv.status == PromptApprovalStatus.APPROVED

    def test_render_substitutes_variables(self) -> None:
        catalog = SdlcPromptCatalog()
        rendered = catalog.render(
            "sdlc.product_vision.v1",
            {"idea": "A task tracker", "platform": "web", "target_users": "developers"},
        )
        assert "A task tracker" in rendered
        assert "web" in rendered
        assert "{{ idea }}" not in rendered

    def test_render_raises_for_missing_inputs(self) -> None:
        catalog = SdlcPromptCatalog()
        with pytest.raises(ValueError, match="Missing required inputs"):
            catalog.render("sdlc.product_vision.v1", {})

    def test_render_raises_for_unknown_prompt(self) -> None:
        catalog = SdlcPromptCatalog()
        with pytest.raises(KeyError):
            catalog.render("nonexistent.prompt", {})

    def test_frontmatter_returned_for_known_prompt(self) -> None:
        catalog = SdlcPromptCatalog()
        fm = catalog.frontmatter("sdlc.requirements.v1")
        assert fm is not None
        assert "idea" in fm.inputs
        assert fm.output_schema_id == "requirements_v1"

    def test_content_hash_validation(self) -> None:
        catalog = SdlcPromptCatalog()
        pv = catalog.get("sdlc.requirements.v1")
        fm = catalog.frontmatter("sdlc.requirements.v1")
        actual_hash = fm.content_hash(pv.content)
        assert catalog.validate_content_hash("sdlc.requirements.v1", actual_hash)
        assert not catalog.validate_content_hash("sdlc.requirements.v1", "wrong_hash")

    def test_build_default_catalog_singleton(self) -> None:
        c1 = build_default_catalog()
        c2 = build_default_catalog()
        assert c1 is c2

    def test_artifact_validation_passes_for_matching_content(self) -> None:
        catalog = SdlcPromptCatalog()
        errors = catalog.validate_artifact(
            "product_vision",
            "# Vision\n\n**Idea:** test\n\n**Platform:** web",
        )
        assert errors == []

    def test_artifact_validation_fails_for_missing_section(self) -> None:
        catalog = SdlcPromptCatalog()
        errors = catalog.validate_artifact(
            "product_vision",
            "# Vision\n\nSome content without the required fields",
        )
        assert len(errors) > 0

    def test_artifact_validation_unknown_artifact_passes(self) -> None:
        catalog = SdlcPromptCatalog()
        errors = catalog.validate_artifact("unknown_artifact", "any content")
        assert errors == []


# ---------------------------------------------------------------------------
# ARTIFACT_SCHEMAS catalog completeness
# ---------------------------------------------------------------------------


class TestArtifactSchemaCatalog:
    def test_all_major_artifact_types_have_schemas(self) -> None:
        expected = [
            "product_vision",
            "requirements",
            "user_stories",
            "system_design",
            "adr",
            "project_plan",
            "generated_code",
            "code_review",
            "ci_cd_pipeline",
        ]
        for name in expected:
            assert name in ARTIFACT_SCHEMAS, f"Missing schema for: {name}"

    def test_all_schemas_have_valid_ids(self) -> None:
        for name, schema in ARTIFACT_SCHEMAS.items():
            assert schema.schema_id, f"Empty schema_id for: {name}"
            assert schema.schema_version, f"Empty schema_version for: {name}"


# ---------------------------------------------------------------------------
# ArtifactSchemaValidator integration
# ---------------------------------------------------------------------------


class TestArtifactSchemaValidator:
    def _make_artifact(self, name: str, content: str) -> DocumentArtifact:
        from uuid import uuid4

        return DocumentArtifact(
            artifact_id=str(uuid4()),
            name=name,
            content=content,
            metadata=ArtifactMetadata(),
        )

    def test_passes_for_valid_product_vision(self) -> None:
        v = ArtifactSchemaValidator()
        art = self._make_artifact(
            "product_vision",
            "# Vision\n\n**Idea:** A tracker\n\n**Platform:** web",
        )
        result = v.validate(art)
        assert result.valid

    def test_fails_for_invalid_product_vision(self) -> None:
        v = ArtifactSchemaValidator()
        art = self._make_artifact("product_vision", "# Just a heading")
        result = v.validate(art)
        assert not result.valid
        assert len(result.errors) > 0

    def test_passes_for_unknown_artifact_name(self) -> None:
        v = ArtifactSchemaValidator()
        art = self._make_artifact("nonexistent_artifact", "some content")
        result = v.validate(art)
        assert result.valid


# ---------------------------------------------------------------------------
# ExecutionContext prompt recording
# ---------------------------------------------------------------------------


class TestExecutionContextPromptRecording:
    def test_record_prompt_stores_provenance(self) -> None:
        from models.execution import ExecutionContext

        ctx = ExecutionContext(project_id="p", workflow_name="w", step_name="s")
        ctx.record_prompt(
            prompt_id="sdlc.requirements.v1",
            version="1.0.0",
            content_hash="abc123",
        )
        assert ctx.prompt_id == "sdlc.requirements.v1"
        assert ctx.prompt_version == "1.0.0"
        assert ctx.prompt_content_hash == "abc123"

    def test_execution_context_defaults_prompt_fields_to_none(self) -> None:
        from models.execution import ExecutionContext

        ctx = ExecutionContext(project_id="p", workflow_name="w", step_name="s")
        assert ctx.prompt_id is None
        assert ctx.prompt_version is None
        assert ctx.prompt_content_hash is None
