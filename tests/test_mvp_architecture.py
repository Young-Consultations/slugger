"""Architecture boundary tests for the MVP package."""

from __future__ import annotations

import ast
from pathlib import Path

MVP_ROOT = Path(__file__).resolve().parents[1] / "mvp"

PROHIBITED_IMPORTS = (
    "workflow.engine",
    "agents.registry",
    "services.canva",
    "agents.architecture.canva_design_agent",
    "workflow.approvals",
    "workflow.durable_approvals",
    "validators.readiness",
    "agents.operations.release_agent",
)

PROHIBITED_NAME_PARTS = (
    "canva",
    "approval",
    "readiness",
    "release_agent",
)


def _python_files() -> list[Path]:
    return sorted(path for path in MVP_ROOT.rglob("*.py") if path.is_file())


def _imported_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                modules.add(node.module)
    return modules


def test_mvp_package_exists() -> None:
    assert MVP_ROOT.is_dir()
    assert (MVP_ROOT / "__init__.py").is_file()


def test_mvp_does_not_import_prohibited_legacy_dependencies() -> None:
    violations: list[str] = []
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for module in _imported_modules(tree):
            if any(
                module == prohibited or module.startswith(f"{prohibited}.")
                for prohibited in PROHIBITED_IMPORTS
            ):
                violations.append(f"{path.relative_to(MVP_ROOT.parent)} imports {module}")
                continue
            if any(part in module.lower() for part in PROHIBITED_NAME_PARTS):
                violations.append(f"{path.relative_to(MVP_ROOT.parent)} imports {module}")

    assert violations == []
