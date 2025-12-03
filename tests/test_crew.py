"""Integration tests for WeatherCrew."""

import pytest
from unittest.mock import Mock, patch
from multi_agent_crew.crews.weather_crew import WeatherCrew


@patch('multi_agent_crew.crews.weather_crew.Crew')
@patch('multi_agent_crew.crews.weather_crew.AgentFactory')
def test_weather_crew_creation(mock_factory, mock_crew_class):
    """Test that the crew is created correctly."""
    # Mock agent creation
    from crewai import Agent
    import os
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
        real_agent = Agent(role="Test", goal="Test", backstory="Test", llm="gpt-4o-mini")
        mock_factory.create.return_value = real_agent
    
    # Mock Crew instance
    mock_crew_instance = Mock()
    mock_crew_instance.agents = [real_agent]  # Configure agents property
    mock_crew_instance.tasks = [Mock()]       # Configure tasks property
    mock_crew_class.return_value = mock_crew_instance
    
    crew_wrapper = WeatherCrew()
    crew = crew_wrapper.create()
    
    # Verify AgentFactory was called
    mock_factory.create.assert_called_with("weather")
    
    # Verify Crew was initialized with correct args
    mock_crew_class.assert_called_once()
    call_args = mock_crew_class.call_args[1]
    assert len(call_args['agents']) == 1
    assert len(call_args['tasks']) == 1
