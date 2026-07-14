"""Golden MVP acceptance tests for the task-tracker CLI scenario."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from mvp.basic_runner import BasicRunner
from mvp.build_service import DefaultMvpBuildService
from mvp.integrations.codex import (
    FakeMvpCodexAdapter,
    MvpCodexAdapter,
    MvpCodexGenerationResult,
    _minimal_build_backend,
    _result_after_generation,
    package_name_for_project,
    render_prompt,
)
from mvp.integrations.github import FakeMvpGitHubPublisher
from mvp.models import MvpProjectRequest, MvpRunStatus
from mvp.project_validator import ProjectValidator
from mvp.run_repository import SQLiteMvpRunRepository
from mvp.workspace import MvpWorkspace, WorkspaceManager, WorkspaceSafetyError


GOLDEN_IDEA = "Create a CLI task tracker with add, list, and done commands"


def _request() -> MvpProjectRequest:
    return MvpProjectRequest(
        idea=GOLDEN_IDEA,
        project_name="task-tracker",
        template="cli",
        github_repository="mightyjoe909/task-tracker",
    )


def _service(
    tmp_path: Path,
    codex_adapter: MvpCodexAdapter | None = None,
    *,
    github_fail: bool = False,
) -> tuple[DefaultMvpBuildService, WorkspaceManager, FakeMvpGitHubPublisher]:
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    publisher = FakeMvpGitHubPublisher(fail=github_fail)
    service = DefaultMvpBuildService(
        run_repository=SQLiteMvpRunRepository(tmp_path / "runs.sqlite3"),
        workspace_manager=workspace_manager,
        codex_adapter=codex_adapter or TaskTrackerCodexAdapter(workspace_manager),
        project_validator=ProjectValidator(workspace_manager),
        basic_runner=BasicRunner(workspace_manager),
        github_publisher=publisher,
    )
    return service, workspace_manager, publisher


class TaskTrackerCodexAdapter(FakeMvpCodexAdapter):
    """Fake Codex adapter that creates the golden task-tracker project."""

    def __init__(
        self,
        workspace_manager: WorkspaceManager,
        *,
        invalid_python: bool = False,
        failing_tests: bool = False,
    ) -> None:
        super().__init__(workspace_manager)
        self.invalid_python = invalid_python
        self.failing_tests = failing_tests

    def generate_project(
        self,
        request: MvpProjectRequest,
        workspace: MvpWorkspace,
    ) -> MvpCodexGenerationResult:
        package_name = package_name_for_project(request.project_name)
        files = _task_tracker_files(request, package_name)
        if self.invalid_python:
            files[f"src/{package_name}/main.py"] = "def broken(:\n"
        if self.failing_tests:
            files["tests/test_main.py"] += (
                "\ndef test_intentional_failure():\n    assert False\n"
            )
        for relative_path, content in files.items():
            path = self.workspace_manager.resolve_generated_path(
                workspace, relative_path
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        prompt_hash = hashlib.sha256(render_prompt(request).encode("utf-8")).hexdigest()
        return _result_after_generation(
            request=request,
            workspace=workspace,
            workspace_manager=self.workspace_manager,
            prompt_hash=prompt_hash,
            codex_session_id=None,
            commands=(),
        )


def _task_tracker_files(
    request: MvpProjectRequest, package_name: str
) -> dict[str, str]:
    return {
        "README.md": f"# {request.project_name}\n\n{request.idea}\n",
        "pyproject.toml": (
            "[build-system]\nrequires = []\nbuild-backend = 'slugger_mvp_backend'\nbackend-path = ['.']\n\n"
            "[project]\n"
            f"name = '{request.project_name}'\nversion = '0.1.0'\nrequires-python = '>=3.11'\n"
            'dependencies = []\n\n[project.optional-dependencies]\ntest = ["pytest>=8,<10"]\n'
        ),
        "slugger_mvp_backend.py": _minimal_build_backend(
            request.project_name, include_pytest_extra=True
        ),
        f"src/{package_name}/__init__.py": "__all__ = ['main']\n",
        f"src/{package_name}/main.py": """from __future__ import annotations

import argparse

_TASKS: list[dict[str, object]] = []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="task-tracker")
    subparsers = parser.add_subparsers(dest="command", required=False)
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("title")
    subparsers.add_parser("list")
    done_parser = subparsers.add_parser("done")
    done_parser.add_argument("task_id", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "add":
        _TASKS.append({"title": args.title, "done": False})
        print(f"Added: {args.title}")
    elif args.command == "list":
        for index, task in enumerate(_TASKS, start=1):
            marker = "x" if task["done"] else " "
            print(f"{index}. [{marker}] {task['title']}")
    elif args.command == "done":
        if args.task_id < 1 or args.task_id > len(_TASKS):
            raise SystemExit("Unknown task")
        _TASKS[args.task_id - 1]["done"] = True
        print(f"Done: {args.task_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""",
        "tests/test_main.py": f"""from {package_name}.main import _TASKS, build_parser, main


def setup_function():
    _TASKS.clear()


def test_parser_exposes_task_commands():
    help_text = build_parser().format_help()
    assert "add" in help_text
    assert "list" in help_text
    assert "done" in help_text


def test_task_tracker_add_list_and_done():
    assert main(["add", "Write tests"]) == 0
    assert main(["list"]) == 0
    assert main(["done", "1"]) == 0
    assert _TASKS[0]["done"] is True
""",
    }


def _repo_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=Path(__file__).resolve().parents[2],
        text=True,
        capture_output=True,
        check=True,
    ).stdout


def test_golden_task_tracker_build_completes_and_publishes_one_draft_pr(
    tmp_path: Path,
) -> None:
    before_status = _repo_status()
    service, _workspace_manager, publisher = _service(tmp_path)

    result = service.build(_request())

    run = result.run
    assert run.status is MvpRunStatus.COMPLETED
    assert run.workspace_path is not None
    workspace = Path(run.workspace_path)
    for relative_path in (
        "README.md",
        "pyproject.toml",
        "src/task_tracker/__init__.py",
        "src/task_tracker/main.py",
        "tests/test_main.py",
    ):
        assert (workspace / relative_path).is_file()
    assert run.inventory is not None
    assert run.inventory.inventory_hash
    install_check = next(
        check for check in run.test_results if check.name == "install_project"
    )
    test_check = next(check for check in run.test_results if check.name == "run_tests")
    smoke_check = next(check for check in run.test_results if check.name == "cli_smoke")
    assert install_check.passed
    assert test_check.passed
    assert "passed" in test_check.details.get("stdout", "")
    assert smoke_check.passed
    assert run.github_publish_result is not None
    assert run.github_publish_result.draft is True
    assert run.github_publish_result.branch.startswith(
        "slugger/generated-task-tracker-"
    )
    assert run.github_publish_result.pull_request_url.startswith(
        "https://github.com/mightyjoe909/task-tracker/pull/"
    )

    runner_result = BasicRunner(_workspace_manager).run(_request(), workspace)
    repeat = publisher.publish(run, workspace, run.validation_results, runner_result)
    assert repeat.existing is True
    assert repeat.pull_request_url == run.github_publish_result.pull_request_url
    assert publisher.publish_count == 1

    reloaded = SQLiteMvpRunRepository(tmp_path / "runs.sqlite3").require(run.run_id)
    assert reloaded.status is MvpRunStatus.COMPLETED
    assert reloaded.github_publish_result is not None
    assert reloaded.inventory is not None
    assert reloaded.inventory.inventory_hash == run.inventory.inventory_hash

    workspace_root = tmp_path / "workspaces"
    assert workspace.is_relative_to(workspace_root)
    for generated_file in run.inventory.files:
        assert (
            (workspace / generated_file.path)
            .resolve()
            .is_relative_to(workspace.resolve())
        )
    assert _repo_status() == before_status


def test_codex_failure_blocks_validation(tmp_path: Path) -> None:
    workspace_manager = WorkspaceManager(tmp_path / "workspaces")
    service, _manager, publisher = _service(
        tmp_path,
        FakeMvpCodexAdapter(workspace_manager, fail=True),
    )

    result = service.build(_request())

    assert result.run.status is MvpRunStatus.FAILED
    assert result.run.validation_results == ()
    assert publisher.publish_count == 0


def test_invalid_python_blocks_testing(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    service, _manager, publisher = _service(
        tmp_path,
        TaskTrackerCodexAdapter(manager, invalid_python=True),
    )

    result = service.build(_request())

    assert result.run.status is MvpRunStatus.FAILED
    assert any(
        not check.passed and check.name == "python_syntax"
        for check in result.run.validation_results
    )
    assert result.run.test_results == ()
    assert publisher.publish_count == 0


def test_failed_tests_block_github_publication(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    service, _manager, publisher = _service(
        tmp_path,
        TaskTrackerCodexAdapter(manager, failing_tests=True),
    )

    result = service.build(_request())

    assert result.run.status is MvpRunStatus.FAILED
    assert any(
        not check.passed and check.name == "run_tests"
        for check in result.run.test_results
    )
    assert result.run.github_publish_result is None
    assert publisher.publish_count == 0


def test_github_failure_preserves_validated_workspace(tmp_path: Path) -> None:
    service, _manager, publisher = _service(tmp_path, github_fail=True)

    result = service.build(_request())

    assert result.run.status is MvpRunStatus.PUBLICATION_FAILED
    assert publisher.publish_count == 0
    assert result.run.workspace_path is not None
    assert Path(result.run.workspace_path).is_dir()
    assert result.run.validation_results
    assert all(check.passed for check in result.run.validation_results)
    assert result.run.test_results
    assert all(check.passed for check in result.run.test_results)


def test_path_traversal_is_rejected(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "workspaces")
    workspace = manager.create_workspace("path-traversal-run")

    with pytest.raises(WorkspaceSafetyError):
        manager.resolve_generated_path(workspace, "../outside.py")


def test_completed_run_publication_is_idempotent(tmp_path: Path) -> None:
    service, manager, publisher = _service(tmp_path)
    result = service.build(_request())

    first = result.run.github_publish_result
    assert first is not None
    workspace = Path(result.run.workspace_path or "")
    runner_result = BasicRunner(manager).run(_request(), workspace)

    second = publisher.publish(
        result.run,
        workspace,
        result.run.validation_results,
        runner_result,
    )

    assert second.pull_request_url == first.pull_request_url
    assert second.branch == first.branch
    assert second.existing is True
    assert publisher.publish_count == 1


def test_resume_publish_ignores_runner_artifacts_when_inventory_is_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SLUGGER_MVP_SKIP_PUBLISH", "1")
    service, _manager, publisher = _service(tmp_path)
    result = service.build(_request())

    assert result.run.status is MvpRunStatus.READY_TO_PUBLISH
    assert result.run.workspace_path is not None
    artifact = Path(result.run.workspace_path) / ".venv" / "runner-artifact.txt"
    artifact.parent.mkdir(exist_ok=True)
    artifact.write_text("created after validation", encoding="utf-8")
    monkeypatch.delenv("SLUGGER_MVP_SKIP_PUBLISH")

    published = service.publish(result.run.run_id)

    assert published.run.status is MvpRunStatus.COMPLETED
    assert published.run.github_publish_result is not None
    assert publisher.publish_count == 1
