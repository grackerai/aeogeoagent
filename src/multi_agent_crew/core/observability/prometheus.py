"""Prometheus backend adapter."""

from typing import Dict, Optional
from contextlib import contextmanager
from datetime import datetime
import logging

from .base import ObservabilityBackend
from .system_logger import SystemLoggerBackend

logger = logging.getLogger(__name__)


class PrometheusBackend(ObservabilityBackend):
    """Prometheus observability backend."""
    
    def __init__(self, port: int = 8000):
        """
        Initialize Prometheus backend.
        
        Args:
            port: Port for metrics endpoint
        """
        self.port = port
        self._fallback = SystemLoggerBackend()
        
        try:
            from prometheus_client import Counter, Histogram, Gauge, start_http_server
            
            # Start metrics server
            start_http_server(port)
            
            # Define metrics
            self.metrics_counter = Counter(
                'agent_operations_total',
                'Total agent operations',
                ['operation', 'agent', 'status']
            )
            
            self.duration_histogram = Histogram(
                'agent_operation_duration_seconds',
                'Agent operation duration',
                ['operation', 'agent']
            )
            
            self.active_operations = Gauge(
                'agent_active_operations',
                'Active agent operations',
                ['agent']
            )
            
            self._prometheus_available = True
            logger.info(f"PrometheusBackend initialized on port {port}")
            
        except ImportError:
            logger.warning("prometheus_client not installed, falling back to SystemLogger")
            self._prometheus_available = False
        except OSError as e:
            logger.warning(f"Failed to start Prometheus server: {e}, falling back to SystemLogger")
            self._prometheus_available = False
    
    def log(self, level: str, message: str, **kwargs) -> None:
        """Log via fallback."""
        self._fallback.log(level, message, **kwargs)
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record metric to Prometheus."""
        if not self._prometheus_available:
            self._fallback.record_metric(name, value, tags)
            return
        
        try:
            tags = tags or {}
            
            # Map to appropriate Prometheus metric
            if 'counter' in name.lower():
                self.metrics_counter.labels(**tags).inc(value)
            elif 'duration' in name.lower():
                self.duration_histogram.labels(**tags).observe(value)
            elif 'active' in name.lower():
                self.active_operations.labels(**tags).set(value)
            else:
                # Default to counter
                self.metrics_counter.labels(operation=name, **tags).inc(value)
                
        except Exception as e:
            logger.error(f"Failed to record Prometheus metric: {e}")
            self._fallback.record_metric(name, value, tags)
    
    @contextmanager
    def trace(self, name: str, **attributes):
        """Create trace span with duration tracking."""
        if not self._prometheus_available:
            with self._fallback.trace(name, **attributes):
                yield
            return
        
        agent = attributes.get('agent', 'unknown')
        self.active_operations.labels(agent=agent).inc()
        
        start_time = datetime.now()
        
        try:
            with self._fallback.trace(name, **attributes):
                yield
            
            # Record success
            self.metrics_counter.labels(
                operation=name,
                agent=agent,
                status='success'
            ).inc()
            
        except Exception as e:
            # Record failure
            self.metrics_counter.labels(
                operation=name,
                agent=agent,
                status='error'
            ).inc()
            raise
            
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            self.duration_histogram.labels(operation=name, agent=agent).observe(duration)
            self.active_operations.labels(agent=agent).dec()
    
    def flush(self) -> None:
        """Flush fallback."""
        self._fallback.flush()
    
    def close(self) -> None:
        """Close backend."""
        self._fallback.close()
        logger.info("PrometheusBackend closed")
