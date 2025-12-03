"""System logger backend - default fallback."""

import logging
import sys
from typing import Dict, Optional
from contextlib import contextmanager
from datetime import datetime

from .base import ObservabilityBackend


class SystemLoggerBackend(ObservabilityBackend):
    """Default observability backend using Python's logging module."""
    
    def __init__(self, log_level: str = "INFO", **kwargs):
        """
        Initialize system logger.
        
        Args:
            log_level: Logging level
            **kwargs: Ignored arguments
        """
        self.logger = logging.getLogger("multi_agent_crew")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Add console handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Metrics storage (in-memory for fallback)
        self._metrics: Dict[str, list] = {}
        
        self.logger.info("SystemLoggerBackend initialized (fallback mode)")
    
    def log(self, level: str, message: str, **kwargs) -> None:
        """Log a message."""
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        
        if kwargs:
            extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{message} | {extra_info}"
        
        log_func(message)
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric (stored in memory, logged)."""
        if name not in self._metrics:
            self._metrics[name] = []
        
        metric_data = {
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'tags': tags or {}
        }
        self._metrics[name].append(metric_data)
        
        # Log the metric
        tag_str = ", ".join(f"{k}={v}" for k, v in (tags or {}).items())
        self.logger.debug(f"METRIC: {name}={value} [{tag_str}]")
    
    @contextmanager
    def trace(self, name: str, **attributes):
        """Create a trace span (logged)."""
        trace_id = f"{name}_{datetime.now().timestamp()}"
        
        attr_str = ", ".join(f"{k}={v}" for k, v in attributes.items())
        self.logger.debug(f"TRACE START: {name} [{attr_str}] (id={trace_id})")
        
        start_time = datetime.now()
        
        try:
            yield trace_id
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.debug(f"TRACE END: {name} (duration={duration:.3f}s, id={trace_id})")
    
    def flush(self) -> None:
        """Flush handlers."""
        for handler in self.logger.handlers:
            handler.flush()
    
    def close(self) -> None:
        """Close handlers."""
        for handler in self.logger.handlers:
            handler.close()
        self.logger.info("SystemLoggerBackend closed")
    
    def get_metrics(self, name: Optional[str] = None) -> Dict:
        """Get recorded metrics (for debugging)."""
        if name:
            return {name: self._metrics.get(name, [])}
        return self._metrics
