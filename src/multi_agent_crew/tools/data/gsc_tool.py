"""Google Search Console tool implementation."""

import os
import json
import logging
from typing import Type, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from ..base.cached_tool import CachedTool
from ...core.exceptions import ToolError
from ...core.config import settings

logger = logging.getLogger(__name__)


class GSCToolInput(BaseModel):
    """Input schema for GSCTool."""
    domain: str = Field(..., description="The domain to fetch GSC data for (e.g., 'example.com').")
    num_keywords: int = Field(default=10, description="Number of top keywords to fetch (default: 10).")
    date_range: int = Field(default=30, description="Number of days to look back (default: 30).")
    sort_by: str = Field(default="clicks", description="Sort by: 'clicks', 'impressions', 'ctr', or 'position' (default: 'clicks').")


class GSCTool(CachedTool):
    name: str = "GSCTool"
    description: str = (
        "A tool that connects to Google Search Console and fetches top performing keywords "
        "for a given domain. Returns keywords with clicks, impressions, CTR, and position data."
    )
    args_schema: Type[BaseModel] = GSCToolInput
    
    # Override cache duration for GSC (24 hours)
    _cache_duration = 86400

    def _run(self, domain: str, num_keywords: int = 10, date_range: int = 30, sort_by: str = "clicks") -> str:
        """Fetch top keywords from Google Search Console."""
        return self._run_with_observability(self._fetch_gsc_data, domain, num_keywords, date_range, sort_by)

    def _fetch_gsc_data(self, domain: str, num_keywords: int, date_range: int, sort_by: str) -> str:
        """Internal method to fetch GSC data."""
        # Check cache first
        cache_key = f"gsc:{domain}:{num_keywords}:{date_range}:{sort_by}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return json.dumps({"status": "success", "data": cached, "cached": True})
        
        try:
            # Import Google API libraries locally to avoid import errors if not installed
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
            
            creds = None
            token_path = settings.gsc_token_path
            credentials_path = settings.gsc_credentials_path
            
            # Check if token exists
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(credentials_path):
                        raise ToolError(
                            f"GSC credentials file not found at {credentials_path}. "
                            "Please create a Google Cloud Project and download credentials."
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            # Build service
            service = build('searchconsole', 'v1', credentials=creds)
            
            # List all available properties
            try:
                sites_list = service.sites().list().execute()
                logger.info(f"Available GSC properties: {json.dumps(sites_list, indent=2)}")
                available_sites = [site['siteUrl'] for site in sites_list.get('siteEntry', [])]
                logger.info(f"Available site URLs: {available_sites}")
            except Exception as e:
                logger.warning(f"Could not list sites: {e}")
                available_sites = []
            
            # Try to find the correct domain format
            base_domain = domain.replace("https://", "").replace("http://", "").replace("sc-domain:", "")
            possible_formats = [
                domain,  # Use as-is first
                f"https://{base_domain}",
                f"http://{base_domain}",
                f"sc-domain:{base_domain}",
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_formats = []
            for fmt in possible_formats:
                if fmt not in seen:
                    seen.add(fmt)
                    unique_formats.append(fmt)
            
            # If we have available sites, prioritize exact matches first
            if available_sites:
                # Separate exact matches from partial matches
                exact_matches = []
                partial_matches = []
                
                for site in available_sites:
                    # Extract the domain from the site URL
                    site_domain = site.replace("https://", "").replace("http://", "").replace("sc-domain:", "").rstrip("/")
                    
                    # Exact match: the domains are identical
                    if site_domain == base_domain:
                        exact_matches.append(site)
                    # Partial match: site contains the base domain (e.g., tools.psywellpath.com contains psywellpath.com)
                    elif base_domain in site:
                        partial_matches.append(site)
                
                # Prioritize exact matches, then user-provided formats, then partial matches
                unique_formats = exact_matches + unique_formats + partial_matches
                
                # Remove duplicates again
                seen = set()
                deduplicated = []
                for fmt in unique_formats:
                    if fmt not in seen:
                        seen.add(fmt)
                        deduplicated.append(fmt)
                unique_formats = deduplicated
            
            logger.info(f"Trying domain formats in order: {unique_formats}")
            
            # Fetch data for configurable date range
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=date_range)).strftime('%Y-%m-%d')
            
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query'],
                'rowLimit': num_keywords,
                'aggregationType': 'auto'
            }
            
            # Try each format until one works
            response = None
            successful_domain = None
            last_error = None
            
            for domain_format in unique_formats:
                try:
                    logger.info(f"Attempting GSC API call with domain format: {domain_format}")
                    logger.info(f"Request body: {json.dumps(request_body, indent=2)}")
                    
                    response = service.searchanalytics().query(siteUrl=domain_format, body=request_body).execute()
                    
                    # logger.info(f"GSC API Response for {domain_format}: {json.dumps(response, indent=2)}")
                    
                    # Check if we got rows
                    if 'rows' in response and len(response['rows']) > 0:
                        successful_domain = domain_format
                        logger.info(f"✓ Successfully fetched {len(response['rows'])} keywords from {domain_format}")
                        break
                    else:
                        logger.info(f"No rows returned for {domain_format}, trying next format...")
                        
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Failed to fetch from {domain_format}: {e}")
                    continue
            
            # If no format worked, return empty result
            if not response or 'rows' not in response:
                logger.warning(f"No data found for any domain format. Last error: {last_error}")
                return json.dumps({
                    "status": "success",
                    "data": [],
                    "message": f"No keyword data found for {domain} in the last {date_range} days",
                    "debug_info": {
                        "tried_formats": unique_formats,
                        "available_properties": available_sites,
                        "last_error": last_error
                    }
                })
            
            # Format results
            keywords = []
            for row in response['rows']:
                keywords.append({
                    'keyword': row['keys'][0],
                    'clicks': row['clicks'],
                    'impressions': row['impressions'],
                    'ctr': round(row['ctr'] * 100, 2),
                    'position': round(row['position'], 1)
                })
            
            # Sort by clicks (descending), then by impressions (descending) as tiebreaker
            keywords.sort(key=lambda x: (-x['clicks'], -x['impressions']))
            
            logger.info(f"✓ Formatted and sorted {len(keywords)} keywords from {successful_domain}")
            
            # Update cache
            self._save_to_cache(cache_key, keywords)
            
            return json.dumps({
                "status": "success",
                "data": keywords,
                "cached": False,
                "period": f"{start_date} to {end_date}",
                "source_property": successful_domain
            })
            
        except ImportError:
            raise ToolError("Google API libraries not installed.")
        except Exception as e:
            raise ToolError(f"Error fetching GSC data: {str(e)}")
