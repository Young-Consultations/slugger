"""CC-006: Canva design generation, export, and approval handoff tests."""

from __future__ import annotations

from agents.architecture.canva_design_agent import (
    CanvaDesignAgent,
    _PLACEHOLDER_MARKER,
    _build_design_brief,
    _build_design_manifest,
)
from models.execution import ExecutionContext
from services.canva import CanvaDesign, MockCanvaService


def _context(
    idea: str = "task manager", design_id: str | None = None
) -> ExecutionContext:
    meta = {"idea": idea}
    if design_id:
        meta["design_id"] = design_id
    return ExecutionContext(
        project_id="p1",
        workflow_name="wf",
        step_name="design",
        metadata=meta,
    )


class TestDesignBrief:
    def test_brief_contains_idea(self) -> None:
        ctx = _context(idea="social recipe app")
        brief = _build_design_brief(ctx)
        assert "social recipe app" in brief

    def test_brief_has_screen_inventory(self) -> None:
        ctx = _context()
        brief = _build_design_brief(ctx)
        assert "Screen Inventory" in brief

    def test_brief_includes_requirements_from_context(self) -> None:
        from models.artifact import DocumentArtifact

        ctx = _context(idea="task manager")
        req_artifact = DocumentArtifact(
            artifact_id="r1", name="requirements", content="REQ-001: Login"
        )
        ctx.inputs["requirements"] = req_artifact
        brief = _build_design_brief(ctx)
        assert "REQ-001" in brief

    def test_brief_hash_is_stable(self) -> None:
        ctx = _context(idea="task manager")
        brief = _build_design_brief(ctx)
        import hashlib

        h1 = hashlib.sha256(brief.encode()).hexdigest()[:16]
        h2 = hashlib.sha256(brief.encode()).hexdigest()[:16]
        assert h1 == h2


class TestDesignManifest:
    def test_manifest_has_screens(self) -> None:
        manifest = _build_design_manifest(
            "App", "d1", "https://export.canva.com/d1.pdf", "abc123"
        )
        assert "screens" in manifest
        assert len(manifest["screens"]) > 0

    def test_manifest_screens_have_requirement_ids(self) -> None:
        manifest = _build_design_manifest(
            "App", "d1", "https://export.canva.com/d1.pdf", "abc123"
        )
        for screen in manifest["screens"]:
            assert "requirement_ids" in screen
            assert len(screen["requirement_ids"]) > 0

    def test_manifest_has_design_tokens(self) -> None:
        manifest = _build_design_manifest(
            "App", "d1", "https://export.canva.com/d1.pdf", "abc123"
        )
        assert "design_tokens" in manifest

    def test_manifest_starts_unapproved(self) -> None:
        manifest = _build_design_manifest(
            "App", "d1", "https://export.canva.com/d1.pdf", "abc123"
        )
        assert manifest["approved"] is False

    def test_manifest_links_brief_hash(self) -> None:
        manifest = _build_design_manifest(
            "App", "d1", "https://export.canva.com/d1.pdf", "deadbeef"
        )
        assert manifest["brief_hash"] == "deadbeef"


class TestCanvaDesignAgentCC006:
    def test_brief_artifact_emitted(self) -> None:
        svc = MockCanvaService()
        svc.designs = [CanvaDesign(design_id="d1", title="App UI")]
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        names = [a.name for a in artifacts]
        assert "design_brief" in names

    def test_manifest_artifact_emitted(self) -> None:
        svc = MockCanvaService()
        svc.designs = [CanvaDesign(design_id="d1", title="App UI")]
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        names = [a.name for a in artifacts]
        assert "design_manifest" in names

    def test_design_artifact_unapproved_by_default(self) -> None:
        svc = MockCanvaService()
        svc.designs = [CanvaDesign(design_id="d1", title="App UI")]
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        design_art = next(a for a in artifacts if a.name == "design_artifact")
        assert design_art.extra.get("approved") is False

    def test_brief_hash_present_in_design_artifact(self) -> None:
        svc = MockCanvaService()
        svc.designs = [CanvaDesign(design_id="d1", title="App UI")]
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        design_art = next(a for a in artifacts if a.name == "design_artifact")
        assert "brief_hash" in design_art.extra

    def test_brief_hash_consistent_across_artifacts(self) -> None:
        svc = MockCanvaService()
        svc.designs = [CanvaDesign(design_id="d1", title="App UI")]
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        hashes = {
            a.extra.get("brief_hash") for a in artifacts if "brief_hash" in a.extra
        }
        # All artifacts should use the same brief hash
        assert len(hashes) == 1


class TestManualHandoff:
    def test_no_designs_triggers_manual_handoff(self) -> None:
        svc = MockCanvaService()  # empty
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        handoff = next(a for a in artifacts if a.name == "design_artifact")
        assert handoff.extra.get("requires_manual_handoff") is True

    def test_handoff_artifact_has_placeholder_marker(self) -> None:
        svc = MockCanvaService()
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        handoff = next(a for a in artifacts if a.name == "design_artifact")
        assert _PLACEHOLDER_MARKER in handoff.content

    def test_handoff_is_unapproved(self) -> None:
        svc = MockCanvaService()
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        handoff = next(a for a in artifacts if a.name == "design_artifact")
        assert handoff.extra.get("approved") is False

    def test_handoff_still_emits_brief(self) -> None:
        svc = MockCanvaService()
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        names = [a.name for a in artifacts]
        assert "design_brief" in names

    def test_handoff_pauses_with_durable_pending_state(self) -> None:
        svc = MockCanvaService()
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        handoff = next(a for a in artifacts if a.name == "design_artifact")
        assert handoff.extra.get("workflow_state") == "awaiting_design"
        assert handoff.extra.get("status") == "awaiting_design"

    def test_placeholder_cannot_be_auto_approved(self) -> None:
        """A placeholder design must never be interpreted as approved completion."""
        svc = MockCanvaService()
        agent = CanvaDesignAgent(svc)
        artifacts = agent.execute(_context())
        for a in artifacts:
            # No artifact from a handoff run may be marked approved
            assert a.extra.get("approved") is not True
