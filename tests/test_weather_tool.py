"""Unit tests for WeatherTool."""

import pytest
from unittest.mock import patch, Mock
from multi_agent_crew.tools.weather_tool import WeatherTool
import requests


class TestWeatherTool:
    """Test suite for WeatherTool."""
    
    def setup_method(self):
        """Clear cache before each test."""
        WeatherTool.clear_cache()
    
    @patch('multi_agent_crew.tools.weather_tool.requests.get')
    def test_weather_tool_valid_location(self, mock_get):
        """Test fetching weather for a valid location."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = "London: ☀️  +15°C"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = WeatherTool()
        result = tool._run("London")
        
        assert "London" in result
        assert "°C" in result
        mock_get.assert_called_once()
    
    @patch('multi_agent_crew.tools.weather_tool.requests.get')
    def test_weather_tool_caching(self, mock_get):
        """Test that caching works correctly."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = "Paris: 🌧  +10°C"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = WeatherTool()
        
        # First call - should hit API
        result1 = tool._run("Paris")
        assert "Paris" in result1
        assert "(cached)" not in result1
        
        # Second call - should use cache
        result2 = tool._run("Paris")
        assert "Paris" in result2
        assert "(cached)" in result2
        
        # Should only call API once
        assert mock_get.call_count == 1
    
    @patch('multi_agent_crew.tools.weather_tool.requests.get')
    def test_weather_tool_timeout(self, mock_get):
        """Test handling of timeout errors."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        tool = WeatherTool()
        result = tool._run("London")
        
        assert "timed out" in result.lower()
    
    @patch('multi_agent_crew.tools.weather_tool.requests.get')
    def test_weather_tool_network_error(self, mock_get):
        """Test handling of network errors."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        tool = WeatherTool()
        result = tool._run("London")
        
        assert "error" in result.lower()
    
    @patch('multi_agent_crew.tools.weather_tool.requests.get')
    def test_weather_tool_invalid_location(self, mock_get):
        """Test handling of invalid location."""
        mock_response = Mock()
        mock_response.text = "Unknown location"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = WeatherTool()
        result = tool._run("InvalidCityName12345")
        
        assert "unable to find" in result.lower() or "unknown" in result.lower()
    
    @patch('multi_agent_crew.tools.weather_tool.requests.get')
    def test_weather_tool_empty_location(self, mock_get):
        """Test handling of empty location."""
        mock_response = Mock()
        mock_response.text = ""
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = WeatherTool()
        result = tool._run("")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        tool = WeatherTool()
        
        # Add something to cache manually
        tool._cache["test"] = ("data", None)
        assert len(tool._cache) > 0
        
        # Clear cache
        WeatherTool.clear_cache()
        assert len(tool._cache) == 0
    
    @patch('multi_agent_crew.tools.weather_tool.requests.get')
    def test_weather_tool_case_insensitive_cache(self, mock_get):
        """Test that cache is case-insensitive."""
        mock_response = Mock()
        mock_response.text = "Tokyo: ☁️  +20°C"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = WeatherTool()
        
        # First call with lowercase
        result1 = tool._run("tokyo")
        assert "(cached)" not in result1
        
        # Second call with different case - should use cache
        result2 = tool._run("TOKYO")
        assert "(cached)" in result2
        
        # Should only call API once
        assert mock_get.call_count == 1
