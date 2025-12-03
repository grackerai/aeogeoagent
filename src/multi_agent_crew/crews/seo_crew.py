"""SEO crew implementation."""

from crewai import Crew, Process
from typing import Dict, Any

from .base import BaseCrew
from ..agents.factory import AgentFactory
from ..tasks.seo.tasks import SEOTasks


class SEOCrew(BaseCrew):
    """Crew for SEO analysis."""
    
    def create(self) -> Crew:
        """Create the SEO crew."""
        seo_agent = AgentFactory.create("seo")
        tasks = SEOTasks()
        
        fetch_task = tasks.fetch_keywords(
            seo_agent, 
            "{domain}", 
            "{num_keywords}",
            "{date_range}",
            "{sort_by}"
        )
        verify_task = tasks.verify_rankings(seo_agent, "{domain}", "{company_name}", [fetch_task])
        
        return Crew(
            agents=[seo_agent],
            tasks=[fetch_task, verify_task],
            process=Process.sequential,
            verbose=True
        )
