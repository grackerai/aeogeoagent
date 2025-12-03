"""Main entry point for the multi-agent crew CLI."""

import sys
import logging
from typing import Optional
import typer
from rich.console import Console
from rich.logging import RichHandler

from .crews import SEOCrew
from .core.observability import get_observability, ObservabilityFactory
from .core.config import settings

# Configure rich logging
logging.basicConfig(
    level=settings.log_level,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

app = typer.Typer(
    name="multi_agent_crew",
    help="Multi-Agent Crew CLI for SEO Analysis",
    add_completion=False,
)
console = Console()


def setup_observability():
    """Initialize observability system."""
    ObservabilityFactory.create(
        backend=settings.observability_backend,
        port=settings.prometheus_port
    )


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """
    Multi-Agent Crew CLI.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    setup_observability()


@app.command()
def seo(
    domain: str = typer.Option(..., "--domain", "-d", help="Domain to analyze"),
    company_name: str = typer.Option(..., "--company-name", "-c", help="Company name to verify"),
    num_keywords: int = typer.Option(10, "--num-keywords", "-n", help="Number of keywords to fetch (default: 10)"),
    date_range: int = typer.Option(30, "--date-range", "-r", help="Days to look back (default: 30)"),
    sort_by: str = typer.Option("clicks", "--sort-by", "-s", help="Sort by: clicks, impressions, ctr, position (default: clicks)"),
):
    """
    Run the SEO Crew to analyze keywords and rankings.
    """
    console.print(f"[bold blue]Starting SEO Crew for {domain}...[/bold blue]")
    
    try:
        crew = SEOCrew()
        result = crew.run(inputs={
            "domain": domain,
            "company_name": company_name,
            "num_keywords": num_keywords,
            "date_range": date_range,
            "sort_by": sort_by
        })
        console.print(f"\n[bold green]Result:[/bold green]\n{result}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command()
def list_agents():
    """List available agents."""
    from .agents.factory import AgentFactory
    
    console.print("[bold]Available Agents:[/bold]")
    for agent_type in AgentFactory._agents:
        console.print(f"  - {agent_type}")


def run():
    """Entry point for the package."""
    app()


if __name__ == "__main__":
    app()
