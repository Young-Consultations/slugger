"""Capability-based runtime provider and service resolution (CC-003).

This module defines named AI capabilities and a resolver that selects the
appropriate provider/service implementation based on project preference,
environment profile, health, and fallback policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Capability(str, Enum):
    """Named AI and platform capabilities required by Slugger agents.

    Each capability maps to one or more provider implementations.
    Agents must declare their required capability instead of a concrete
    provider class name.
    """

    PLANNING_GENERATION = "planning_generation"
    """Generate requirements, user stories, and project plans (ChatGPT)."""

    PROMPT_REVIEW = "prompt_review"
    """Review prompt quality and approve prompt changes (ChatGPT)."""

    CODE_AGENT = "code_agent"
    """Agentic repository coding sessions (Codex)."""

    CODE_REVIEW = "code_review"
    """Structured code review and finding triage (Codex or ChatGPT)."""

    REFACTOR = "refactor"
    """File-scoped code refactoring within approved workspace (Codex)."""

    EMBEDDINGS = "embeddings"
    """Text embedding for knowledge indexing (OpenAI or Anthropic)."""

    DESIGN = "design"
    """UI/UX design generation and export (Canva)."""

    REPOSITORY_MANAGEMENT = "repository_management"
    """Issue, PR, branch, and release management (GitHub)."""

    WORKFLOW_MANAGEMENT = "workflow_management"
    """CI/CD trigger and status polling (GitHub Actions)."""


@dataclass
class CapabilityResolution:
    """Result of resolving a capability to a concrete implementation.

    Records the selected implementation, model/tool version, whether a
    fallback was used, and the health state at resolution time.
    """

    capability: Capability
    provider_name: str
    provider_type: str
    model: str = ""
    used_fallback: bool = False
    fallback_reason: str = ""
    available: bool = True
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability.value,
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "model": self.model,
            "used_fallback": self.used_fallback,
            "fallback_reason": self.fallback_reason,
            "available": self.available,
        }


class CapabilityNotAvailableError(Exception):
    """Raised in strict mode when a mandatory capability cannot be resolved."""

    def __init__(self, capability: Capability, reason: str = "") -> None:
        self.capability = capability
        msg = f"Capability {capability.value!r} is not available"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


# ---------------------------------------------------------------------------
# Default capability → provider mapping
# ---------------------------------------------------------------------------

#: Maps each capability to an ordered list of preferred provider names.
#: The first available provider that passes a health check is selected.
DEFAULT_CAPABILITY_PROVIDERS: dict[Capability, list[str]] = {
    Capability.PLANNING_GENERATION: ["chatgpt", "openai", "mock"],
    Capability.PROMPT_REVIEW: ["chatgpt", "openai", "mock"],
    Capability.CODE_AGENT: ["codex", "mock"],
    Capability.CODE_REVIEW: ["codex", "chatgpt", "mock"],
    Capability.REFACTOR: ["codex", "mock"],
    Capability.EMBEDDINGS: ["openai", "anthropic", "mock"],
    Capability.DESIGN: ["canva", "mock"],
    Capability.REPOSITORY_MANAGEMENT: ["github", "mock"],
    Capability.WORKFLOW_MANAGEMENT: ["github", "mock"],
}

NON_PRODUCTION_PROFILES = frozenset({"development", "dev", "test", "testing", "ci"})


class CapabilityResolver:
    """Resolve AI and platform capabilities at runtime.

    Resolution order for a capability:
    1. If the project brief specifies a coding-agent preference, honour it for
       ``CODE_AGENT``, ``CODE_REVIEW``, and ``REFACTOR`` capabilities.
    2. Try providers in the configured fallback order.
    3. Perform a bounded health check on each candidate.
    4. In strict mode, raise :exc:`CapabilityNotAvailableError` if only a mock
       provider is available and mock fallback is not allowed.

    Parameters
    ----------
    provider_registry:
        Registered provider instances.
    capability_map:
        Override the default capability → provider-name mapping.
    strict_mode:
        When ``True``, mock providers are not accepted as fallbacks.
    allow_mock:
        When ``True`` (default), mock providers are accepted in non-strict mode
        for non-production profiles.
    """

    def __init__(
        self,
        provider_registry: Any,
        capability_map: dict[Capability, list[str]] | None = None,
        strict_mode: bool = False,
        allow_mock: bool = True,
        profile: str = "development",
    ) -> None:
        self._registry = provider_registry
        self._capability_map = capability_map or dict(DEFAULT_CAPABILITY_PROVIDERS)
        self.strict_mode = strict_mode
        self.allow_mock = allow_mock
        self.profile = profile

    def resolve(
        self,
        capability: Capability,
        preferred_provider: str | None = None,
        profile: str | None = None,
    ) -> CapabilityResolution:
        """Resolve *capability* to a concrete provider implementation.

        Parameters
        ----------
        capability:
            The required capability.
        preferred_provider:
            Optional override (e.g. from :attr:`ProjectBrief.coding_agent`).

        Returns
        -------
        CapabilityResolution
            Contains the selected provider name, type, model, and health info.

        Raises
        ------
        CapabilityNotAvailableError
            In strict mode when no non-mock provider is available.
        """
        return self._resolve(
            capability, preferred_provider=preferred_provider, profile=profile
        )

    def resolve_strict(
        self,
        capability: Capability,
        preferred_provider: str | None = None,
        profile: str = "production",
    ) -> CapabilityResolution:
        """Resolve *capability* without permitting mock fallback."""
        try:
            return self._resolve(
                capability,
                preferred_provider=preferred_provider,
                profile=profile,
                require_real_provider=True,
            )
        except CapabilityNotAvailableError as exc:
            raise RuntimeError(str(exc)) from exc

    def _resolve(
        self,
        capability: Capability,
        preferred_provider: str | None = None,
        profile: str | None = None,
        require_real_provider: bool = False,
    ) -> CapabilityResolution:
        active_profile = (profile or self.profile).strip().lower()
        candidates = list(self._capability_map.get(capability, ["mock"]))
        if preferred_provider and preferred_provider not in candidates:
            candidates.insert(0, preferred_provider)
        elif preferred_provider and preferred_provider in candidates:
            candidates.remove(preferred_provider)
            candidates.insert(0, preferred_provider)

        last_reason = "no candidates configured"
        for name in candidates:
            is_mock = name == "mock"
            if is_mock and (self.strict_mode or require_real_provider):
                last_reason = "mock fallback forbidden in strict mode"
                continue
            if is_mock and active_profile not in NON_PRODUCTION_PROFILES:
                last_reason = (
                    f"mock providers are not allowed in profile {active_profile!r}"
                )
                continue
            if is_mock and not self.allow_mock:
                last_reason = "mock providers not allowed"
                continue
            try:
                provider = self._registry.resolve(name)
            except (KeyError, Exception) as exc:
                last_reason = str(exc)
                continue
            try:
                health = provider.health_check()
                available = health.available
                model = health.model or ""
                provider_type = getattr(
                    provider.config, "provider_type", type(provider).__name__
                )
                if hasattr(provider_type, "value"):
                    provider_type = provider_type.value
                else:
                    provider_type = str(provider_type)
            except Exception as exc:
                last_reason = f"health check failed: {exc}"
                continue
            if not available:
                last_reason = "provider unavailable"
                continue
            used_fallback = name != candidates[0] if candidates else False
            return CapabilityResolution(
                capability=capability,
                provider_name=name,
                provider_type=str(provider_type),
                model=model,
                used_fallback=used_fallback,
                available=True,
            )

        if self._should_raise_on_failure(active_profile, require_real_provider):
            raise CapabilityNotAvailableError(capability, last_reason)
        return CapabilityResolution(
            capability=capability,
            provider_name="mock",
            provider_type="mock",
            available=True,
            used_fallback=True,
            fallback_reason=f"all providers exhausted: {last_reason}",
        )

    def _should_raise_on_failure(
        self, profile: str, require_real_provider: bool
    ) -> bool:
        return (
            self.strict_mode
            or require_real_provider
            or not self.allow_mock
            or profile not in NON_PRODUCTION_PROFILES
        )

    def diagnostics(self) -> dict[str, Any]:
        """Return a capability resolution matrix for all known capabilities.

        Useful for startup diagnostics and operator visibility.
        """
        result: dict[str, Any] = {}
        for cap in Capability:
            try:
                resolution = self.resolve(cap)
                result[cap.value] = resolution.to_dict()
            except CapabilityNotAvailableError as exc:
                result[cap.value] = {"available": False, "error": str(exc)}
        return result

    def validate_mandatory(self, capabilities: list[Capability]) -> list[str]:
        """Validate that each listed capability is resolvable.

        Returns a list of error messages (empty = all OK).
        """
        errors: list[str] = []
        for cap in capabilities:
            try:
                resolution = self.resolve(cap)
                if not resolution.available:
                    errors.append(
                        f"Capability {cap.value!r} resolved to unavailable provider"
                    )
                if self.strict_mode and resolution.provider_name == "mock":
                    errors.append(
                        f"Capability {cap.value!r} resolved to mock in strict mode"
                    )
            except CapabilityNotAvailableError as exc:
                errors.append(str(exc))
        return errors
