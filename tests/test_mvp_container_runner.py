from pathlib import Path

from mvp.container_runner import ContainerizedVerifierRunner


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
    assert "--network" in argv and argv[argv.index("--network") + 1] == "none"
    assert "--cap-drop" in argv and argv[argv.index("--cap-drop") + 1] == "ALL"
    assert "no-new-privileges" in argv
    assert "--read-only" in argv
    assert "--user" in argv and argv[argv.index("--user") + 1] != "0"
    assert "--memory" in argv and argv[argv.index("--memory") + 1] == "512m"
    assert "--cpus" in argv and argv[argv.index("--cpus") + 1] == "1"
    assert "--pids-limit" in argv and argv[argv.index("--pids-limit") + 1] == "128"
    joined = " ".join(argv)
    assert "/var/run/docker.sock" not in joined
    assert str(Path.home()) not in joined
    assert command.summary["network_disabled"] is True
    assert command.summary["runs_as_non_root"] is True


def test_container_command_keeps_project_below_workspace_and_writes_evidence_to_tmpfs(
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

    assert "/tmp:rw,nosuid,nodev,size=256m" in argv
    assert "noexec" not in next(value for value in argv if value.startswith("/tmp:"))
    assert "/evidence:rw,nosuid,nodev,size=16m" in argv
    assert "dst=/approved-project" not in joined
    assert "--project-dir /approved-project" not in joined
    assert argv[argv.index("--project-dir") + 1] == "/verification/approved-project"
    assert argv[argv.index("--workspace-root") + 1] == "/verification"
    assert (
        argv[argv.index("--evidence-file") + 1]
        == "/evidence/verification-evidence.json"
    )
    assert f"type=bind,src={project},dst=/verification/approved-project,ro" in argv
    assert "tmpfs:/evidence:writable" in command.summary["mounts"]
