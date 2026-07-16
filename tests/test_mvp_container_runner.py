from pathlib import Path

from mvp.container_runner import ContainerizedVerifierRunner


def test_container_command_applies_restricted_policy(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    root = tmp_path / "verification"
    root.mkdir()
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
