import importlib
import sys
from pathlib import Path

from mvp import verify_cli
from tests.test_mvp_verify_existing import _project


def test_minimal_verify_cli_imports_without_legacy_bootstrap_modules() -> None:
    sys.modules.pop("cli.main", None)
    sys.modules.pop("requests", None)
    importlib.reload(verify_cli)
    assert "cli.main" not in sys.modules
    assert "requests" not in sys.modules


def test_minimal_verify_cli_valid_project_returns_zero(tmp_path: Path) -> None:
    project, root, name = _project(tmp_path)
    evidence = tmp_path / "evidence" / "verification-evidence.json"
    assert (
        verify_cli.main(
            [
                "--project-dir",
                str(project),
                "--project-name",
                name,
                "--workspace-root",
                str(root),
                "--evidence-file",
                str(evidence),
            ]
        )
        == 0
    )
    assert evidence.is_file()


def test_minimal_verify_cli_validation_failure_returns_nonzero(tmp_path: Path) -> None:
    project, root, name = _project(tmp_path)
    (project / "README.md").unlink()
    assert (
        verify_cli.main(
            [
                "--project-dir",
                str(project),
                "--project-name",
                name,
                "--workspace-root",
                str(root),
                "--evidence-file",
                str(tmp_path / "evidence.json"),
            ]
        )
        == 1
    )
