"""Custom exceptions for the multi-agent crew."""

class MultiAgentCrewError(Exception):
    """Base exception for all errors in the application."""
    pass


class ConfigurationError(MultiAgentCrewError):
    """Raised when there is a configuration error."""
    pass


class ToolError(MultiAgentCrewError):
    """Raised when a tool fails."""
    pass


class AgentError(MultiAgentCrewError):
    """Raised when an agent fails."""
    pass


class ObservabilityError(MultiAgentCrewError):
    """Raised when observability backend fails."""
    pass
