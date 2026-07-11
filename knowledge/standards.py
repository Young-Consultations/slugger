"""Engineering standards repository and pattern retrieval.

Provides :class:`StandardsRepository` for storing and searching engineering
standards, best practices, and reusable patterns.  Complements the
:class:`~knowledge.indexer.KnowledgeIndexer` with a structured, in-memory
registry aimed at agent consumption.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StandardCategory(str, Enum):
    """Categories of engineering standards."""

    ARCHITECTURE = 'architecture'
    CODING = 'coding'
    TESTING = 'testing'
    SECURITY = 'security'
    DOCUMENTATION = 'documentation'
    DEPLOYMENT = 'deployment'
    PROMPT_ENGINEERING = 'prompt_engineering'
    WORKFLOW = 'workflow'
    OTHER = 'other'


@dataclass
class EngineeringStandard:
    """A single engineering standard or best practice.

    Parameters
    ----------
    standard_id:
        Unique stable identifier (e.g. ``'SEC-001'``).
    title:
        Short, descriptive title.
    description:
        Full description of the standard.
    category:
        Broad category this standard belongs to.
    rationale:
        Why this standard exists.
    examples:
        Concrete usage examples.
    references:
        External references (URLs, document names).
    tags:
        Free-text search tags.
    mandatory:
        Whether this standard is mandatory or advisory.
    metadata:
        Arbitrary extra data.
    """

    standard_id: str
    title: str
    description: str
    category: StandardCategory = StandardCategory.OTHER
    rationale: str = ''
    examples: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    mandatory: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'standard_id': self.standard_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'rationale': self.rationale,
            'examples': list(self.examples),
            'references': list(self.references),
            'tags': list(self.tags),
            'mandatory': self.mandatory,
        }


@dataclass
class Pattern:
    """A reusable engineering pattern (design pattern, architectural pattern, etc.).

    Parameters
    ----------
    pattern_id:
        Unique stable identifier (e.g. ``'PAT-001'``).
    name:
        Pattern name (e.g. ``'Repository Pattern'``).
    description:
        What the pattern does and when to use it.
    category:
        Broad category.
    problem:
        The problem the pattern solves.
    solution:
        How the pattern solves the problem.
    consequences:
        Trade-offs and consequences of using the pattern.
    tags:
        Free-text search tags.
    template:
        Optional code or document template for this pattern.
    """

    pattern_id: str
    name: str
    description: str
    category: StandardCategory = StandardCategory.OTHER
    problem: str = ''
    solution: str = ''
    consequences: str = ''
    tags: list[str] = field(default_factory=list)
    template: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {
            'pattern_id': self.pattern_id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'problem': self.problem,
            'solution': self.solution,
            'consequences': self.consequences,
            'tags': list(self.tags),
            'has_template': bool(self.template),
        }


def _matches(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(t.lower() in lower for t in terms)


class StandardsRepository:
    """In-memory repository of engineering standards and patterns.

    Supports registration, retrieval by ID, category-based filtering,
    and free-text search across titles, descriptions, and tags.

    Examples
    --------
    >>> repo = StandardsRepository()
    >>> repo.add_standard(EngineeringStandard('SEC-001', 'Input Validation', 'Always validate...', StandardCategory.SECURITY))
    >>> results = repo.search_standards('validation')
    >>> results[0].standard_id
    'SEC-001'
    """

    def __init__(self) -> None:
        self._standards: dict[str, EngineeringStandard] = {}
        self._patterns: dict[str, Pattern] = {}

    # ------------------------------------------------------------------
    # Standards
    # ------------------------------------------------------------------

    def add_standard(self, standard: EngineeringStandard) -> None:
        """Register an engineering standard."""
        self._standards[standard.standard_id] = standard

    def get_standard(self, standard_id: str) -> EngineeringStandard | None:
        """Return the standard with *standard_id*, or ``None``."""
        return self._standards.get(standard_id)

    def standards_by_category(self, category: StandardCategory) -> list[EngineeringStandard]:
        """Return all standards in *category*."""
        return [s for s in self._standards.values() if s.category == category]

    def mandatory_standards(self) -> list[EngineeringStandard]:
        """Return all mandatory standards."""
        return [s for s in self._standards.values() if s.mandatory]

    def search_standards(self, query: str) -> list[EngineeringStandard]:
        """Return standards that match *query* (searches title, description, tags)."""
        terms = query.split()
        if not terms:
            return list(self._standards.values())
        return [
            s for s in self._standards.values()
            if _matches(s.title + ' ' + s.description + ' ' + ' '.join(s.tags), terms)
        ]

    def all_standards(self) -> list[EngineeringStandard]:
        """Return all registered standards."""
        return list(self._standards.values())

    # ------------------------------------------------------------------
    # Patterns
    # ------------------------------------------------------------------

    def add_pattern(self, pattern: Pattern) -> None:
        """Register a reusable pattern."""
        self._patterns[pattern.pattern_id] = pattern

    def get_pattern(self, pattern_id: str) -> Pattern | None:
        """Return the pattern with *pattern_id*, or ``None``."""
        return self._patterns.get(pattern_id)

    def patterns_by_category(self, category: StandardCategory) -> list[Pattern]:
        """Return all patterns in *category*."""
        return [p for p in self._patterns.values() if p.category == category]

    def search_patterns(self, query: str) -> list[Pattern]:
        """Return patterns that match *query* (searches name, description, tags)."""
        terms = query.split()
        if not terms:
            return list(self._patterns.values())
        return [
            p for p in self._patterns.values()
            if _matches(p.name + ' ' + p.description + ' ' + ' '.join(p.tags), terms)
        ]

    def all_patterns(self) -> list[Pattern]:
        """Return all registered patterns."""
        return list(self._patterns.values())

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return a summary of the repository contents."""
        return {
            'standards_count': len(self._standards),
            'patterns_count': len(self._patterns),
            'mandatory_standards': len(self.mandatory_standards()),
            'categories': sorted({s.category.value for s in self._standards.values()} | {p.category.value for p in self._patterns.values()}),
        }
