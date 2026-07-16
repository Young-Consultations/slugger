"""Restricted Docker execution adapter for generated MVP verification."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shlex
import subprocess


@dataclass(frozen=True)
class ContainerPolicy:
    image: str = "slugger-mvp-verifier:python3.11-pytest"
    user: str = "1000:1000"
    network: str = "none"
    memory: str = "512m"
    cpus: str = "1"
    pids_limit: int = 128
    timeout_seconds: int = 180
    output_limit: int = 12000

    def resource_limits(self) -> dict[str, object]:
        return {
            "network": self.network,
            "memory": self.memory,
            "cpus": self.cpus,
            "pids_limit": self.pids_limit,
            "timeout_seconds": self.timeout_seconds,
            "read_only_rootfs": True,
            "cap_drop": ["ALL"],
            "no_new_privileges": True,
            "user": self.user,
        }


@dataclass(frozen=True)
class ContainerCommand:
    argv: tuple[str, ...]
    summary: dict[str, object]


class ContainerizedVerifierRunner:
    """Build and run the restricted verifier container command."""

    def __init__(self, *, policy: ContainerPolicy | None = None) -> None:
        self.policy = policy or ContainerPolicy()

    def build_command(
        self,
        *,
        repo_root: Path,
        approved_project: Path,
        workspace_root: Path,
        project_name: str,
    ) -> ContainerCommand:
        repo_root = repo_root.resolve(strict=True)
        approved_project = approved_project.resolve(strict=True)
        workspace_root = workspace_root.resolve(strict=True)
        argv = (
            "docker",
            "run",
            "--rm",
            "--network",
            self.policy.network,
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            str(self.policy.pids_limit),
            "--memory",
            self.policy.memory,
            "--cpus",
            self.policy.cpus,
            "--read-only",
            "--user",
            self.policy.user,
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,nodev,size=128m",
            "--mount",
            f"type=bind,src={repo_root},dst=/slugger,ro",
            "--mount",
            f"type=bind,src={approved_project},dst=/approved-project,ro",
            "--mount",
            f"type=bind,src={workspace_root},dst=/verification,ro",
            "--workdir",
            "/slugger",
            "--env",
            "PYTHONNOUSERSITE=1",
            "--env",
            "PIP_NO_INDEX=1",
            self.policy.image,
            "python",
            "-m",
            "cli.main",
            "mvp",
            "verify-existing",
            "--project-dir",
            "/approved-project",
            "--project-name",
            project_name,
            "--workspace-root",
            "/verification",
            "--no-container",
        )
        summary = {
            "image": self.policy.image,
            "network_disabled": self.policy.network == "none",
            "runs_as_non_root": self.policy.user != "0"
            and not self.policy.user.startswith("0:"),
            "capabilities_dropped": ["ALL"],
            "no_new_privileges": True,
            "resource_limits": self.policy.resource_limits(),
            "mounts": [
                "repo:ro",
                "approved_project:ro",
                "verification_root:ro",
                "tmpfs:/tmp",
            ],
            "prohibited_mounts_absent": [
                "/var/run/docker.sock",
                "home",
                "ssh",
                "cloud_credentials",
            ],
            "command": " ".join(shlex.quote(part) for part in argv[:38]) + " ...",
        }
        return ContainerCommand(argv=argv, summary=summary)

    def run(self, command: ContainerCommand) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command.argv,
            text=True,
            capture_output=True,
            timeout=self.policy.timeout_seconds,
            check=False,
        )
