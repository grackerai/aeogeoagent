"""Observability factory - creates appropriate backend with fallbacks."""

import logging
from typing import Optional

from .base import ObservabilityBackend
from .system_logger import SystemLoggerBackend

logger = logging.getLogger(__name__)


class ObservabilityFactory:
    """Factory for creating observability backends with fallback chain."""
    
    _instance: Optional[ObservabilityBackend] = None
    
    @classmethod
    def create(
        cls,
        backend: str = "system",
        **kwargs
    ) -> ObservabilityBackend:
        """
        Create observability backend with automatic fallback.
        
        Fallback chain:
        1. Requested backend (prometheus, grafana, datadog)
        2. System logger (always works)
        
        Args:
            backend: Backend type (system, prometheus, grafana, datadog)
            **kwargs: Backend-specific configuration
            
        Returns:
            ObservabilityBackend instance
        """
        if cls._instance is not None:
            return cls._instance
        
        backend = backend.lower()
        
        # Try requested backend
        if backend == "prometheus":
            try:
                from .prometheus import PrometheusBackend
                cls._instance = PrometheusBackend(**kwargs)
                logger.info("Using PrometheusBackend")
                return cls._instance
            except Exception as e:
                logger.warning(f"Failed to initialize Prometheus: {e}, falling back to SystemLogger")
        
        elif backend == "grafana":
            try:
                from .grafana import GrafanaBackend
                cls._instance = GrafanaBackend(**kwargs)
                logger.info("Using GrafanaBackend")
                return cls._instance
            except Exception as e:
                logger.warning(f"Failed to initialize Grafana: {e}, falling back to SystemLogger")
        
        elif backend == "datadog":
            try:
                from .datadog import DatadogBackend
                cls._instance = DatadogBackend(**kwargs)
                logger.info("Using DatadogBackend")
                return cls._instance
            except Exception as e:
                logger.warning(f"Failed to initialize Datadog: {e}, falling back to SystemLogger")
        
        # Default fallback: System logger (always works)
        cls._instance = SystemLoggerBackend(**kwargs)
        logger.info("Using SystemLoggerBackend (default)")
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        if cls._instance:
            cls._instance.close()
        cls._instance = None
    
    @classmethod
    def get_instance(cls) -> Optional[ObservabilityBackend]:
        """Get current instance."""
        return cls._instance
