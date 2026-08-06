from __future__ import annotations

import scripts.validate_repo_governance as governance


def test_required_governance_files_exist() -> None:
    governance.validate_required_files()


def test_generated_demo_repository_is_not_local_submodule() -> None:
    governance.validate_no_submodule()


def test_workflows_are_least_privilege_and_pinned() -> None:
    governance.validate_workflows()


def test_documentation_keeps_generation_certification_and_release_distinct() -> None:
    governance.validate_docs_boundaries()
