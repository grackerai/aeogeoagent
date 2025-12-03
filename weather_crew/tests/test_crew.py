"""Integration tests for the weather crew."""

import pytest
from unittest.mock import patch, Mock
import os


class TestWeatherCrew:
    """Integration tests for WeatherCrew."""
    
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'})
    @patch('multi_agent_crew.crew.Agent')
    def test_crew_initialization(self, mock_agent):
        """Test that crew can be initialized."""
        from multi_agent_crew.crew import WeatherCrew
        
        # Mock the agent to avoid LLM initialization
        mock_agent.return_value = Mock()
        
        crew = WeatherCrew()
        assert crew is not None
    
    def test_crew_structure(self):
        """Test that crew class has required methods."""
        from multi_agent_crew.crew import WeatherCrew
        
        # Test that the class has the required decorated methods
        assert hasattr(WeatherCrew, 'weather_reporter')
        assert hasattr(WeatherCrew, 'report_weather_task')
        assert hasattr(WeatherCrew, 'crew')
