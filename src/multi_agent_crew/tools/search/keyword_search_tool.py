"""Keyword search tool implementation with multi-model parallel search."""

import os
import json
import asyncio
from typing import Type, List, Dict, ClassVar
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
        "A tool that uses multiple AI models in parallel to search for a keyword and check if a specific "
        "domain or company name appears in the search results. Returns aggregated results from all models."
    )
    args_schema: Type[BaseModel] = KeywordSearchToolInput
    
    # Models to search with in parallel
    SEARCH_MODELS: ClassVar[List[str]] = [
        "openai/gpt-4o-mini",
        "google/gemini-2.5-flash-lite",
        "x-ai/grok-beta",
        "deepseek/deepseek-chat"
    ]

    def _run(self, keyword: str, target_domain: str) -> str:
        """Search for keyword and verify if target domain/company appears."""
        return self._run_with_observability(self._search_keyword, keyword, target_domain)

    async def _search_single_model(self, client, model: str, keyword: str, target_domain: str) -> Dict:
        """Search with a single model asynchronously."""
        try:
            prompt = f"""You are a search engine. When someone searches for "{keyword}", what are the top 5 results?

For each result, provide:
1. The website URL or domain name
2. A brief description (1-2 sentences)

Format your response as a numbered list. Be realistic about what would actually appear in search results for this keyword."""
            
            response = await asyncio.to_thread(
                client.chat.completions.create,
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
            
            return {
                "model": model,
                "found": found,
                "search_results": search_results
            }
            
        except Exception as model_error:
            return {
                "model": model,
                "found": False,
                "error": str(model_error)
            }

    def _search_keyword(self, keyword: str, target_domain: str) -> str:
        """Internal method to search keyword using multiple models in parallel."""
        try:
            import openai
            
            # Get API key
            api_key = settings.openrouter_api_key or settings.openai_api_key
            if not api_key:
                raise ToolError("No API key found. Set OPENROUTER_API_KEY or OPENAI_API_KEY.")
            
            # Use OpenRouter for multi-model access
            if settings.openrouter_api_key:
                client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                models = self.SEARCH_MODELS
            else:
                # Fallback to OpenAI only
                client = openai.OpenAI(api_key=api_key)
                models = ["gpt-4o-mini"]
            
            # Run all model searches in parallel using asyncio
            async def search_all_models():
                tasks = [
                    self._search_single_model(client, model, keyword, target_domain)
                    for model in models
                ]
                return await asyncio.gather(*tasks)
            
            # Execute parallel searches
            results = asyncio.run(search_all_models())
            
            # Aggregate results
            total_models = len(results)
            found_count = sum(1 for r in results if r.get("found", False))
            consensus = found_count > (total_models / 2)  # Majority vote
            
            return json.dumps({
                "status": "success",
                "keyword": keyword,
                "target": target_domain,
                "consensus_found": consensus,
                "found_in_models": found_count,
                "total_models": total_models,
                "model_results": results
            }, indent=2)
            
        except ImportError:
            raise ToolError("OpenAI library not installed.")
        except Exception as e:
            raise ToolError(f"Error searching for keyword: {str(e)}")
