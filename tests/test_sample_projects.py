"""Tests for TASK-063: Sample Projects."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

EXAMPLES_ROOT = Path(__file__).parents[1] / "examples"
RUNNABLE_EXAMPLES = (
    "hello_world",
    "custom_agent",
    "custom_provider",
    "workflow_customization",
)


def test_examples_root_readme_exists() -> None:
    readme = EXAMPLES_ROOT / "README.md"
    assert readme.exists()


def test_runnable_examples_include_readmes_and_scripts() -> None:
    for example in RUNNABLE_EXAMPLES:
        example_dir = EXAMPLES_ROOT / example
        assert (example_dir / "README.md").exists(), f"{example}/README.md not found"
        assert (example_dir / "run.py").exists(), f"{example}/run.py not found"


def test_runnable_example_scripts_are_valid_python() -> None:
    for example in RUNNABLE_EXAMPLES:
        script = EXAMPLES_ROOT / example / "run.py"
        ast.parse(script.read_text(encoding="utf-8"))  # raises if invalid


def test_runnable_examples_execute_successfully() -> None:
    for example in RUNNABLE_EXAMPLES:
        script = EXAMPLES_ROOT / example / "run.py"
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=EXAMPLES_ROOT / example,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, (
            f"{example}/run.py failed with exit code {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert result.stdout.strip(), f"{example}/run.py did not produce output"


def test_workflow_customization_yaml_exists() -> None:
    workflow = EXAMPLES_ROOT / "workflow_customization" / "custom-workflow.yaml"
    assert workflow.exists()
