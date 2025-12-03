# CrewAI Weather Agent - README

A multi-agent system built with CrewAI that fetches weather information for any location using a custom weather tool.

## 🌟 Features

- **Custom Weather Tool**: Reusable tool that fetches weather data from wttr.in (no API key required)
- **Weather Reporter Agent**: Expert meteorologist agent that provides friendly weather reports
- **OpenRouter Integration**: Uses OpenRouter for flexible LLM provider selection
- **Standard CrewAI Structure**: Follows best practices and latest CrewAI standards

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
│       │   └── weather_tool.py   # Custom weather tool
│       └── config/
│           ├── agents.yaml       # Agent definitions
│           └── tasks.yaml        # Task definitions
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd multi_agent_crew
crewai install
```

### 2. Configure API Key

Add your OpenRouter API key to `.env`:

```bash
OPENROUTER_API_KEY=your_key_here
```

### 3. Run the Crew

```bash
crewai run
```

## 🎯 Example Output

```
=== WEATHER REPORT ===

Good morning, London! The current temperature in London is 9°C.
```

## 🔧 Customization

### Change Location

Edit `src/multi_agent_crew/main.py` line 13:

```python
inputs = {
    'location': 'New York'  # Change to any city
}
```

### Change LLM Model

Edit `src/multi_agent_crew/config/agents.yaml`:

```yaml
weather_reporter:
  llm: openrouter/anthropic/claude-3.5-sonnet  # Use different model
```

### Add More Agents

1. Define new agent in `config/agents.yaml`
2. Create corresponding task in `config/tasks.yaml`
3. Register in `crew.py`

## 🛠️ Components

### WeatherTool

A reusable tool that:
- Fetches weather data from wttr.in
- Requires no API key
- Returns temperature and conditions
- Can be used by any agent

### Weather Reporter Agent

- **Role**: Weather Reporter
- **Goal**: Provide accurate temperature information
- **Tools**: WeatherTool
- **LLM**: OpenRouter (Gemini 2.0 Flash)

### Report Weather Task

- Fetches current temperature for specified location
- Uses WeatherTool
- Outputs friendly, concise report

## 📚 Learn More

- [CrewAI Documentation](https://docs.crewai.com)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [wttr.in API](https://github.com/chubin/wttr.in)

## 🔮 Future Enhancements

- [ ] Multi-location support
- [ ] Weather forecasting agent
- [ ] Historical weather data
- [ ] Weather alerts and warnings
- [ ] Hierarchical crew structure
- [ ] Caching for API calls

## ✅ Verified

This project has been tested and verified to work with:
- CrewAI 1.6.1
- OpenRouter API
- Python 3.13
- wttr.in weather service
