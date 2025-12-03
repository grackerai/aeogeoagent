"""SEO Agent implementation."""

from crewai import Agent
from typing import Optional

from .base import BaseAgent
from ..tools.data.gsc_tool import GSCTool
from ..tools.search.keyword_search_tool import KeywordSearchTool
from ..core.config import settings


class SEOAgent(BaseAgent):
    """Agent responsible for SEO analysis."""
    
    def create(self, domain: Optional[str] = None) -> Agent:
        """
        Create the SEO Analyst agent.
        
        Args:
            domain: Optional default domain context
            
        Returns:
            Agent: SEO Analyst agent
        """
        role = "SEO Analyst"
        if domain:
            role += f" for {domain}"
            
        return Agent(
            role=role,
            goal="Analyze Google Search Console data and verify keyword rankings",
            backstory=(
                "You are an expert SEO analyst with deep knowledge of search engine optimization "
                "and keyword research. You excel at analyzing search performance data and identifying "
                "opportunities to improve visibility. You have a talent for understanding how search "
                "engines rank content and can quickly assess a website's search presence."
            ),
            tools=[GSCTool(), KeywordSearchTool()],
            verbose=True,
            llm=settings.default_llm_model,
            allow_delegation=False
        )
