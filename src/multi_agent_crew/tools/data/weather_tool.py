"""Weather tool implementation."""

import requests
from typing import Type, Optional
from pydantic import BaseModel, Field

from ..base.cached_tool import CachedTool
from ...core.exceptions import ToolError


class WeatherToolInput(BaseModel):
    """Input schema for WeatherTool."""
    location: str = Field(..., description="The city or location to get weather for (e.g., 'London', 'Tokyo').")


class WeatherTool(CachedTool):
    name: str = "WeatherTool"
    description: str = (
        "A tool that fetches the current weather for a given location using wttr.in. "
        "Returns a string with the temperature and condition."
    )
    args_schema: Type[BaseModel] = WeatherToolInput

    def _run(self, location: str) -> str:
        """
        Fetch weather data for the given location.
        
        Args:
            location: The location to fetch weather for
            
        Returns:
            str: Weather report
        """
        return self._run_with_observability(self._fetch_weather, location)

    def _fetch_weather(self, location: str) -> str:
        """Internal method to fetch weather."""
        # Check cache
        cache_key = f"weather:{location.lower()}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return f"{cached} (cached)"
        
        try:
            # wttr.in format: %C+%t for Condition and Temperature
            url = f"https://wttr.in/{location}?format=%C+%t"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            weather_data = response.text.strip()
            
            # Update cache
            self._save_to_cache(cache_key, weather_data)
            
            return weather_data
            
        except requests.RequestException as e:
            raise ToolError(f"Failed to fetch weather for {location}: {str(e)}")
