"""Manually gated real-Codex MVP demo test."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


pytestmark = pytest.mark.real_codex

_IDEA = """Create a Python command-line application named hello-codex.
Requirements:
- Provide a `greet NAME` command.
- The command prints exactly `Hello, NAME!`.
- Provide conventional `--help` output.
- Use argparse.
- Use a src-based package layout.
- Include pytest tests.
- Use no runtime dependencies.
- Do not use the network.
"""


def _codex_preflight() -> tuple[bool, str]:
    try:
        subprocess.run(
            ["codex", "--version"],
            text=True,
            capture_output=True,
            timeout=30,
            check=True,
        )
        subprocess.run(
            ["codex", "login", "status"],
            text=True,
            capture_output=True,
            timeout=30,
            check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    return True, ""


def test_real_codex_generates_valid_hello_codex_demo(tmp_path: Path) -> None:
    if os.environ.get("RUN_REAL_CODEX") != "1":
        pytest.skip("Set RUN_REAL_CODEX=1 to run the real Codex integration test")
    ok, reason = _codex_preflight()
    if not ok:
        pytest.skip(f"Codex authentication preflight failed: {reason}")

    env = os.environ.copy()
    env["SLUGGER_HOME"] = str(tmp_path / "slugger-home")
    env["SLUGGER_MVP_SKIP_PUBLISH"] = "1"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "cli.main",
            "mvp",
            "build",
            _IDEA,
            "--name",
            "hello-codex",
            "--template",
            "cli",
            "--repo",
            "local/hello-codex-demo",
        ],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        text=True,
        capture_output=True,
        timeout=1200,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout
    result = json.loads(completed.stdout)
    workspace = Path(result["workspace_path"])
    assert result["status"] == "ready_to_publish"
    assert result["publication_skipped"] is True
    assert result["source_integrity_result"] == "passed"
    assert result["changed_source_paths"] == []
    assert result["generated_files"] > 0
    assert result["codex_session_id"]
    assert result["validation_passed"] is True
    assert result["test_passed"] is True
    assert result["smoke_passed"] is True
    assert workspace.is_dir()
    for path in workspace.rglob("*"):
        assert path.resolve().is_relative_to(workspace.resolve())

    python = (
        workspace
        / ".venv"
        / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    demo = subprocess.run(
        [str(python), "-m", "hello_codex.main", "greet", "Joseph"],
        cwd=workspace,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert demo.returncode == 0, demo.stderr
    assert demo.stdout.strip() == "Hello, Joseph!"
