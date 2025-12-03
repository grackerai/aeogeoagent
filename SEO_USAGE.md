# SEO Agent - Usage Guide

## Overview

The SEO agent analyzes Google Search Console data and verifies keyword rankings using GPT-4o-mini.

## Setup

### 1. Google Search Console Authentication

#### Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the **Google Search Console API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Search Console API"
   - Click "Enable"

#### Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: "Multi-Agent Crew SEO"
   - Add your email
   - Save and continue through all steps
4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "Multi-Agent Crew"
   - Click "Create"
5. Download the JSON file
6. Rename it to `credentials.json`
7. Place it in the `multi_agent_crew/` directory

### 2. Environment Variables

Update your `.env` file:

```bash
# OpenRouter for LLM (already configured)
OPENROUTER_API_KEY=your_key_here

# OR use OpenAI directly
OPENAI_API_KEY=your_openai_key_here

# GSC credentials (optional, defaults shown)
GSC_CREDENTIALS_PATH=credentials.json
GSC_TOKEN_PATH=token.json
```

### 3. First Run Authentication

On first run, the tool will:
1. Open your browser
2. Ask you to sign in to Google
3. Request permission to access Search Console data
4. Save a token for future use

The token is saved to `token.json` and will be reused for future runs.

---

## Usage

### Run SEO Analysis

The SEO agent will run as part of the crew. You need to provide:
- `domain`: The website domain (e.g., "https://example.com")
- `company_name`: Company name to search for
- `num_keywords`: Number of top keywords to analyze (default: 10)

#### Example: Analyze a Domain

```bash
cd multi_agent_crew/src
../.venv/bin/python3 -m multi_agent_crew.main \
    --mode seo \
    --domain "https://example.com" \
    --company-name "Example Inc" \
    --num-keywords 10
```

### What the SEO Agent Does

1. **Fetch GSC Keywords** (`fetch_gsc_keywords_task`):
   - Connects to Google Search Console
   - Fetches top N keywords by clicks/impressions
   - Returns metrics: clicks, impressions, CTR, position

2. **Verify Rankings** (`verify_keyword_rankings_task`):
   - For each keyword, searches using GPT-4o-mini
   - Checks if your domain/company appears in results
   - Returns found/not found status

### Example Output

```
=== SEO ANALYSIS REPORT ===

Top Keywords from Google Search Console:
1. "best seo tools" - 1,234 clicks, 45,678 impressions, 2.7% CTR, Position 3.2
2. "keyword research api" - 987 clicks, 23,456 impressions, 4.2% CTR, Position 2.1
...

Keyword Ranking Verification:
✓ "best seo tools" - FOUND in search results
✗ "keyword research api" - NOT FOUND in search results
...

Summary:
- Total keywords analyzed: 10
- Found in results: 7 (70%)
- Not found: 3 (30%)

Recommendations:
- Focus on improving content for: "keyword research api", "seo analytics", "search optimization"
```

---

## Advanced Usage

### Option 1: Modify Crew to Run Specific Tasks

```python
# In main.py, add a new function
def run_seo_only():
    """Run only SEO analysis tasks."""
    inputs = {
        'domain': 'https://example.com',
        'company_name': 'Example Inc',
        'num_keywords': 10
    }
    
    crew_instance = SEOCrew()
    
    # Run only SEO tasks
    seo_agent = crew_instance.seo_analyst()
    task1 = crew_instance.fetch_gsc_keywords_task()
    task2 = crew_instance.verify_keyword_rankings_task()
    
    # Create a crew with only SEO tasks
    seo_crew = Crew(
        agents=[seo_agent],
        tasks=[task1, task2],
        process=Process.sequential,
        verbose=True
    )
    
    result = seo_crew.kickoff(inputs=inputs)
    return result
```

### Task Configuration

The SEO crew is designed to run SEO analysis tasks. All tasks are configured in `config/tasks.yaml` and use the SEO analyst agent.

---

## Troubleshooting

### "credentials.json not found"

**Solution**: Download OAuth2 credentials from Google Cloud Console and place in project root.

### "No data found for this domain"

**Possible causes**:
1. Domain not verified in Google Search Console
2. No data in last 30 days
3. Wrong domain format (try with/without https://)

**Solution**: 
- Verify domain ownership in [Google Search Console](https://search.google.com/search-console)
- Ensure domain format matches exactly (e.g., "https://example.com" vs "https://www.example.com")

### "API key not found"

**Solution**: Set `OPENAI_API_KEY` or `OPENROUTER_API_KEY` in `.env` file.

### "Rate limit exceeded"

**Solution**: GSC API has rate limits. The tool caches results for 24 hours. If you hit limits, wait a few minutes and try again.

---

## Advanced Configuration

### Change Cache Duration

Edit `gsc_tool.py`:

```python
_cache_duration: ClassVar[int] = 86400  # 24 hours (change this)
```

### Use Different LLM Model

Edit `keyword_search_tool.py`:

```python
model = "openai/gpt-4o"  # Use GPT-4 instead of GPT-4o-mini
```

Or update `agents.yaml`:

```yaml
seo_analyst:
  llm: openrouter/anthropic/claude-3.5-sonnet
```

### Analyze More Keywords

```bash
python -m multi_agent_crew.main \
    --mode seo \
    --domain "https://example.com" \
    --company-name "Example Inc" \
    --num-keywords 50  # Analyze top 50 keywords
```

---

## API Costs

### Google Search Console API
- **Free**: 1,200 queries per minute
- **Cost**: $0

### OpenAI GPT-4o-mini
- **Cost**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **Typical usage**: ~$0.01-0.05 per 10 keywords

### OpenRouter
- **Cost**: Varies by model
- **GPT-4o-mini**: Similar to OpenAI pricing
- **Gemini 2.0 Flash**: Free tier available

---

## Next Steps

1. **Add More SEO Metrics**: Extend GSCTool to fetch page-level data
2. **Competitor Analysis**: Add tool to compare with competitor rankings
3. **Historical Trends**: Track keyword performance over time
4. **Automated Reports**: Schedule daily/weekly SEO reports
5. **Integration**: Connect with other SEO tools (Ahrefs, SEMrush)
