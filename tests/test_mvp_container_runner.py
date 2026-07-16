import json
import shutil
import subprocess
from pathlib import Path

import pytest

from mvp.container_runner import (
    ContainerCommand,
    ContainerizedVerifierRunner,
    load_inner_evidence,
)


def _mount_values(argv: list[str]) -> list[str]:
    return [argv[index + 1] for index, value in enumerate(argv) if value == "--mount"]


def test_container_command_applies_restricted_policy(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    root = tmp_path / "verification"
    root.mkdir()
    project = root / "project"
    project.mkdir()
    command = ContainerizedVerifierRunner().build_command(
        repo_root=repo,
        approved_project=project,
        workspace_root=root,
        project_name="codex-cli-demo",
    )
    argv = list(command.argv)
    assert "--rm" in argv
    assert "--network" in argv and argv[argv.index("--network") + 1] == "none"
    assert "--cap-drop" in argv and argv[argv.index("--cap-drop") + 1] == "ALL"
    assert "no-new-privileges" in argv
    assert "--read-only" in argv
    assert "--user" in argv and argv[argv.index("--user") + 1] == "1000:1000"
    assert "--memory" in argv and argv[argv.index("--memory") + 1] == "512m"
    assert "--cpus" in argv and argv[argv.index("--cpus") + 1] == "1"
    assert "--pids-limit" in argv and argv[argv.index("--pids-limit") + 1] == "128"
    joined = " ".join(argv)
    assert "/var/run/docker.sock" not in joined
    assert str(Path.home()) not in joined
    assert "--privileged" not in argv
    assert "host" not in argv
    assert command.summary["network_disabled"] is True
    assert command.summary["runs_as_non_root"] is True


def test_container_command_keeps_project_below_workspace_and_writes_evidence_to_bind_mount(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    root = tmp_path / "verification"
    root.mkdir()
    project = root / "approved-project"
    project.mkdir()

    command = ContainerizedVerifierRunner().build_command(
        repo_root=repo,
        approved_project=project,
        workspace_root=root,
        project_name="codex-cli-demo",
    )
    argv = list(command.argv)
    joined = " ".join(argv)
    mounts = _mount_values(argv)

    assert "/tmp:rw,nosuid,nodev,size=256m" in argv
    assert "noexec" not in next(value for value in argv if value.startswith("/tmp:"))
    assert "dst=/approved-project" not in joined
    assert "--project-dir /approved-project" not in joined
    assert argv[argv.index("--project-dir") + 1] == "/verification/approved-project"
    assert argv[argv.index("--workspace-root") + 1] == "/verification"
    assert (
        argv[argv.index("--evidence-file") + 1]
        == "/evidence/verification-evidence.json"
    )
    assert f"type=bind,src={repo},dst=/slugger,ro" in mounts
    assert f"type=bind,src={root},dst=/verification,ro" in mounts
    expected_mount = f"type=bind,src={command.evidence_dir},dst=/evidence"
    assert expected_mount in mounts
    assert f"{expected_mount},rw" not in mounts
    assert f"{expected_mount},ro" not in mounts
    assert f"{expected_mount},readonly" not in mounts
    assert [mount for mount in mounts if not mount.endswith(",ro")] == [expected_mount]
    assert command.evidence_dir.is_dir()
    stat = command.evidence_dir.stat()
    assert stat.st_uid == 1000 or stat.st_mode & 0o002
    assert "evidence_dir:/evidence:rw" in command.summary["mounts"]
    assert "python" in argv
    assert argv[argv.index("python") + 1 : argv.index("python") + 4] == [
        "-m",
        "mvp.verify_cli",
        "--project-dir",
    ]
    assert "cli.main" not in argv


def test_inner_evidence_validation_accepts_successful_container_evidence(
    tmp_path: Path,
) -> None:
    digest = "a" * 64
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    evidence_file = evidence_dir / "verification-evidence.json"
    command = ContainerCommand((), {}, evidence_dir, evidence_file)
    evidence_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "project_name": "codex-cli-demo",
                "initial_inventory_digest": digest,
                "check_statuses": {
                    "installation": "passed",
                    "tests": "passed",
                    "smoke_test": "passed",
                    "mutation_check": "passed",
                },
            }
        ),
        encoding="utf-8",
    )

    assert load_inner_evidence(
        command,
        expected_project_name="codex-cli-demo",
        expected_manifest_digest=digest,
    )["check_statuses"] == {
        "installation": "passed",
        "tests": "passed",
        "smoke_test": "passed",
        "mutation_check": "passed",
    }


def test_inner_evidence_validation_rejects_bad_schema_and_mismatch(
    tmp_path: Path,
) -> None:
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    evidence_file = evidence_dir / "verification-evidence.json"
    command = ContainerCommand((), {}, evidence_dir, evidence_file)
    evidence_file.write_text(json.dumps({"schema_version": 2}), encoding="utf-8")
    try:
        load_inner_evidence(
            command,
            expected_project_name="codex-cli-demo",
            expected_manifest_digest="a" * 64,
        )
    except ValueError as exc:
        assert "schema_version" in str(exc)
    else:
        raise AssertionError("unsupported schema accepted")

    evidence_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "project_name": "other",
                "initial_inventory_digest": "a" * 64,
            }
        ),
        encoding="utf-8",
    )
    try:
        load_inner_evidence(
            command,
            expected_project_name="codex-cli-demo",
            expected_manifest_digest="a" * 64,
        )
    except ValueError as exc:
        assert "project_name mismatch" in str(exc)
    else:
        raise AssertionError("mismatched evidence accepted")


@pytest.mark.docker
def test_docker_accepts_generated_mounts_and_non_root_can_write_evidence(
    tmp_path: Path,
) -> None:
    if shutil.which("docker") is None:
        pytest.skip("Docker CLI is unavailable")
    probe = subprocess.run(
        ["docker", "info"], text=True, capture_output=True, timeout=20, check=False
    )
    if probe.returncode != 0:
        pytest.skip(f"Docker daemon is unavailable: {probe.stderr[:200]}")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "repo.txt").write_text("repo", encoding="utf-8")
    root = tmp_path / "verification"
    root.mkdir()
    project = root / "approved-project"
    project.mkdir()
    (project / "project.txt").write_text("project", encoding="utf-8")

    command = ContainerizedVerifierRunner().build_command(
        repo_root=repo,
        approved_project=project,
        workspace_root=root,
        project_name="codex-cli-demo",
    )
    argv = list(command.argv)
    image_index = argv.index("slugger-mvp-verifier:python3.11-pytest")
    docker_argv = argv[:image_index] + [
        "python:3.11-slim",
        "python",
        "-c",
        (
            "from pathlib import Path; "
            "Path('/evidence/probe.txt').write_text('ok', encoding='utf-8'); "
            "assert Path('/evidence/probe.txt').read_text(encoding='utf-8') == 'ok'; "
            "assert not Path('/slugger/should-not-write').exists(); "
            "assert not Path('/verification/should-not-write').exists(); "
            "failed=[]; "
            "\nfor p in ('/slugger/should-not-write', '/verification/should-not-write'):"
            "\n    try: Path(p).write_text('no', encoding='utf-8')"
            "\n    except OSError: failed.append(p)"
            "\nassert len(failed) == 2"
        ),
    ]

    completed = subprocess.run(
        docker_argv, text=True, capture_output=True, timeout=60, check=False
    )

    assert completed.returncode == 0, completed.stderr
    assert (command.evidence_dir / "probe.txt").read_text(encoding="utf-8") == "ok"
    assert not (repo / "should-not-write").exists()
    assert not (root / "should-not-write").exists()
