from crewai.tools import BaseTool
from typing import Type, Dict, Tuple, ClassVar
from pydantic import BaseModel, Field
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WeatherToolInput(BaseModel):
    """Input schema for WeatherTool."""
    location: str = Field(..., description="The location to get the weather for (e.g., 'London', 'New York').")


class WeatherTool(BaseTool):
    name: str = "WeatherTool"
    description: str = (
        "A tool that fetches the current weather for a given location using wttr.in. "
        "It returns a text summary of the weather including temperature and conditions."
    )
    args_schema: Type[BaseModel] = WeatherToolInput
    
    # Cache storage (class variable shared across instances)
    _cache: ClassVar[Dict[str, Tuple[str, datetime]]] = {}
    _cache_duration: ClassVar[int] = 300  # 5 minutes in seconds

    def _run(self, location: str) -> str:
        """
        Fetch weather data for the given location.
        
        Args:
            location: The location to get weather for
            
        Returns:
            Weather information as a string
        """
        # Check cache
        cache_key = location.lower().strip()
        if cache_key in WeatherTool._cache:
            cached_data, timestamp = WeatherTool._cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=WeatherTool._cache_duration):
                logger.info(f"Using cached weather data for {location}")
                return f"{cached_data} (cached)"
        
        try:
            logger.info(f"Fetching weather data for {location}")
            # wttr.in returns a simple text response with ?format=3
            url = f"https://wttr.in/{location}?format=3"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.text.strip()
            
            # Validate response
            if not result or "Unknown location" in result:
                logger.warning(f"Invalid location: {location}")
                return f"Unable to find weather data for '{location}'. Please check the location name."
            
            # Update cache
            WeatherTool._cache[cache_key] = (result, datetime.now())
            logger.info(f"Successfully fetched weather for {location}: {result}")
            
            return result
            
        except requests.exceptions.Timeout:
            error_msg = f"Request timed out while fetching weather for {location}"
            logger.error(error_msg)
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error fetching weather for {location}: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error fetching weather for {location}: {str(e)}"
            logger.exception(error_msg)
            return error_msg
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the weather data cache."""
        cls._cache.clear()
        logger.info("Weather cache cleared")
