"""CodeGeneratorAgent implementation."""

from __future__ import annotations

import logging
from pathlib import Path
import re

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import CodeArtifact
from models.app_manifest import (
    AppManifest,
    FileEntry,
    make_cli_manifest,
    make_fastapi_manifest,
)
from models.execution import ExecutionContext

_LOG = logging.getLogger(__name__)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "generated-app"


def _base_manifest(idea: str, platform: str, coding_agent: str) -> AppManifest:
    name = idea[:40].strip() or "Generated App"
    app_id = _slug(name)
    if platform == "web":
        manifest = make_fastapi_manifest(app_id, name, idea)
    else:
        manifest = make_cli_manifest(app_id, name, idea)
    manifest.metadata.update(
        {"idea": idea, "platform": platform, "coding_agent": coding_agent}
    )
    return manifest


def _manifest_to_artifact_content(manifest: AppManifest) -> str:
    return manifest.to_json()


def _manifest_from_codex_result(
    idea: str,
    platform: str,
    coding_agent: str,
    workspace_root: Path,
    result,
) -> AppManifest:
    manifest = _base_manifest(idea, platform, coding_agent)
    manifest.metadata["codex_session_id"] = result.session_id
    path_to_index = {entry.path: index for index, entry in enumerate(manifest.files)}
    for change in result.file_changes:
        path = Path(change.path)
        try:
            relative_path = path.resolve().relative_to(workspace_root)
            manifest_path = relative_path.as_posix()
        except ValueError:
            manifest_path = path.name
        file_entry = FileEntry(
            path=manifest_path, content=change.content, requirement_ids=["REQ-001"]
        )
        if manifest_path in path_to_index:
            manifest.files[path_to_index[manifest_path]] = file_entry
        else:
            manifest.files.append(file_entry)
    if result.commands_run:
        manifest.commands = list(result.commands_run)
    return manifest


def _manifest_from_workspace(
    idea: str,
    platform: str,
    coding_agent: str,
    workspace_root: Path,
    result,
) -> AppManifest:
    manifest = _base_manifest(idea, platform, coding_agent)
    manifest.metadata["codex_session_id"] = result.session_id
    path_to_index = {entry.path: index for index, entry in enumerate(manifest.files)}
    for file_path in sorted(
        path for path in workspace_root.rglob("*") if path.is_file()
    ):
        manifest_path = file_path.relative_to(workspace_root).as_posix()
        file_entry = FileEntry(
            path=manifest_path,
            content=file_path.read_text(encoding="utf-8"),
            requirement_ids=["REQ-001"],
        )
        if manifest_path in path_to_index:
            manifest.files[path_to_index[manifest_path]] = file_entry
        else:
            manifest.files.append(file_entry)
    if result.commands_run:
        manifest.commands = list(result.commands_run)
    return manifest


class CodeGeneratorAgent(BaseAgent):
    """Create code artifacts.

    When a ``codex_agent_client`` is available in the execution context the
    agent delegates to the full coding-agent adapter (workspace-level file
    writes, command evidence).  When not available it falls back to the
    template scaffold so that all tests and offline runs continue to work.
    """

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="code_generator_agent",
                version="1.0.0",
                description="Create code artifacts.",
                category="development",
                inputs=[],
                outputs=["generated_code"],
                tags=["development", "code_generation"],
                provider="mock",
                external_interface="openai_codex",
            ),
            capabilities=[
                AgentCapability(
                    name="code_generation",
                    description="Create code artifacts.",
                    outputs=("generated_code",),
                )
            ],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea() or "Unspecified idea"
        platform = context.metadata.get("platform", "web")
        if context.project_brief is not None:
            platform = context.project_brief.platform.value
        coding_agent = context.metadata.get("coding_agent", "codex")
        if context.project_brief is not None:
            coding_agent = context.project_brief.coding_agent.value

        manifest = self._generate_code_manifest(idea, platform, coding_agent, context)
        artifact = self.create_artifact(
            context,
            "generated_code",
            _manifest_to_artifact_content(manifest),
            CodeArtifact,
            format="json",
        )
        artifact.extra["application_id"] = manifest.application_id
        artifact.extra["schema_version"] = manifest.schema_version
        artifact.extra["file_count"] = len(manifest.files)
        return [artifact]

    def _generate_code_manifest(
        self, idea: str, platform: str, coding_agent: str, context: ExecutionContext
    ) -> AppManifest:
        client = getattr(context, "codex_agent_client", None)
        workspace_root_value = context.metadata.get("workspace_root")
        workspace_root = (
            Path(workspace_root_value).resolve()
            if workspace_root_value is not None
            else Path.cwd().resolve()
        )
        if client is not None:
            from providers.codex_agent_client import CodexWorkspace

            workspace = CodexWorkspace(root=workspace_root)
            try:
                task_brief = f"Generate a complete {platform} application for: {idea}"
                result = client.start_task(task_brief, workspace)
                if result.success:
                    if result.file_changes:
                        return _manifest_from_codex_result(
                            idea, platform, coding_agent, workspace_root, result
                        )
                    if workspace_root_value is not None and any(
                        path.is_file() for path in workspace_root.rglob("*")
                    ):
                        return _manifest_from_workspace(
                            idea, platform, coding_agent, workspace_root, result
                        )
            except Exception as exc:  # noqa: BLE001
                _LOG.warning(
                    "Codex agent code generation failed, using manifest template: %s",
                    exc,
                )

        return _base_manifest(idea, platform, coding_agent)
