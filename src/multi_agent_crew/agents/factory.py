"""Agent factory for creating agents."""

from typing import Dict, Type, Optional
from crewai import Agent

from .base import BaseAgent
from .seo_agent import SEOAgent
from ..core.exceptions import AgentError
from ..core.observability import get_observability


class AgentFactory:
    """Factory for creating agents."""
    
    _agents: Dict[str, Type[BaseAgent]] = {
        "seo": SEOAgent,
    }
    
    @classmethod
    def create(cls, agent_type: str, **kwargs) -> Agent:
        """
        Create an agent instance.
        
        Args:
            agent_type: Type of agent to create (seo)
            **kwargs: Configuration for the agent
            
        Returns:
            Agent: Configured CrewAI agent
            
        Raises:
            AgentError: If agent type is unknown
        """
        obs = get_observability()
        
        with obs.trace(f"factory_create_agent", agent_type=agent_type):
            if agent_type not in cls._agents:
                raise AgentError(f"Unknown agent type: {agent_type}")
            
            agent_cls = cls._agents[agent_type]
            agent_wrapper = agent_cls()
            return agent_wrapper.create(**kwargs)
    
    @classmethod
    def register(cls, agent_type: str, agent_cls: Type[BaseAgent]) -> None:
        """Register a new agent type."""
        cls._agents[agent_type] = agent_cls
