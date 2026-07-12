"""Custom exceptions for Slugger."""


class SluggerError(Exception):
    """Base class for Slugger-specific exceptions."""


class ConfigurationError(SluggerError):
    """Raised when configuration is invalid."""


class AgentError(SluggerError):
    """Raised when agent execution fails."""


class WorkflowError(SluggerError):
    """Raised when workflow execution fails."""


class ProviderError(SluggerError):
    """Raised when a provider cannot complete its work."""


class CodexNotAvailableError(SluggerError):
    """Raised when the production Codex adapter is required but unavailable."""


class PluginError(SluggerError):
    """Raised when plugin loading or health checks fail."""


class ValidationError(SluggerError):
    """Raised when validation blocks progress."""


class RemediationExhaustedError(SluggerError):
    """Raised when bounded remediation cannot resolve a defect automatically."""

    def __init__(self, message: str, *, result: object | None = None) -> None:
        super().__init__(message)
        self.result = result
