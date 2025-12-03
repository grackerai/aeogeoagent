"""Observability module - pluggable backends with fallback."""

from .base import ObservabilityBackend, ObservabilityContext
from .system_logger import SystemLoggerBackend
from .factory import ObservabilityFactory

__all__ = [
    'ObservabilityBackend',
    'ObservabilityContext',
    'SystemLoggerBackend',
    'ObservabilityFactory',
]


# Convenience functions
def get_observability(backend: str = "system", **kwargs) -> ObservabilityBackend:
    """Get observability backend instance."""
    return ObservabilityFactory.create(backend, **kwargs)


def reset_observability() -> None:
    """Reset observability instance (for testing)."""
    ObservabilityFactory.reset()
