"""Tests for TASK-063: Sample Projects."""

from __future__ import annotations

from pathlib import Path

EXAMPLES_ROOT = Path(__file__).parents[1] / "examples"


def test_hello_world_readme_exists() -> None:
    readme = EXAMPLES_ROOT / "hello_world" / "README.md"
    assert readme.exists(), f"hello_world/README.md not found at {readme}"


def test_hello_world_run_script_exists() -> None:
    script = EXAMPLES_ROOT / "hello_world" / "run.py"
    assert script.exists(), f"hello_world/run.py not found at {script}"


def test_custom_agent_readme_exists() -> None:
    readme = EXAMPLES_ROOT / "custom_agent" / "README.md"
    assert readme.exists()


def test_custom_agent_run_script_exists() -> None:
    script = EXAMPLES_ROOT / "custom_agent" / "run.py"
    assert script.exists()


def test_examples_root_readme_exists() -> None:
    readme = EXAMPLES_ROOT / "README.md"
    assert readme.exists()


def test_hello_world_run_script_is_valid_python() -> None:
    import ast

    script = EXAMPLES_ROOT / "hello_world" / "run.py"
    ast.parse(script.read_text(encoding="utf-8"))  # raises if invalid


def test_custom_agent_run_script_is_valid_python() -> None:
    import ast

    script = EXAMPLES_ROOT / "custom_agent" / "run.py"
    ast.parse(script.read_text(encoding="utf-8"))
