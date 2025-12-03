"""Weather tasks definition."""

from crewai import Task
from ...agents.weather_agent import WeatherAgent
from ...core.config import settings


class WeatherTasks:
    """Tasks for weather reporting."""
    
    def report_weather(self, agent, location: str) -> Task:
        """
        Create a task to report weather.
        
        Args:
            agent: The agent to perform the task
            location: The location to report on
            
        Returns:
            Task: The configured task
        """
        return Task(
            description=f"""
                Get the current temperature for {location}.
                Use the WeatherTool to fetch the weather information.
                Present the temperature in a clear and concise format.
            """,
            expected_output=f"""
                A brief, friendly report containing the current temperature for {location}.
                Include the location name and temperature in the output.
            """,
            agent=agent
        )
