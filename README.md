# Multi-Agent Crew - CrewAI System

A production-ready multi-agent system built with CrewAI featuring specialized agents for weather reporting and SEO analysis.

## 🌟 Features

- **Weather Reporter Agent**: Fetches real-time weather data for any location
- **SEO Analyst Agent**: Analyzes Google Search Console data and verifies keyword rankings
- **Reusable Tools**: Modular tools that can be used by any agent
- **Production-Ready**: Logging, caching, error handling, and comprehensive tests

## 📁 Project Structure

```
multi_agent_crew/
├── .env                          # Environment variables (API keys)
├── pyproject.toml                # Project dependencies
├── src/
│   └── multi_agent_crew/
│       ├── main.py               # Entry point
│       ├── crew.py               # Crew configuration
│       ├── tools/
│       │   ├── weather_tool.py   # Weather data fetching
│       │   ├── gsc_tool.py       # Google Search Console integration
│       │   └── keyword_search_tool.py  # Keyword verification
│       └── config/
│           ├── agents.yaml       # Agent definitions
│           └── tasks.yaml        # Task definitions
├── tests/                        # Unit tests
└── SEO_USAGE.md                  # SEO agent usage guide
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd multi_agent_crew
crewai install
```

### 2. Configure API Keys

Create/update `.env` file:

```bash
# Required for LLM
OPENROUTER_API_KEY=your_openrouter_key_here

# OR use OpenAI directly
OPENAI_API_KEY=your_openai_key_here

# Optional: For SEO agent
GSC_CREDENTIALS_PATH=credentials.json
GSC_TOKEN_PATH=token.json
```

### 3. Run the Crew

#### Weather Analysis
```bash
cd src
../.venv/bin/python3 -m multi_agent_crew.main --location "London"
```

#### SEO Analysis
For SEO analysis, you'll need to set up Google Search Console credentials first. See [SEO_USAGE.md](SEO_USAGE.md) for detailed setup instructions.

## 🤖 Agents

### 1. Weather Reporter
- **Role**: Weather Reporter
- **Tools**: WeatherTool
- **Capabilities**: Fetches current temperature and conditions for any location
- **Data Source**: wttr.in (no API key required)

### 2. SEO Analyst
- **Role**: SEO Analyst
- **Tools**: GSCTool, KeywordSearchTool
- **Capabilities**: 
  - Fetches top keywords from Google Search Console
  - Verifies keyword rankings using GPT-4o-mini
  - Provides visibility analysis and recommendations
- **Data Sources**: Google Search Console API, OpenAI/OpenRouter

## 🛠️ Tools

### WeatherTool
Fetches weather data from wttr.in with 5-minute caching.

### GSCTool
Connects to Google Search Console via OAuth2 and fetches keyword performance data with 24-hour caching.

### KeywordSearchTool
Uses GPT-4o-mini to simulate search results and verify if a domain appears for specific keywords.

## 📊 Example Output

### Weather Report
```
=== WEATHER REPORT ===

Good morning, London! The current temperature in London is 9°C.
```

### SEO Analysis
```
=== SEO ANALYSIS REPORT ===

Top Keywords from Google Search Console:
1. "best weather app" - 1,234 clicks, 2.7% CTR, Position 3.2
2. "weather forecast api" - 987 clicks, 4.2% CTR, Position 2.1

Keyword Ranking Verification:
✓ "best weather app" - FOUND
✗ "weather forecast api" - NOT FOUND

Visibility: 70% (7/10 keywords found)
```

## 🧪 Testing

Run unit tests:

```bash
.venv/bin/pytest tests/ -v
```

Run with coverage:

```bash
.venv/bin/pytest tests/ --cov=src/multi_agent_crew --cov-report=html
```

## 📚 Documentation

- **SEO Setup**: [SEO_USAGE.md](SEO_USAGE.md)
- **Observability**: See artifacts for integration guides
- **API Documentation**: Check individual tool files for detailed docstrings

## 🔧 Customization

### Add New Agent

1. Define agent in `src/multi_agent_crew/config/agents.yaml`
2. Create tasks in `src/multi_agent_crew/config/tasks.yaml`
3. Register in `src/multi_agent_crew/crew.py`

### Create Custom Tool

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param: str = Field(..., description="Parameter description")

class MyTool(BaseTool):
    name: str = "MyTool"
    description: str = "Tool description"
    args_schema: Type[BaseModel] = MyToolInput
    
    def _run(self, param: str) -> str:
        # Your logic here
        return result
```

## 🌐 API Costs

- **wttr.in**: Free
- **Google Search Console API**: Free (1,200 queries/min)
- **OpenRouter/OpenAI**: ~$0.01-0.05 per 10 keywords (GPT-4o-mini)

## 🏆 Features

✅ Production-ready code quality  
✅ Comprehensive error handling  
✅ Logging (console + file)  
✅ Caching for performance  
✅ Type hints throughout  
✅ Unit tests  
✅ CLI arguments  
✅ OAuth2 authentication  
✅ Multi-agent coordination  

## 📝 License

MIT

## 🤝 Contributing

This is a reference implementation for CrewAI multi-agent systems. Feel free to extend and customize for your needs!
