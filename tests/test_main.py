"""Unit tests for the CLI."""

from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from multi_agent_crew.main import app

runner = CliRunner()


@patch('multi_agent_crew.main.SEOCrew')
def test_seo_command(mock_seo_crew):
    """Test the seo command."""
    # Mock crew execution
    mock_instance = MagicMock()
    mock_instance.run.return_value = "SEO Report"
    mock_seo_crew.return_value = mock_instance
    
    result = runner.invoke(app, [
        "seo", 
        "--domain", "example.com", 
        "--company-name", "Example",
        "--num-keywords", "5"
    ])
    
    assert result.exit_code == 0
    assert "Starting SEO Crew for example.com" in result.stdout
    assert "SEO Report" in result.stdout
    mock_seo_crew.assert_called_once()
    mock_instance.run.assert_called_with(inputs={
        "domain": "example.com",
        "company_name": "Example",
        "num_keywords": 5
    })
