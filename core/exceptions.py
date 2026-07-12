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
