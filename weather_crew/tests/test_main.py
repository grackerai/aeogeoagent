"""Unit tests for main module."""

import pytest
from unittest.mock import patch, Mock
from multi_agent_crew.main import run


class TestMain:
    """Test suite for main module."""
    
    @patch('multi_agent_crew.main.WeatherCrew')
    @patch('sys.argv', ['multi_agent_crew', '--location', 'Tokyo'])
    def test_run_with_custom_location(self, mock_crew_class):
        """Test running crew with custom location."""
        # Mock crew and result
        mock_crew_instance = Mock()
        mock_result = Mock()
        mock_result.raw = "Tokyo: ☁️  +20°C"
        mock_crew_instance.crew().kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        result = run()
        
        assert result == "Tokyo: ☁️  +20°C"
        mock_crew_instance.crew().kickoff.assert_called_once()
        
        # Check that Tokyo was passed as input
        call_args = mock_crew_instance.crew().kickoff.call_args
        assert call_args[1]['inputs']['location'] == 'Tokyo'
    
    @patch('multi_agent_crew.main.WeatherCrew')
    @patch('sys.argv', ['multi_agent_crew'])
    def test_run_with_default_location(self, mock_crew_class):
        """Test running crew with default location (London)."""
        # Mock crew and result
        mock_crew_instance = Mock()
        mock_result = Mock()
        mock_result.raw = "London: 🌧  +10°C"
        mock_crew_instance.crew().kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        result = run()
        
        assert result == "London: 🌧  +10°C"
        
        # Check that London was passed as input (default)
        call_args = mock_crew_instance.crew().kickoff.call_args
        assert call_args[1]['inputs']['location'] == 'London'
