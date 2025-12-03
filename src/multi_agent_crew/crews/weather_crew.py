"""Weather crew implementation."""

from crewai import Crew, Process
from typing import Dict, Any

from .base import BaseCrew
from ..agents.factory import AgentFactory
from ..tasks.weather.tasks import WeatherTasks


class WeatherCrew(BaseCrew):
    """Crew for weather reporting."""
    
    def create(self) -> Crew:
        """Create the weather crew."""
        # Create agents
        weather_agent = AgentFactory.create("weather")
        
        # Create tasks
        tasks = WeatherTasks()
        
        # We need to defer task creation until run time to get inputs
        # But CrewAI expects tasks at creation. 
        # For this restructure, we'll use a slightly different pattern
        # where we create the crew with generic tasks or recreate it per run.
        # Here we'll return a configured crew but the tasks will need inputs injected.
        
        # NOTE: In a real production system, we might use a dynamic task creation
        # or pass inputs differently. For now, we'll create a generic task structure.
        
        return Crew(
            agents=[weather_agent],
            tasks=[
                tasks.report_weather(weather_agent, "{location}")
            ],
            process=Process.sequential,
            verbose=True
        )
    
    def run(self, inputs: Dict[str, Any]) -> Any:
        """Run the weather crew."""
        # Override run to handle dynamic agent creation if needed
        # or just pass inputs to kickoff
        return super().run(inputs)
