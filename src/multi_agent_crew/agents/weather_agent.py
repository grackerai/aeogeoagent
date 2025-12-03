"""Weather Agent implementation."""

from crewai import Agent
from typing import Optional

from .base import BaseAgent
from ..tools.data.weather_tool import WeatherTool
from ..core.config import settings


class WeatherAgent(BaseAgent):
    """Agent responsible for weather reporting."""
    
    def create(self, location: Optional[str] = None) -> Agent:
        """
        Create the Weather Reporter agent.
        
        Args:
            location: Optional default location context
            
        Returns:
            Agent: Weather Reporter agent
        """
        role = "Weather Reporter"
        if location:
            role += f" for {location}"
            
        return Agent(
            role=role,
            goal="Provide accurate and concise temperature information",
            backstory=(
                "You are an expert meteorologist with years of experience in weather reporting. "
                "You have a talent for presenting weather information in a clear and accessible way. "
                "Your mission is to help people understand the current weather conditions quickly and accurately."
            ),
            tools=[WeatherTool()],
            verbose=True,
            llm=settings.default_llm_model,
            allow_delegation=False
        )
