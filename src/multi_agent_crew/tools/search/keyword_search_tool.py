"""Keyword search tool implementation."""

import os
import json
from typing import Type
from pydantic import BaseModel, Field

from ..base.cached_tool import CachedTool
from ...core.exceptions import ToolError
from ...core.config import settings


class KeywordSearchToolInput(BaseModel):
    """Input schema for KeywordSearchTool."""
    keyword: str = Field(..., description="The keyword to search for.")
    target_domain: str = Field(..., description="The domain or company name to look for in results.")


class KeywordSearchTool(CachedTool):
    name: str = "KeywordSearchTool"
    description: str = (
        "A tool that uses GPT-4o-mini to search for a keyword and check if a specific "
        "domain or company name appears in the search results. Returns found/not found status."
    )
    args_schema: Type[BaseModel] = KeywordSearchToolInput

    def _run(self, keyword: str, target_domain: str) -> str:
        """Search for keyword and verify if target domain/company appears."""
        return self._run_with_observability(self._search_keyword, keyword, target_domain)

    def _search_keyword(self, keyword: str, target_domain: str) -> str:
        """Internal method to search keyword."""
        try:
            import openai
            
            # Get API key
            api_key = settings.openrouter_api_key or settings.openai_api_key
            if not api_key:
                raise ToolError("No API key found. Set OPENROUTER_API_KEY or OPENAI_API_KEY.")
            
            # Configure client
            if settings.openrouter_api_key:
                client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                model = "openai/gpt-4o-mini"
            else:
                client = openai.OpenAI(api_key=api_key)
                model = "gpt-4o-mini"
            
            prompt = f"""You are a search engine. When someone searches for "{keyword}", what are the top 5 results?

For each result, provide:
1. The website URL or domain name
2. A brief description (1-2 sentences)

Format your response as a numbered list. Be realistic about what would actually appear in search results for this keyword."""
            
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
            
            # Check if target domain/company appears in results
            target_lower = target_domain.lower()
            results_lower = search_results.lower()
            
            clean_target = target_lower.replace('https://', '').replace('http://', '').replace('www.', '')
            
            found = (
                clean_target in results_lower or
                target_lower in results_lower
            )
            
            return json.dumps({
                "status": "success",
                "keyword": keyword,
                "target": target_domain,
                "found": found,
                "search_results": search_results
            })
            
        except ImportError:
            raise ToolError("OpenAI library not installed.")
        except Exception as e:
            raise ToolError(f"Error searching for keyword: {str(e)}")
