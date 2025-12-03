"""Unit tests for WeatherTool."""

import pytest
from unittest.mock import Mock, patch
from multi_agent_crew.tools.data.weather_tool import WeatherTool
from multi_agent_crew.core.exceptions import ToolError


@pytest.fixture
def weather_tool():
    # Clear cache before test
    WeatherTool._cache.clear()
    return WeatherTool()


def test_weather_tool_initialization(weather_tool):
    """Test that the tool is initialized correctly."""
    assert weather_tool.name == "WeatherTool"
    assert "fetches the current weather" in weather_tool.description
    assert weather_tool.obs is not None


@patch('multi_agent_crew.tools.data.weather_tool.requests.get')
def test_fetch_weather_success(mock_get, weather_tool):
    """Test successful weather fetch."""
    # Mock response
    mock_response = Mock()
    mock_response.text = "Sunny +25°C"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = weather_tool._run("London")
    
    assert result == "Sunny +25°C"
    mock_get.assert_called_once()
    assert "London" in mock_get.call_args[0][0]


@patch('multi_agent_crew.tools.data.weather_tool.requests.get')
def test_fetch_weather_cached(mock_get, weather_tool):
    """Test that cached result is returned."""
    # Mock response
    mock_response = Mock()
    mock_response.text = "Sunny +25°C"
    mock_get.return_value = mock_response

    # First call
    weather_tool._run("London")
    
    # Second call should use cache
    result = weather_tool._run("London")
    
    assert "cached" in result
    # requests.get should only be called once
    mock_get.assert_called_once()


@patch('multi_agent_crew.tools.data.weather_tool.requests.get')
def test_fetch_weather_error(mock_get, weather_tool):
    """Test error handling."""
    # Mock error
    mock_get.side_effect = Exception("Network error")

    with pytest.raises(Exception):
        weather_tool._run("London")
