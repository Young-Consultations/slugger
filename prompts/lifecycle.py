"""Prompt lifecycle management.

Provides prompt versioning, quality scoring, and an approval workflow so
that prompts are treated as first-class engineering assets alongside code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class PromptApprovalStatus(str, Enum):
    """Lifecycle status for a prompt version."""

    DRAFT = 'draft'
    PENDING_REVIEW = 'pending_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    DEPRECATED = 'deprecated'


@dataclass
class PromptVersion:
    """A single versioned snapshot of a prompt.

    Parameters
    ----------
    prompt_id:
        Stable identifier for the prompt (shared across versions).
    name:
        Human-readable prompt name.
    content:
        The prompt text.
    version:
        SemVer version string.
    author:
        Identity of the author.
    status:
        Current lifecycle status.
    quality_score:
        Automated quality score 0–10 (``None`` if not yet evaluated).
    change_notes:
        Description of changes from the previous version.
    metadata:
        Arbitrary extra data.
    created_at:
        UTC creation timestamp.
    """

    prompt_id: str
    name: str
    content: str
    version: str = '1.0.0'
    author: str = 'unknown'
    status: PromptApprovalStatus = PromptApprovalStatus.DRAFT
    quality_score: float | None = None
    change_notes: str = ''
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            'prompt_id': self.prompt_id,
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'status': self.status.value,
            'quality_score': self.quality_score,
            'change_notes': self.change_notes,
            'metadata': dict(self.metadata),
            'created_at': self.created_at.isoformat(),
            'content_length': len(self.content),
        }


def _bump_minor(version: str) -> str:
    """Increment the minor component of a SemVer string."""
    parts = version.split('.')
    try:
        parts[1] = str(int(parts[1]) + 1)
        if len(parts) > 2:
            parts[2] = '0'
        elif len(parts) == 2:
            parts.append('0')
    except (ValueError, IndexError):
        parts = ['1', '0', '0']
    return '.'.join(parts)


class PromptQualityScorer:
    """Heuristic-based prompt quality scorer.

    Evaluates prompts on several dimensions and returns a score 0–10.

    Dimensions:
    - Length (0–2): prompts between 50 and 500 chars score highest
    - Specificity (0–3): presence of action verbs and constraints
    - Structure (0–2): numbered lists, bullet points, or section headers
    - Context (0–2): mentions of role, audience, or output format
    - Clarity (0–1): absence of vague filler words
    """

    _ACTION_VERBS = {'generate', 'create', 'write', 'produce', 'list', 'describe', 'summarise',
                     'summarize', 'explain', 'review', 'analyse', 'analyze', 'compare', 'return'}
    _VAGUE_WORDS = {'stuff', 'things', 'etc', 'somehow', 'kind of', 'sort of'}
    _FORMAT_HINTS = {'json', 'yaml', 'markdown', 'table', 'bullet', 'numbered', 'output:', 'format:'}
    _ROLE_HINTS = {'you are', 'act as', 'as a', 'role:', 'persona:'}

    def score(self, content: str) -> float:
        if not content.strip():
            return 0.0
        lower = content.lower()
        total = 0.0

        # Length score (0–2)
        length = len(content)
        if 50 <= length <= 500:
            total += 2.0
        elif 20 <= length < 50 or 500 < length <= 1000:
            total += 1.0

        # Specificity (0–3): action verbs and constraints
        verbs_found = sum(1 for v in self._ACTION_VERBS if v in lower)
        total += min(verbs_found * 0.5, 1.5)
        if any(kw in lower for kw in ('must', 'should', 'only', 'exactly', 'always', 'never', 'do not')):
            total += 1.0
        if any(char in content for char in (':', '-', '•')):
            total += 0.5

        # Structure (0–2)
        lines = content.splitlines()
        if any(line.strip().startswith(('1.', '2.', '3.', '-', '*', '•')) for line in lines):
            total += 1.0
        if any(line.strip().endswith(':') for line in lines):
            total += 1.0

        # Context (0–2): format hints and role hints
        if any(hint in lower for hint in self._FORMAT_HINTS):
            total += 1.0
        if any(hint in lower for hint in self._ROLE_HINTS):
            total += 1.0

        # Clarity penalty (0–1): subtract for vague words
        vague_count = sum(1 for w in self._VAGUE_WORDS if w in lower)
        clarity = max(0.0, 1.0 - vague_count * 0.5)
        total += clarity

        return round(min(total, 10.0), 1)


class PromptRegistry:
    """Store and manage versioned prompts with lifecycle tracking.

    Examples
    --------
    >>> registry = PromptRegistry()
    >>> v1 = registry.register('req-prompt', 'Requirements Prompt', 'Generate requirements for...')
    >>> v1.version
    '1.0.0'
    >>> v2 = registry.update('req-prompt', 'Improved requirements for...', change_notes='Added constraints')
    >>> v2.version
    '1.1.0'
    """

    def __init__(self, scorer: PromptQualityScorer | None = None) -> None:
        self._scorer = scorer or PromptQualityScorer()
        # prompt_id → ordered list of PromptVersion
        self._store: dict[str, list[PromptVersion]] = {}

    def register(
        self,
        prompt_id: str,
        name: str,
        content: str,
        author: str = 'unknown',
        metadata: dict[str, Any] | None = None,
    ) -> PromptVersion:
        """Register a new prompt and return its first version."""
        quality = self._scorer.score(content)
        version = PromptVersion(
            prompt_id=prompt_id,
            name=name,
            content=content,
            version='1.0.0',
            author=author,
            quality_score=quality,
            metadata=metadata or {},
        )
        self._store[prompt_id] = [version]
        return version

    def update(
        self,
        prompt_id: str,
        content: str,
        author: str | None = None,
        change_notes: str = '',
        metadata: dict[str, Any] | None = None,
    ) -> PromptVersion:
        """Create a new minor version of an existing prompt.

        Raises :exc:`KeyError` if *prompt_id* is not registered.
        """
        history = self._store.get(prompt_id)
        if not history:
            raise KeyError(f'Prompt not registered: {prompt_id!r}')
        latest = history[-1]
        quality = self._scorer.score(content)
        new_version = PromptVersion(
            prompt_id=prompt_id,
            name=latest.name,
            content=content,
            version=_bump_minor(latest.version),
            author=author or latest.author,
            quality_score=quality,
            change_notes=change_notes,
            metadata=metadata if metadata is not None else dict(latest.metadata),
        )
        history.append(new_version)
        return new_version

    def approve(self, prompt_id: str, approver: str = 'system') -> PromptVersion:
        """Set the latest version of *prompt_id* to APPROVED."""
        version = self.latest(prompt_id)
        if version is None:
            raise KeyError(f'Prompt not registered: {prompt_id!r}')
        version.status = PromptApprovalStatus.APPROVED
        version.metadata['approved_by'] = approver
        return version

    def reject(self, prompt_id: str, reason: str = '') -> PromptVersion:
        """Set the latest version of *prompt_id* to REJECTED."""
        version = self.latest(prompt_id)
        if version is None:
            raise KeyError(f'Prompt not registered: {prompt_id!r}')
        version.status = PromptApprovalStatus.REJECTED
        if reason:
            version.metadata['rejection_reason'] = reason
        return version

    def latest(self, prompt_id: str) -> PromptVersion | None:
        """Return the most recent version of *prompt_id*, or ``None``."""
        history = self._store.get(prompt_id)
        return history[-1] if history else None

    def history(self, prompt_id: str) -> list[PromptVersion]:
        """Return the full version history of *prompt_id* (oldest first)."""
        return list(self._store.get(prompt_id, []))

    def all_prompts(self) -> list[PromptVersion]:
        """Return the latest version of every registered prompt."""
        return [history[-1] for history in self._store.values() if history]
