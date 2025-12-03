"""SEO tasks definition."""

from crewai import Task
from ...agents.seo_agent import SEOAgent
from ...core.config import settings


class SEOTasks:
    """Tasks for SEO analysis."""
    
    def fetch_keywords(self, agent, domain: str, num_keywords: int, date_range: int = 30, sort_by: str = "clicks") -> Task:
        """Task to fetch keywords from GSC."""
        return Task(
            description=f"""
                Connect to Google Search Console for the domain {domain} and fetch the top {num_keywords} keywords
                sorted by {sort_by} from the last {date_range} days. Use the GSCTool to retrieve this data.
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
                For each keyword retrieved from Google Search Console, use the KeywordSearchTool to verify 
                if {domain} or {company_name} appears in search results.
                
                The KeywordSearchTool uses 4 AI models in parallel (OpenAI, Gemini, Grok, DeepSeek).
                For EACH keyword, you MUST show the results from ALL 4 models.
            """,
            expected_output=f"""
                Create a markdown table report with the following structure:
                
                ## Keyword Ranking Verification Report
                
                | Keyword | OpenAI | Gemini | Grok | DeepSeek | Consensus | Vote |
                |---------|--------|--------|------|----------|-----------|------|
                | keyword1 | ✓ | ✗ | ✓ | ✓ | Found | 3/4 |
                | keyword2 | ✗ | ✗ | ✗ | ✗ | Not Found | 0/4 |
                
                ### Summary
                - Total Keywords: X
                - Found: Y (Z%)
                - Not Found: W
                
                ### Recommendations
                List specific actions for keywords not found.
            """,
            agent=agent,
            context=context_tasks or []
        )
