from crewai.tools import BaseTool
from typing import Type, Dict, List, ClassVar, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
import os
import json

logger = logging.getLogger(__name__)


class GSCToolInput(BaseModel):
    """Input schema for GSCTool."""
    domain: str = Field(..., description="The domain to fetch GSC data for (e.g., 'example.com').")
    num_keywords: int = Field(default=10, description="Number of top keywords to fetch (default: 10).")


class GSCTool(BaseTool):
    name: str = "GSCTool"
    description: str = (
        "A tool that connects to Google Search Console and fetches top performing keywords "
        "for a given domain. Returns keywords with clicks, impressions, CTR, and position data."
    )
    args_schema: Type[BaseModel] = GSCToolInput
    
    # Cache storage
    _cache: ClassVar[Dict[str, Tuple[List[Dict], datetime]]] = {}
    _cache_duration: ClassVar[int] = 86400  # 24 hours in seconds

    def _run(self, domain: str, num_keywords: int = 10) -> str:
        """
        Fetch top keywords from Google Search Console.
        
        Args:
            domain: The domain to analyze
            num_keywords: Number of top keywords to return
            
        Returns:
            JSON string with keyword data
        """
        # Normalize domain
        if not domain.startswith('http'):
            domain = f'https://{domain}'
        
        # Check cache
        cache_key = f"{domain}:{num_keywords}"
        if cache_key in GSCTool._cache:
            cached_data, timestamp = GSCTool._cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=GSCTool._cache_duration):
                logger.info(f"Using cached GSC data for {domain}")
                return json.dumps({"status": "success", "data": cached_data, "cached": True})
        
        try:
            logger.info(f"Fetching GSC data for {domain}")
            
            # Import Google API libraries
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
            
            creds = None
            token_path = os.getenv('GSC_TOKEN_PATH', 'token.json')
            credentials_path = os.getenv('GSC_CREDENTIALS_PATH', 'credentials.json')
            
            # Check if token exists
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing GSC credentials")
                    creds.refresh(Request())
                else:
                    if not os.path.exists(credentials_path):
                        error_msg = (
                            f"GSC credentials file not found at {credentials_path}. "
                            "Please create a Google Cloud Project, enable Search Console API, "
                            "and download OAuth2 credentials as 'credentials.json'"
                        )
                        logger.error(error_msg)
                        return json.dumps({"status": "error", "message": error_msg})
                    
                    logger.info("Starting OAuth2 flow for GSC authentication")
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                logger.info(f"GSC credentials saved to {token_path}")
            
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
            
            logger.info(f"Querying GSC for {domain} from {start_date} to {end_date}")
            response = service.searchanalytics().query(siteUrl=domain, body=request).execute()
            
            if 'rows' not in response:
                logger.warning(f"No data found for {domain}")
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
                    'ctr': round(row['ctr'] * 100, 2),  # Convert to percentage
                    'position': round(row['position'], 1)
                })
            
            # Update cache
            GSCTool._cache[cache_key] = (keywords, datetime.now())
            logger.info(f"Successfully fetched {len(keywords)} keywords for {domain}")
            
            return json.dumps({
                "status": "success",
                "data": keywords,
                "cached": False,
                "period": f"{start_date} to {end_date}"
            })
            
        except ImportError as e:
            error_msg = (
                "Google API libraries not installed. "
                "Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )
            logger.error(error_msg)
            return json.dumps({"status": "error", "message": error_msg})
        
        except Exception as e:
            error_msg = f"Error fetching GSC data for {domain}: {str(e)}"
            logger.exception(error_msg)
            return json.dumps({"status": "error", "message": error_msg})
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the GSC data cache."""
        cls._cache.clear()
        logger.info("GSC cache cleared")
