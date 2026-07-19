"""Tests for the MVP basic project runner."""

from __future__ import annotations

from pathlib import Path

from mvp.basic_runner import BasicRunner, _minimal_environment
from mvp.integrations.codex import FakeMvpCodexAdapter
from mvp.models import CheckResult, MvpProjectRequest
from mvp.workspace import WorkspaceManager


def _request() -> MvpProjectRequest:
    return MvpProjectRequest(
        "Create a CLI task tracker", "task-tracker", "cli", "owner/repo"
    )


def _workspace(tmp_path: Path):
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("run-runner")
    FakeMvpCodexAdapter(manager).generate_project(_request(), workspace)
    return manager, workspace


def test_real_runner_installs_tests_and_smokes_valid_cli_project(
    tmp_path: Path,
) -> None:
    manager, workspace = _workspace(tmp_path)

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    assert not any(
        check.name == "create_environment"
        and "--system-site-packages" in check.details.get("command", [])
        for check in result.checks
    )
    assert [check.name for check in result.checks] == [
        "create_environment",
        "provision_build_tools",
        "install_verifier_dependencies",
        "install_project",
        "verify_pytest_available",
        "run_tests",
        "cli_smoke",
    ]
    assert any(
        check.name == "run_tests" and " passed" in check.details.get("stdout", "")
        for check in result.checks
    )


def test_test_failure_blocks_smoke_and_publication_preconditions(
    tmp_path: Path,
) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "tests" / "test_main.py").write_text(
        "def test_bad():\n    assert False\n", encoding="utf-8"
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    assert not result.passed
    assert any(
        check.name == "run_tests" and not check.passed for check in result.checks
    )
    assert any(
        check.name == "cli_smoke" and not check.passed and "Skipped" in check.message
        for check in result.checks
    )


def test_install_failure_blocks_later_phases(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "pyproject.toml").write_text("not toml = [", encoding="utf-8")

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    assert not result.passed
    assert any(
        check.name == "install_project" and not check.passed for check in result.checks
    )
    assert any(
        check.name == "run_tests" and not check.passed and "Skipped" in check.message
        for check in result.checks
    )


def test_normal_build_preserves_broken_backend_install_failure(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "pyproject.toml").write_text(
        (
            "[build-system]\n"
            "requires = []\n"
            'build-backend = "does.not.exist"\n\n'
            "[project]\n"
            'name = "task-tracker"\n'
            'version = "0.1.0"\n'
            'requires-python = ">=3.11"\n'
            "dependencies = []\n"
        ),
        encoding="utf-8",
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    install_check = next(
        check for check in result.checks if check.name == "install_project"
    )
    assert not result.passed
    assert not install_check.passed
    assert install_check.details.get("returncode", 0) != 0
    assert install_check.name == "install_project"
    assert install_check.details.get("manual_source_install") is None
    assert "manual_source_install_error" not in install_check.details
    assert "approved_dependency_copy" not in install_check.details
    assert isinstance(install_check.details.get("stdout"), str)
    assert isinstance(install_check.details.get("stderr"), str)
    assert install_check.details.get("stdout") or install_check.details.get("stderr")


def test_build_tool_verification_uses_metadata_without_importing_packages(
    tmp_path: Path, monkeypatch
) -> None:
    manager, workspace = _workspace(tmp_path)
    runner = BasicRunner(manager, timeout_seconds=180)
    captured: dict[str, object] = {}

    def fake_run_phase(name, command, workspace_path, **kwargs):
        captured["command"] = command
        return CheckResult(
            name,
            True,
            "metadata ok",
            {
                "command": command,
                "returncode": 0,
                "stdout": '{"pip": "25.0.1", "setuptools": "80.9.0", "wheel": "0.45.1"}\n',
                "stderr": "",
            },
        )

    monkeypatch.setattr(runner, "_run_phase", fake_run_phase)

    provision = runner._verify_build_tools(
        workspace.path / ".venv" / "bin" / "python",
        workspace.path,
        {
            "expected_versions": {
                "pip": "25.0.1",
                "setuptools": "80.9.0",
                "wheel": "0.45.1",
            }
        },
    )

    script = captured["command"][-1]  # type: ignore[index]
    assert "importlib.metadata" in script
    assert "import pip" not in script
    assert "import setuptools" not in script
    assert provision.details["expected_versions"]["setuptools"] == "80.9.0"
    assert provision.details["installed_versions"]["setuptools"] == "80.9.0"


def test_failed_build_tool_provisioning_reports_structured_diagnostics(
    tmp_path: Path, monkeypatch
) -> None:
    manager, workspace = _workspace(tmp_path)
    missing_wheelhouse = tmp_path / "empty-wheelhouse"
    missing_wheelhouse.mkdir()
    monkeypatch.setenv("SLUGGER_WHEELHOUSE", str(missing_wheelhouse))

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    provision = next(
        check for check in result.checks if check.name == "provision_build_tools"
    )
    assert not provision.passed
    assert provision.details["expected_versions"] == {
        "pip": "25.0.1",
        "setuptools": "80.9.0",
        "wheel": "0.45.1",
    }
    assert provision.details["failed_provisioning_command"]
    assert isinstance(provision.details["returncode"], int)
    assert isinstance(provision.details["stdout"], str)
    assert isinstance(provision.details["stderr"], str)
    assert "approved_dependency_copy" not in provision.details


def _all_commands(result):
    return [
        check.details.get("command", [])
        for check in result.checks
        if check.details.get("command")
    ]


def test_generated_environment_does_not_inherit_ambient_pytest(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    pyproject = workspace.path / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text(encoding="utf-8").replace(
            next(
                line
                for line in pyproject.read_text(encoding="utf-8").splitlines()
                if line.startswith("test = [")
            ),
            "test = []",
        ),
        encoding="utf-8",
    )
    backend = workspace.path / "slugger_mvp_backend.py"
    backend.write_text(
        backend.read_text(encoding="utf-8").replace(
            "INCLUDE_PYTEST_EXTRA = True", "INCLUDE_PYTEST_EXTRA = False"
        ),
        encoding="utf-8",
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    create = next(
        check for check in result.checks if check.name == "create_environment"
    )
    pytest_check = next(
        check for check in result.checks if check.name == "verify_pytest_available"
    )
    tests = next(check for check in result.checks if check.name == "run_tests")
    assert "--system-site-packages" not in create.details["command"]
    assert pytest_check.passed
    assert tests.passed


def test_minimal_environment_does_not_expose_host_site_packages(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("PYTHONPATH", "/host/site-packages")
    monkeypatch.setenv("PIP_NO_BUILD_ISOLATION", "1")

    env = _minimal_environment(tmp_path)

    assert "PYTHONPATH" not in env
    assert "PIP_NO_BUILD_ISOLATION" not in env
    assert env["PYTHONNOUSERSITE"] == "1"


def test_standard_setuptools_backend_installs_in_isolated_venv(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "pyproject.toml").write_text(
        (
            "[build-system]\n"
            'requires = ["setuptools>=68", "wheel"]\n'
            'build-backend = "setuptools.build_meta"\n\n'
            "[project]\n"
            'name = "task-tracker"\n'
            'version = "0.1.0"\n'
            'requires-python = ">=3.11"\n'
            "dependencies = []\n\n"
            "[project.optional-dependencies]\n"
            'test = ["pytest>=8,<10"]\n\n'
            "[tool.setuptools.packages.find]\n"
            'where = ["src"]\n'
        ),
        encoding="utf-8",
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    install_check = next(
        check for check in result.checks if check.name == "install_project"
    )
    assert result.passed
    assert install_check.passed
    assert ".[test]" in install_check.details.get("command", [])
    assert "--no-build-isolation" in install_check.details.get("command", [])
    assert "--no-deps" in install_check.details.get("command", [])


def test_missing_pytest_configuration_causes_controlled_failure(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    pyproject = workspace.path / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text(encoding="utf-8").replace(
            next(
                line
                for line in pyproject.read_text(encoding="utf-8").splitlines()
                if line.startswith("test = [")
            ),
            "test = []",
        ),
        encoding="utf-8",
    )
    backend = workspace.path / "slugger_mvp_backend.py"
    backend.write_text(
        backend.read_text(encoding="utf-8").replace(
            "INCLUDE_PYTEST_EXTRA = True", "INCLUDE_PYTEST_EXTRA = False"
        ),
        encoding="utf-8",
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    assert result.passed
    assert [check.name for check in result.checks] == [
        "create_environment",
        "provision_build_tools",
        "install_verifier_dependencies",
        "install_project",
        "verify_pytest_available",
        "run_tests",
        "cli_smoke",
    ]
    install_check = next(
        check for check in result.checks if check.name == "install_project"
    )
    pytest_check = next(
        check for check in result.checks if check.name == "verify_pytest_available"
    )
    assert install_check.passed
    assert install_check.details.get("command", [])[-1] == "."
    assert pytest_check.passed


def test_smoke_failure_blocks_success_preconditions(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    package_dir = workspace.path / "src" / "task_tracker"
    (package_dir / "main.py").write_text(
        "from __future__ import annotations\n\ndef build_parser():\n    return None\n\ndef main(argv=None):\n    return 0\n\nif __name__ == '__main__':\n    raise SystemExit(7)\n",
        encoding="utf-8",
    )
    (workspace.path / "tests" / "test_main.py").write_text(
        "def test_ok():\n    assert True\n", encoding="utf-8"
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    assert not result.passed
    assert next(check for check in result.checks if check.name == "run_tests").passed
    assert not next(
        check for check in result.checks if check.name == "cli_smoke"
    ).passed


def test_every_generated_project_command_uses_venv_python(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    venv_python = str(
        workspace.path
        / ".venv"
        / ("Scripts/python.exe" if __import__("os").name == "nt" else "bin/python")
    )
    commands = {check.name: check.details.get("command", []) for check in result.checks}
    assert commands["install_project"][:3] == [venv_python, "-m", "pip"]
    assert "--system-site-packages" not in commands["create_environment"]
    assert commands["verify_pytest_available"][:2] == [venv_python, "-c"]
    assert commands["run_tests"][:3] == [venv_python, "-m", "pytest"]
    assert commands["cli_smoke"][:2] == [venv_python, "-m"]


def test_real_pytest_fails_when_no_tests_are_collected(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "tests" / "test_main.py").write_text(
        "class Helper:\n    def test_hidden(self):\n        assert False\n",
        encoding="utf-8",
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    tests = next(check for check in result.checks if check.name == "run_tests")
    assert not tests.passed
    assert "no tests ran" in tests.details.get("stdout", "")


def test_real_pytest_runs_class_based_tests(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "tests" / "test_main.py").write_text(
        "class TestMain:\n    def test_bad(self):\n        assert False\n",
        encoding="utf-8",
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    tests = next(check for check in result.checks if check.name == "run_tests")
    assert not tests.passed
    assert "failed" in tests.details.get("stdout", "")


def test_cli_smoke_accepts_standard_argparse_module_help_without_project_name(
    tmp_path: Path,
) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "src" / "task_tracker" / "main.py").write_text(
        "from __future__ import annotations\n"
        "import argparse\n\n"
        "def build_parser():\n"
        "    parser = argparse.ArgumentParser(description='Task tracker CLI')\n"
        "    parser.add_argument('--version', action='store_true')\n"
        "    return parser\n\n"
        "def main(argv=None):\n"
        "    build_parser().parse_args(argv)\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n",
        encoding="utf-8",
    )
    (workspace.path / "tests" / "test_main.py").write_text(
        "def test_ok():\n    assert True\n", encoding="utf-8"
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    smoke = next(check for check in result.checks if check.name == "cli_smoke")
    assert smoke.passed
    assert "usage" in smoke.details.get("stdout", "")


def test_cli_smoke_requires_meaningful_help_output(tmp_path: Path) -> None:
    manager, workspace = _workspace(tmp_path)
    (workspace.path / "src" / "task_tracker" / "main.py").write_text(
        "def main(argv=None):\n    return 0\nif __name__ == '__main__':\n    raise SystemExit(main())\n",
        encoding="utf-8",
    )
    (workspace.path / "tests" / "test_main.py").write_text(
        "def test_ok():\n    assert True\n", encoding="utf-8"
    )

    result = BasicRunner(manager, timeout_seconds=180).run(_request(), workspace)

    smoke = next(check for check in result.checks if check.name == "cli_smoke")
    assert not smoke.passed
    assert smoke.details.get("missing_stdout")


def test_verifier_versions_stay_aligned_across_constraints_runner_and_dockerfile() -> (
    None
):
    constraints = Path("constraints-ci.txt").read_text(encoding="utf-8")
    dockerfile = Path("docker/mvp-verifier.Dockerfile").read_text(encoding="utf-8")
    runner_source = Path("mvp/basic_runner.py").read_text(encoding="utf-8")
    for requirement in [
        "pip==25.0.1",
        "setuptools==80.9.0",
        "wheel==0.45.1",
        "pytest==8.3.5",
    ]:
        name = requirement.split("==", 1)[0]
        assert requirement in constraints
        assert f"{name}==" not in dockerfile
        assert f"{name}==" not in runner_source
    assert "--requirement /tmp/slugger-constraints-ci.txt" in dockerfile
    assert "--constraint /tmp/slugger-constraints-ci.txt" in dockerfile
    assert "constraints-ci.txt" in runner_source
