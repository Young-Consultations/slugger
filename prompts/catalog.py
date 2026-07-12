"""SDLC Prompt Catalog and Artifact Schema contracts (CC-002).

This module provides:
- :class:`PromptFrontmatter` — structured metadata for versioned prompts
- :class:`ArtifactSchema` — typed validation contract for major SDLC artifacts
- :class:`SdlcPromptCatalog` — pre-registered, approved prompts for every pipeline stage
- :func:`build_default_catalog` — convenience factory returning a ready-to-use catalog
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from prompts.lifecycle import PromptApprovalStatus, PromptRegistry, PromptVersion


# ---------------------------------------------------------------------------
# Prompt frontmatter
# ---------------------------------------------------------------------------

@dataclass
class PromptFrontmatter:
    """Structured metadata for a versioned prompt.

    Every provider-backed agent must reference a prompt by its ``prompt_id``
    and ``version``.  The content hash allows CI to detect unauthorised edits
    without re-running live providers.
    """

    prompt_id: str
    version: str
    owner: str = 'slugger-team'
    status: PromptApprovalStatus = PromptApprovalStatus.APPROVED
    inputs: list[str] = field(default_factory=list)
    output_schema_id: str = ''
    model_requirements: list[str] = field(default_factory=list)
    changelog: list[str] = field(default_factory=list)

    def content_hash(self, content: str) -> str:
        """SHA-256 hash of the prompt content for tamper detection."""
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            'prompt_id': self.prompt_id,
            'version': self.version,
            'owner': self.owner,
            'status': self.status.value,
            'inputs': list(self.inputs),
            'output_schema_id': self.output_schema_id,
            'model_requirements': list(self.model_requirements),
            'changelog': list(self.changelog),
        }


# ---------------------------------------------------------------------------
# Artifact schemas
# ---------------------------------------------------------------------------

@dataclass
class ArtifactSchemaField:
    """A single required field in an artifact schema."""

    name: str
    description: str
    required: bool = True


@dataclass
class ArtifactSchema:
    """Typed validation contract for a major SDLC artifact.

    Validation checks that the artifact content contains the required section
    headers / field markers so downstream consumers can parse structured output.
    """

    schema_id: str
    schema_version: str = '1.0.0'
    description: str = ''
    required_sections: list[str] = field(default_factory=list)
    fields: list[ArtifactSchemaField] = field(default_factory=list)

    def validate(self, content: str) -> list[str]:
        """Return a list of missing-section error messages (empty = valid)."""
        errors: list[str] = []
        for section in self.required_sections:
            if section.lower() not in content.lower():
                errors.append(f'Missing required section: {section!r}')
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            'schema_id': self.schema_id,
            'schema_version': self.schema_version,
            'description': self.description,
            'required_sections': list(self.required_sections),
        }


# ---------------------------------------------------------------------------
# Default artifact schemas
# ---------------------------------------------------------------------------

ARTIFACT_SCHEMAS: dict[str, ArtifactSchema] = {
    'product_vision': ArtifactSchema(
        schema_id='product_vision_v1',
        description='Product vision document',
        required_sections=['Idea', 'Platform'],
    ),
    'requirements': ArtifactSchema(
        schema_id='requirements_v1',
        description='Functional requirements document',
        required_sections=['Idea'],
    ),
    'user_stories': ArtifactSchema(
        schema_id='user_stories_v1',
        description='User stories document',
        required_sections=['Idea'],
    ),
    'system_design': ArtifactSchema(
        schema_id='system_design_v1',
        description='System design document',
        required_sections=['Idea'],
    ),
    'adr': ArtifactSchema(
        schema_id='adr_v1',
        description='Architecture Decision Record',
        required_sections=['Idea'],
    ),
    'project_plan': ArtifactSchema(
        schema_id='project_plan_v1',
        description='Project plan',
        required_sections=['Idea'],
    ),
    'generated_code': ArtifactSchema(
        schema_id='generated_code_v1',
        description='Generated AppManifest JSON',
        required_sections=['"schema_version"', '"application_id"'],
    ),
    'code_review': ArtifactSchema(
        schema_id='code_review_v1',
        description='Code review findings',
        required_sections=['Code Review'],
    ),
    'test_suite': ArtifactSchema(
        schema_id='test_suite_v1',
        description='Test suite',
        required_sections=[],
    ),
    'ci_cd_pipeline': ArtifactSchema(
        schema_id='ci_cd_pipeline_v1',
        description='CI/CD pipeline configuration',
        required_sections=['CI/CD'],
    ),
}


# ---------------------------------------------------------------------------
# SDLC prompt catalog content
# ---------------------------------------------------------------------------

_SDLC_PROMPTS: list[dict[str, Any]] = [
    {
        'prompt_id': 'sdlc.product_vision.v1',
        'name': 'Product Vision',
        'content': (
            'You are a senior product manager. '
            'Create a concise product vision document for the following idea.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Platform:** {{ platform }}\n'
            '**Target users:** {{ target_users }}\n\n'
            'Output sections:\n'
            '1. Vision statement\n'
            '2. Problem being solved\n'
            '3. Target users and personas\n'
            '4. Key outcomes and success metrics\n\n'
            'Constraints: Be specific, actionable, and measurable. '
            'Return only the product vision document in Markdown. '
            'Failure handling: If the idea is empty, return an error object '
            'with field "error" set to "missing_idea".'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.product_vision.v1',
            version='1.0.0',
            inputs=['idea', 'platform', 'target_users'],
            output_schema_id='product_vision_v1',
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.requirements.v1',
        'name': 'Requirements',
        'content': (
            'You are a senior business analyst. '
            'Convert the product vision into structured software requirements.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Product Vision:**\n{{ product_vision }}\n\n'
            'Output sections:\n'
            '1. Functional requirements (REQ-XXX IDs)\n'
            '2. Non-functional requirements\n'
            '3. Acceptance criteria\n'
            '4. Out of scope\n'
            '5. Risks and assumptions\n\n'
            'Constraints: Every requirement must have a stable ID (REQ-001, REQ-002, …). '
            'Return only the requirements document in Markdown. '
            'Failure handling: Return error object with "error" and "missing_inputs" fields '
            'if required inputs are absent.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.requirements.v1',
            version='1.0.0',
            inputs=['idea', 'product_vision'],
            output_schema_id='requirements_v1',
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.user_stories.v1',
        'name': 'User Stories',
        'content': (
            'You are a senior product owner. '
            'Generate user stories from the requirements document.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Requirements:**\n{{ requirements }}\n\n'
            'Output format: Markdown with stories in "As a … I want … so that …" format. '
            'Include stable story IDs (US-001, US-002, …). '
            'Constraints: Every story must map to at least one requirement ID. '
            'Failure handling: Return error object if requirements are empty.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.user_stories.v1',
            version='1.0.0',
            inputs=['idea', 'requirements'],
            output_schema_id='user_stories_v1',
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.system_design.v1',
        'name': 'System Design',
        'content': (
            'You are a senior software architect. '
            'Design the system architecture for the following project.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Requirements:**\n{{ requirements }}\n\n'
            'Output sections:\n'
            '1. Architecture overview\n'
            '2. Components and responsibilities\n'
            '3. Data model\n'
            '4. Technology choices with justification\n'
            '5. Sequence diagrams (Mermaid)\n'
            '6. Risks and trade-offs\n\n'
            'Constraints: Include a Mermaid C4 or sequence diagram. '
            'Return only the architecture document in Markdown. '
            'Failure handling: Return error object if requirements are absent.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.system_design.v1',
            version='1.0.0',
            inputs=['idea', 'requirements'],
            output_schema_id='system_design_v1',
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.adr.v1',
        'name': 'Architecture Decision Record',
        'content': (
            'You are a senior architect. '
            'Create an Architecture Decision Record for the most significant technology choice.\n\n'
            '**Idea:** {{ idea }}\n'
            '**System Design:**\n{{ system_design }}\n\n'
            'ADR format:\n'
            '## Title\n## Status\n## Context\n## Decision\n## Consequences\n\n'
            'Constraints: Include stable ADR ID (ADR-001). '
            'Failure handling: Return error object if system_design is missing.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.adr.v1',
            version='1.0.0',
            inputs=['idea', 'system_design'],
            output_schema_id='adr_v1',
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.project_plan.v1',
        'name': 'Project Plan',
        'content': (
            'You are a senior engineering manager. '
            'Create an implementation project plan.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Requirements:**\n{{ requirements }}\n\n'
            'Output sections:\n'
            '1. Milestones with stable IDs (M-001, M-002, …)\n'
            '2. Tasks with dependencies and story mappings\n'
            '3. Risk register\n'
            '4. Definition of Done\n\n'
            'Failure handling: Return error if requirements are empty.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.project_plan.v1',
            version='1.0.0',
            inputs=['idea', 'requirements'],
            output_schema_id='project_plan_v1',
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.code_manifest.v1',
        'name': 'Code Manifest',
        'content': (
            'You are a senior Python engineer using Codex. '
            'Generate a complete multi-file Python application.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Platform:** {{ platform }}\n'
            '**Requirements:**\n{{ requirements }}\n'
            '**Architecture:**\n{{ system_design }}\n\n'
            'Return a JSON application manifest with schema version "1.0" containing:\n'
            '- app_name, template_id, files (list of {path, content, checksum})\n'
            '- pyproject.toml, README.md, src/, tests/ must all be present\n\n'
            'Constraints: No absolute paths. No credentials. '
            'Files must be valid Python. Tests must import from the src package. '
            'Failure handling: Return JSON error object if required inputs are missing.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.code_manifest.v1',
            version='1.0.0',
            inputs=['idea', 'platform', 'requirements', 'system_design'],
            output_schema_id='generated_code_v1',
            model_requirements=['codex'],
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.code_review.v1',
        'name': 'Code Review',
        'content': (
            'You are a senior code reviewer. '
            'Review the generated code for correctness, security, and quality.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Generated Code:**\n{{ generated_code }}\n\n'
            'Output a prioritized list of findings with:\n'
            '- finding_id (FIND-001, …)\n'
            '- severity (critical/high/medium/low)\n'
            '- category (security/correctness/quality/style)\n'
            '- file and line\n'
            '- description and recommended fix\n\n'
            'Constraints: Review only, do not modify files. '
            'Return Markdown with a structured findings table. '
            'Failure handling: Return error object if code is empty.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.code_review.v1',
            version='1.0.0',
            inputs=['idea', 'generated_code'],
            output_schema_id='code_review_v1',
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.qa_remediation.v1',
        'name': 'QA Remediation',
        'content': (
            'You are a senior QA engineer. '
            'Remediate the failing tests and quality findings.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Test Results:**\n{{ test_results }}\n'
            '**Code Review Findings:**\n{{ code_review }}\n\n'
            'For each finding, provide:\n'
            '- finding_id\n'
            '- remediation_action (fix/defer/waive)\n'
            '- changed_files (list)\n'
            '- verification_command\n\n'
            'Constraints: Only remediate within the approved file scope. '
            'Failure handling: Return error if test_results or code_review are absent.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.qa_remediation.v1',
            version='1.0.0',
            inputs=['idea', 'test_results', 'code_review'],
            output_schema_id='code_review_v1',
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.security_remediation.v1',
        'name': 'Security Remediation',
        'content': (
            'You are a senior application security engineer. '
            'Review and remediate security findings.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Security Review:**\n{{ security_review }}\n'
            '**Generated Code:**\n{{ generated_code }}\n\n'
            'For each security finding:\n'
            '- finding_id\n'
            '- cvss_score_estimate\n'
            '- remediation_action (fix/waive with justification)\n'
            '- changed_files\n'
            '- verification_command\n\n'
            'Constraints: Never auto-waive critical findings without human approval. '
            'Return JSON with schema_version "1.0" and findings array. '
            'Failure handling: Return error object if security_review is empty.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.security_remediation.v1',
            version='1.0.0',
            inputs=['idea', 'security_review', 'generated_code'],
            output_schema_id='code_review_v1',
            model_requirements=['codex'],
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.documentation.v1',
        'name': 'Documentation',
        'content': (
            'You are a senior technical writer. '
            'Generate user and developer documentation.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Generated Code:**\n{{ generated_code }}\n\n'
            'Output sections:\n'
            '1. README.md (installation, usage, examples)\n'
            '2. API reference (if applicable)\n'
            '3. Contributing guide\n'
            '4. Changelog entry\n\n'
            'Constraints: Use Markdown. Include code examples. '
            'Failure handling: Return error if generated_code is absent.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.documentation.v1',
            version='1.0.0',
            inputs=['idea', 'generated_code'],
            output_schema_id='requirements_v1',
            changelog=['Initial version'],
        ),
    },
    {
        'prompt_id': 'sdlc.release_readiness.v1',
        'name': 'Release Readiness',
        'content': (
            'You are a release manager. '
            'Evaluate release readiness based on evidence.\n\n'
            '**Idea:** {{ idea }}\n'
            '**Build Results:**\n{{ build_results }}\n'
            '**Test Results:**\n{{ test_results }}\n'
            '**Security Review:**\n{{ security_review }}\n\n'
            'Output:\n'
            '1. go_nogo_decision (go/nogo/conditional)\n'
            '2. blocking_issues (list)\n'
            '3. release_notes_draft\n'
            '4. evidence_summary\n\n'
            'Constraints: nogo if any critical security finding is unresolved. '
            'Return JSON with schema_version "1.0". '
            'Failure handling: Return nogo with error if required inputs are missing.'
        ),
        'frontmatter': PromptFrontmatter(
            prompt_id='sdlc.release_readiness.v1',
            version='1.0.0',
            inputs=['idea', 'build_results', 'test_results', 'security_review'],
            output_schema_id='requirements_v1',
            changelog=['Initial version'],
        ),
    },
]


# ---------------------------------------------------------------------------
# SDLC Prompt Catalog
# ---------------------------------------------------------------------------

class SdlcPromptCatalog:
    """Pre-registered and approved prompts for every AI-SDLC pipeline stage.

    Every prompt in the catalog is automatically approved on construction.
    Production agents must reference a prompt from this catalog by its
    ``prompt_id`` and ``version``.
    """

    def __init__(self, registry: PromptRegistry | None = None) -> None:
        self._registry = registry or PromptRegistry()
        self._frontmatters: dict[str, PromptFrontmatter] = {}
        self._populate()

    def _populate(self) -> None:
        for entry in _SDLC_PROMPTS:
            prompt_id = entry['prompt_id']
            pv = self._registry.register(
                prompt_id=prompt_id,
                name=entry['name'],
                content=entry['content'],
                author='slugger-team',
                metadata={'frontmatter': entry['frontmatter'].to_dict()},
            )
            self._registry.approve(prompt_id, approver='slugger-system')
            self._frontmatters[prompt_id] = entry['frontmatter']

    @property
    def registry(self) -> PromptRegistry:
        return self._registry

    def get(self, prompt_id: str) -> PromptVersion | None:
        """Return the latest approved version of *prompt_id*."""
        return self._registry.latest(prompt_id)

    def frontmatter(self, prompt_id: str) -> PromptFrontmatter | None:
        return self._frontmatters.get(prompt_id)

    def render(self, prompt_id: str, variables: dict[str, str]) -> str:
        """Render the prompt template with *variables* substituted.

        All ``{{ variable }}`` placeholders in the prompt content are replaced
        by the corresponding values from *variables*.

        Raises
        ------
        KeyError
            If *prompt_id* is not in the catalog.
        ValueError
            If a required input variable is absent from *variables*.
        """
        prompt = self.get(prompt_id)
        if prompt is None:
            raise KeyError(f'Unknown prompt: {prompt_id!r}')
        fm = self._frontmatters.get(prompt_id)
        if fm:
            missing = [inp for inp in fm.inputs if inp not in variables]
            if missing:
                raise ValueError(
                    f'Missing required inputs for prompt {prompt_id!r}: {missing}'
                )
        content = prompt.content
        for key, value in variables.items():
            content = content.replace('{{ ' + key + ' }}', value)
        return content

    def validate_content_hash(self, prompt_id: str, expected_hash: str) -> bool:
        """Return ``True`` if the current content hash matches *expected_hash*."""
        prompt = self.get(prompt_id)
        if prompt is None:
            return False
        fm = self._frontmatters.get(prompt_id)
        if fm is None:
            return False
        actual = fm.content_hash(prompt.content)
        return actual == expected_hash

    def all_approved(self) -> list[PromptVersion]:
        """Return all prompts in APPROVED status."""
        from prompts.lifecycle import PromptApprovalStatus
        return [
            p for p in self._registry.all_prompts()
            if p.status == PromptApprovalStatus.APPROVED
        ]

    def validate_artifact(self, artifact_name: str, content: str) -> list[str]:
        """Validate artifact *content* against its schema; returns error list."""
        schema = ARTIFACT_SCHEMAS.get(artifact_name)
        if schema is None:
            return []
        return schema.validate(content)


_default_catalog: SdlcPromptCatalog | None = None


def build_default_catalog() -> SdlcPromptCatalog:
    """Return a shared singleton SDLC prompt catalog."""
    global _default_catalog
    if _default_catalog is None:
        _default_catalog = SdlcPromptCatalog()
    return _default_catalog
