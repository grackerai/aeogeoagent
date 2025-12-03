from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import logging
import json
import os

logger = logging.getLogger(__name__)


class KeywordSearchToolInput(BaseModel):
    """Input schema for KeywordSearchTool."""
    keyword: str = Field(..., description="The keyword to search for.")
    target_domain: str = Field(..., description="The domain or company name to look for in results.")


class KeywordSearchTool(BaseTool):
    name: str = "KeywordSearchTool"
    description: str = (
        "A tool that uses GPT-4o-mini to search for a keyword and check if a specific "
        "domain or company name appears in the search results. Returns found/not found status."
    )
    args_schema: Type[BaseModel] = KeywordSearchToolInput

    def _run(self, keyword: str, target_domain: str) -> str:
        """
        Search for keyword and verify if target domain/company appears.
        
        Args:
            keyword: The keyword to search for
            target_domain: The domain or company name to look for
            
        Returns:
            JSON string with search results
        """
        try:
            logger.info(f"Searching for keyword '{keyword}' to find '{target_domain}'")
            
            # Import OpenAI
            try:
                import openai
            except ImportError:
                error_msg = "OpenAI library not installed. Run: pip install openai"
                logger.error(error_msg)
                return json.dumps({"status": "error", "message": error_msg})
            
            # Get API key
            api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                error_msg = "No API key found. Set OPENAI_API_KEY or OPENROUTER_API_KEY environment variable"
                logger.error(error_msg)
                return json.dumps({"status": "error", "message": error_msg})
            
            # Configure client
            if os.getenv('OPENROUTER_API_KEY'):
                # Use OpenRouter
                client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                model = "openai/gpt-4o-mini"
            else:
                # Use OpenAI directly
                client = openai.OpenAI(api_key=api_key)
                model = "gpt-4o-mini"
            
            # Create search prompt
            prompt = f"""You are a search engine. When someone searches for "{keyword}", what are the top 5 results?

For each result, provide:
1. The website URL or domain name
2. A brief description (1-2 sentences)

Format your response as a numbered list. Be realistic about what would actually appear in search results for this keyword."""
            
            logger.info(f"Querying {model} for keyword: {keyword}")
            
            # Call API
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful search engine that provides realistic search results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            search_results = response.choices[0].message.content
            logger.info(f"Received search results for '{keyword}'")
            
            # Check if target domain/company appears in results
            target_lower = target_domain.lower()
            results_lower = search_results.lower()
            
            # Clean domain for matching (remove http/https/www)
            clean_target = target_lower.replace('https://', '').replace('http://', '').replace('www.', '')
            
            found = (
                clean_target in results_lower or
                target_lower in results_lower
            )
            
            result_data = {
                "status": "success",
                "keyword": keyword,
                "target": target_domain,
                "found": found,
                "search_results": search_results
            }
            
            if found:
                logger.info(f"✓ Found '{target_domain}' in results for '{keyword}'")
            else:
                logger.info(f"✗ '{target_domain}' NOT found in results for '{keyword}'")
            
            return json.dumps(result_data)
            
        except Exception as e:
            error_msg = f"Error searching for keyword '{keyword}': {str(e)}"
            logger.exception(error_msg)
            return json.dumps({
                "status": "error",
                "keyword": keyword,
                "message": error_msg
            })
