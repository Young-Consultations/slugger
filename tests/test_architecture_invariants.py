from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from models.project import Platform, ProjectBrief
from orchestrator.orchestrator import Slugger, _DEFAULT_WORKFLOW

ROOT = Path(__file__).resolve().parent.parent
LEGACY_ERROR = (
    "The 'full-sdlc' workflow has been superseded by 'full-sdlc-v2'. "
    "Resume existing runs using 'full-sdlc-v2' or start a new build."
)


def test_default_workflow_is_full_sdlc_v2() -> None:
    assert _DEFAULT_WORKFLOW == "full-sdlc-v2"


def test_adr_0017_exists() -> None:
    assert (ROOT / "docs" / "adr" / "0017-canonical-execution-path.md").exists()


def test_full_sdlc_v2_recipe_exists() -> None:
    assert (ROOT / "workflow" / "recipes" / "full-sdlc-v2.yaml").exists()


def test_legacy_full_sdlc_recipe_is_archived() -> None:
    assert not (ROOT / "workflow" / "recipes" / "full-sdlc.yaml").exists()
    assert (ROOT / "workflow" / "recipes" / "archived" / "full-sdlc.yaml").exists()


def test_build_rejects_legacy_full_sdlc_workflow() -> None:
    context = MagicMock()
    slugger = Slugger(context)
    brief = ProjectBrief(idea="Task tracker", platform=Platform.WEB)
    with pytest.raises(ValueError, match=re.escape(LEGACY_ERROR)):
        slugger.build(brief, workflow="full-sdlc")
    context.workflow_engine.run.assert_not_called()
