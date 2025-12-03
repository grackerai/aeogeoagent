"""Base interface for observability backends."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from contextlib import contextmanager


class ObservabilityBackend(ABC):
    """Abstract base class for observability backends."""
    
    @abstractmethod
    def log(self, level: str, message: str, **kwargs) -> None:
        """
        Log a message.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            **kwargs: Additional context
        """
        pass
    
    @abstractmethod
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a metric.
        
        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags/labels
        """
        pass
    
    @abstractmethod
    @contextmanager
    def trace(self, name: str, **attributes):
        """
        Create a trace span.
        
        Args:
            name: Span name
            **attributes: Span attributes
            
        Yields:
            Span context
        """
        pass
    
    @abstractmethod
    def flush(self) -> None:
        """Flush any buffered data."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the backend and cleanup resources."""
        pass


class ObservabilityContext:
    """Context for passing observability data."""
    
    def __init__(self, backend: ObservabilityBackend):
        self.backend = backend
        self._context: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any) -> None:
        """Set context value."""
        self._context[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get context value."""
        return self._context.get(key, default)
    
    def clear(self) -> None:
        """Clear context."""
        self._context.clear()
