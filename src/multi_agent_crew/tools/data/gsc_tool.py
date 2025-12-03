"""Google Search Console tool implementation."""

import os
import json
from typing import Type, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from ..base.cached_tool import CachedTool
from ...core.exceptions import ToolError
from ...core.config import settings


class GSCToolInput(BaseModel):
    """Input schema for GSCTool."""
    domain: str = Field(..., description="The domain to fetch GSC data for (e.g., 'example.com').")
    num_keywords: int = Field(default=10, description="Number of top keywords to fetch (default: 10).")


class GSCTool(CachedTool):
    name: str = "GSCTool"
    description: str = (
        "A tool that connects to Google Search Console and fetches top performing keywords "
        "for a given domain. Returns keywords with clicks, impressions, CTR, and position data."
    )
    args_schema: Type[BaseModel] = GSCToolInput
    
    # Override cache duration for GSC (24 hours)
    _cache_duration = 86400

    def _run(self, domain: str, num_keywords: int = 10) -> str:
        """Fetch top keywords from Google Search Console."""
        return self._run_with_observability(self._fetch_gsc_data, domain, num_keywords)

    def _fetch_gsc_data(self, domain: str, num_keywords: int) -> str:
        """Internal method to fetch GSC data."""
        # Normalize domain
        if not domain.startswith('http'):
            domain = f'https://{domain}'
        
        # Check cache
        cache_key = f"gsc:{domain}:{num_keywords}"
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
            
            # Fetch data for last 30 days
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query'],
                'rowLimit': num_keywords,
                'aggregationType': 'auto'
            }
            
            response = service.searchanalytics().query(siteUrl=domain, body=request).execute()
            
            if 'rows' not in response:
                return json.dumps({
                    "status": "success",
                    "data": [],
                    "message": "No keyword data found for this domain in the last 30 days"
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
            
            # Update cache
            self._save_to_cache(cache_key, keywords)
            
            return json.dumps({
                "status": "success",
                "data": keywords,
                "cached": False,
                "period": f"{start_date} to {end_date}"
            })
            
        except ImportError:
            raise ToolError("Google API libraries not installed.")
        except Exception as e:
            raise ToolError(f"Error fetching GSC data: {str(e)}")
