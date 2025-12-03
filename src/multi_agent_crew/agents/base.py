"""Base agent class with observability integration."""

from abc import ABC, abstractmethod
from typing import Optional, List, Any
from crewai import Agent

from ..core.observability import get_observability, ObservabilityBackend
from ..core.config import settings


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, observability: Optional[ObservabilityBackend] = None):
        """
        Initialize base agent.
        
        Args:
            observability: Optional observability backend (uses default if None)
        """
        self.obs = observability or get_observability()
        self.agent: Optional[Agent] = None
    
    @abstractmethod
    def create(self) -> Agent:
        """
        Create and return the CrewAI Agent instance.
        
        Returns:
            Agent: Configured CrewAI agent
        """
        pass
    
    def get_agent(self) -> Agent:
        """Get the agent instance, creating it if necessary."""
        if not self.agent:
            with self.obs.trace(f"create_agent_{self.__class__.__name__}"):
                self.agent = self.create()
        return self.agent
