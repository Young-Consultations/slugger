"""Tests for Epic 6: prompt lifecycle."""

from __future__ import annotations

import pytest

from models.execution import ExecutionContext
from prompts.catalog import build_default_catalog
from prompts.lifecycle import (
    PromptApprovalStatus,
    PromptQualityScorer,
    PromptRegistry,
    PromptVersion,
)


# ---------------------------------------------------------------------------
# Quality Scorer
# ---------------------------------------------------------------------------


def test_scorer_high_quality_prompt() -> None:
    scorer = PromptQualityScorer()
    prompt = (
        "You are an expert Python engineer. "
        "Generate a FastAPI REST endpoint that:\n"
        "1. Accepts a POST request with JSON body\n"
        "2. Validates the input using Pydantic\n"
        "3. Returns a JSON response\n"
        "Return only the Python source code."
    )
    score = scorer.score(prompt)
    assert score >= 6.0


def test_scorer_empty_prompt_low_score() -> None:
    scorer = PromptQualityScorer()
    assert scorer.score("") == 0.0


def test_scorer_vague_prompt_lower_score() -> None:
    scorer = PromptQualityScorer()
    vague = "Do some stuff with things etc."
    clear = "Generate a Python function that validates an email address."
    assert scorer.score(clear) > scorer.score(vague)


def test_scorer_max_score_capped() -> None:
    scorer = PromptQualityScorer()
    long_prompt = (
        "You are a senior engineer. "
        "Generate a Python class that:\n"
        "1. Implements a repository pattern\n"
        "2. Must include type hints\n"
        "3. Must include docstrings\n"
        "4. Should return JSON format output\n"
        "Role: backend developer. Always include error handling. Never use global state."
    )
    score = scorer.score(long_prompt)
    assert 0.0 <= score <= 10.0


# ---------------------------------------------------------------------------
# PromptRegistry
# ---------------------------------------------------------------------------


@pytest.fixture()
def registry() -> PromptRegistry:
    return PromptRegistry()


def test_register_creates_v1(registry: PromptRegistry) -> None:
    v = registry.register(
        "req-prompt", "Requirements Prompt", "Generate requirements for..."
    )
    assert v.version == "1.0.0"
    assert v.prompt_id == "req-prompt"
    assert v.quality_score is not None


def test_update_bumps_minor_version(registry: PromptRegistry) -> None:
    registry.register(
        "req-prompt", "Requirements Prompt", "Generate requirements for..."
    )
    v2 = registry.update(
        "req-prompt",
        "Generate detailed requirements for...",
        change_notes="Added detail",
    )
    assert v2.version == "1.1.0"
    assert v2.change_notes == "Added detail"


def test_update_again_bumps_further(registry: PromptRegistry) -> None:
    registry.register("p", "P", "content")
    registry.update("p", "content v2")
    v3 = registry.update("p", "content v3")
    assert v3.version == "1.2.0"


def test_update_unknown_id_raises(registry: PromptRegistry) -> None:
    with pytest.raises(KeyError):
        registry.update("nonexistent", "content")


def test_latest_returns_most_recent(registry: PromptRegistry) -> None:
    registry.register("p", "P", "v1 content")
    registry.update("p", "v2 content")
    latest = registry.latest("p")
    assert latest is not None
    assert latest.version == "1.1.0"


def test_history_ordered_oldest_first(registry: PromptRegistry) -> None:
    registry.register("p", "P", "v1")
    registry.update("p", "v2")
    history = registry.history("p")
    assert len(history) == 2
    assert history[0].version == "1.0.0"
    assert history[1].version == "1.1.0"


def test_approve_sets_status(registry: PromptRegistry) -> None:
    registry.register("p", "P", "content")
    v = registry.approve("p", approver="alice")
    assert v.status == PromptApprovalStatus.APPROVED
    assert v.metadata.get("approved_by") == "alice"


def test_reject_sets_status(registry: PromptRegistry) -> None:
    registry.register("p", "P", "content")
    v = registry.reject("p", reason="needs work")
    assert v.status == PromptApprovalStatus.REJECTED
    assert v.metadata.get("rejection_reason") == "needs work"


def test_all_prompts_returns_latest_versions(registry: PromptRegistry) -> None:
    registry.register("p1", "P1", "content")
    registry.register("p2", "P2", "content")
    all_prompts = registry.all_prompts()
    assert len(all_prompts) == 2


def test_execution_context_records_prompt_provenance() -> None:
    context = ExecutionContext(
        project_id="project", workflow_name="workflow", step_name="step"
    )
    context.record_prompt(
        prompt_id="sdlc.requirements.v1",
        version="1.0.0",
        content_hash="abc123",
    )
    assert context.prompt_id == "sdlc.requirements.v1"
    assert context.prompt_version == "1.0.0"
    assert context.prompt_content_hash == "abc123"


def test_catalog_contains_all_production_prompts() -> None:
    catalog = build_default_catalog()
    for prompt_id in (
        "sdlc.product_vision.v1",
        "sdlc.requirements.v1",
        "sdlc.user_stories.v1",
        "sdlc.project_plan.v1",
    ):
        prompt = catalog.get(prompt_id)
        assert prompt is not None
        assert prompt.status == PromptApprovalStatus.APPROVED


def test_unapproved_prompt_status() -> None:
    draft = PromptVersion(prompt_id="draft", name="Draft", content="content")
    rejected = PromptVersion(
        prompt_id="rejected",
        name="Rejected",
        content="content",
        status=PromptApprovalStatus.REJECTED,
    )
    approved = PromptVersion(
        prompt_id="approved",
        name="Approved",
        content="content",
        status=PromptApprovalStatus.APPROVED,
    )

    assert draft.status == PromptApprovalStatus.DRAFT
    assert rejected.status == PromptApprovalStatus.REJECTED
    assert draft.status != PromptApprovalStatus.APPROVED
    assert rejected.status != PromptApprovalStatus.APPROVED
    assert approved.status == PromptApprovalStatus.APPROVED
