"""Restricted Docker execution adapter for generated MVP verification."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shlex
import subprocess
import tempfile
from typing import Any


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
    evidence_dir: Path
    evidence_file: Path


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
        container_workspace_root = Path("/verification")
        container_project_dir = container_workspace_root / approved_project.name
        host_evidence_dir = Path(tempfile.mkdtemp(prefix="slugger-container-evidence-"))
        host_evidence_file = host_evidence_dir / "verification-evidence.json"
        container_evidence_file = Path("/evidence/verification-evidence.json")
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
            "/tmp:rw,nosuid,nodev,size=256m",
            "--mount",
            f"type=bind,src={repo_root},dst=/slugger,ro",
            "--mount",
            f"type=bind,src={workspace_root},dst=/verification,ro",
            "--mount",
            f"type=bind,src={host_evidence_dir},dst=/evidence,rw",
            "--workdir",
            "/slugger",
            "--env",
            "PYTHONNOUSERSITE=1",
            "--env",
            "PIP_NO_INDEX=1",
            self.policy.image,
            "python",
            "-m",
            "mvp.verify_cli",
            "--project-dir",
            str(container_project_dir),
            "--project-name",
            project_name,
            "--workspace-root",
            str(container_workspace_root),
            "--evidence-file",
            str(container_evidence_file),
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
                "approved_project:/verification/<project>:ro",
                "verification_root:ro",
                "tmpfs:/tmp:exec",
                "evidence_dir:/evidence:rw",
            ],
            "prohibited_mounts_absent": [
                "/var/run/docker.sock",
                "home",
                "ssh",
                "cloud_credentials",
            ],
            "command": " ".join(shlex.quote(part) for part in argv[:38]) + " ...",
        }
        return ContainerCommand(
            argv=argv,
            summary=summary,
            evidence_dir=host_evidence_dir,
            evidence_file=host_evidence_file,
        )

    def run(self, command: ContainerCommand) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command.argv,
            text=True,
            capture_output=True,
            timeout=self.policy.timeout_seconds,
            check=False,
        )


MAX_EVIDENCE_BYTES = 256_000


def load_inner_evidence(
    command: ContainerCommand,
    *,
    expected_project_name: str,
    expected_manifest_digest: str,
) -> dict[str, Any]:
    evidence_dir = command.evidence_dir.resolve(strict=True)
    evidence_file = command.evidence_file
    if evidence_file.name != "verification-evidence.json":
        raise ValueError("Unsupported evidence filename")
    if evidence_file.parent.resolve(strict=True) != evidence_dir:
        raise ValueError("Evidence path escapes evidence directory")
    if evidence_file.is_symlink():
        raise ValueError("Evidence file must not be a symlink")
    if not evidence_file.exists():
        raise ValueError("Inner evidence file was not exported")
    if not evidence_file.is_file():
        raise ValueError("Inner evidence path is not a regular file")
    size = evidence_file.stat().st_size
    if size > MAX_EVIDENCE_BYTES:
        raise ValueError("Inner evidence exceeds maximum size")
    try:
        data = json.loads(evidence_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed inner evidence: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Inner evidence must be an object")
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported inner evidence schema_version")
    if data.get("project_name") != expected_project_name:
        raise ValueError("Inner evidence project_name mismatch")
    if data.get("initial_inventory_digest") != expected_manifest_digest:
        raise ValueError("Inner evidence manifest digest mismatch")
    return data
