"""Capability models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Capability(str, Enum):
    PRODUCT_VISION = 'product_vision'
    REQUIREMENTS = 'requirements'
    USER_STORIES = 'user_stories'
    PROJECT_PLANNING = 'project_planning'
    SYSTEM_DESIGN = 'system_design'
    ADR = 'adr'
    DIAGRAM = 'diagram'
    API_DESIGN = 'api_design'
    CODE_GENERATION = 'code_generation'
    CODE_REVIEW = 'code_review'
    REFACTORING = 'refactoring'
    DOCUMENTATION = 'documentation'
    TEST_GENERATION = 'test_generation'
    TEST_EXECUTION = 'test_execution'
    SECURITY_REVIEW = 'security_review'
    PERFORMANCE_ANALYSIS = 'performance_analysis'
    DEPLOYMENT = 'deployment'
    CI_CD = 'ci_cd'
    MONITORING = 'monitoring'
    RELEASE = 'release'
    KNOWLEDGE = 'knowledge'
    GITHUB = 'github'
    CHANGELOG = 'changelog'
    REFLECTION = 'reflection'


@dataclass(slots=True, frozen=True)
class CapabilityDescriptor:
    """Typed description of a capability contract."""

    capability: Capability
    description: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
