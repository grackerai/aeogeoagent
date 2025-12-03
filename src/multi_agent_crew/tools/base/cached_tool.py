"""Base tool class with caching and observability."""

from typing import Any, ClassVar, Dict, Optional, Tuple
from datetime import datetime, timedelta
from crewai.tools import BaseTool
from pydantic import PrivateAttr

from ...core.observability import get_observability
from ...core.config import settings


class CachedTool(BaseTool):
    """Base class for tools with built-in caching and observability."""
    
    _cache: ClassVar[Dict[str, Tuple[Any, datetime]]] = {}
    _cache_duration: ClassVar[int] = settings.cache_ttl_seconds
    _obs: Any = PrivateAttr()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._obs = get_observability()
    
    @property
    def obs(self):
        """Get observability backend."""
        if not hasattr(self, "_obs"):
            self._obs = get_observability()
        return self._obs
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Retrieve value from cache if valid."""
        if not settings.enable_caching:
            return None
            
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_duration):
                self.obs.record_metric("tool_cache_hit", 1, {"tool": self.name})
                return data
        
        self.obs.record_metric("tool_cache_miss", 1, {"tool": self.name})
        return None
    
    def _save_to_cache(self, key: str, data: Any) -> None:
        """Save value to cache."""
        if settings.enable_caching:
            self._cache[key] = (data, datetime.now())
    
    def _run_with_observability(self, func, *args, **kwargs):
        """Run tool method with tracing and metrics."""
        with self.obs.trace(f"tool_run_{self.name}", tool=self.name):
            try:
                result = func(*args, **kwargs)
                self.obs.record_metric("tool_run_success", 1, {"tool": self.name})
                return result
            except Exception as e:
                self.obs.record_metric("tool_run_error", 1, {"tool": self.name, "error": str(type(e).__name__)})
                raise
