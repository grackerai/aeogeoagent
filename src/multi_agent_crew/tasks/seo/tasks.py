"""SEO tasks definition."""

from crewai import Task
from ...agents.seo_agent import SEOAgent
from ...core.config import settings


class SEOTasks:
    """Tasks for SEO analysis."""
    
    def fetch_keywords(self, agent, domain: str, num_keywords: int) -> Task:
        """Task to fetch keywords from GSC."""
        return Task(
            description=f"""
                Connect to Google Search Console for the domain {domain} and fetch the top {num_keywords} keywords
                by clicks and impressions from the last 30 days. Use the GSCTool to retrieve this data.
                Present the keywords with their performance metrics in a clear, organized format.
            """,
            expected_output=f"""
                A structured list of the top {num_keywords} keywords with their metrics including:
                keyword name, clicks, impressions, CTR (%), and average position.
                If no data is available, explain why.
            """,
            agent=agent
        )
    
    def verify_rankings(self, agent, domain: str, company_name: str, context_tasks: list = None) -> Task:
        """Task to verify keyword rankings."""
        return Task(
            description=f"""
                For each keyword retrieved from Google Search Console, use the KeywordSearchTool to search
                for that keyword and verify if {domain} or {company_name} appears in the search results.
                Use GPT-4o-mini to simulate search results and check for presence.
                Provide a clear found/not found status for each keyword.
            """,
            expected_output=f"""
                A comprehensive report showing:
                1. Each keyword from GSC
                2. Whether {domain} or {company_name} was found in search results (✓ Found / ✗ Not Found)
                3. A summary with total keywords analyzed and visibility percentage
                4. Recommendations for keywords where the domain was not found
            """,
            agent=agent,
            context=context_tasks or []
        )
