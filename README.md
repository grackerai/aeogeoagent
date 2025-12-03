# Multi-Agent Crew System

A production-ready, scalable multi-agent system built with CrewAI, featuring specialized agents for weather reporting and SEO analysis.

## 🌟 Features

- **Scalable Architecture**: Modular design supporting 10+ agents
- **Pluggable Observability**: Prometheus, Grafana, or System Logs
- **Robust Tooling**: Caching, error handling, and metrics built-in
- **Type-Safe Configuration**: Pydantic-based settings management
- **CLI Interface**: Easy-to-use command line interface

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Configure Environment

Create a `.env` file:

```bash
# LLM Configuration
OPENROUTER_API_KEY=your_key_here

# Observability (Optional)
OBSERVABILITY_BACKEND=system  # or prometheus
PROMETHEUS_PORT=8000
```

### 3. Run the CLI

```bash
# Get Weather
multi_agent_crew weather --location "London"

# Analyze SEO
multi_agent_crew seo --domain "example.com" --company-name "Example Inc"
```

## 🏗️ Architecture

The system follows a modular architecture designed for scalability:

- **Agents**: Specialized workers (Weather, SEO) created via Factory
- **Tools**: Reusable capabilities with built-in caching
- **Crews**: Composable workflows
- **Observability**: Pluggable backends (Prometheus, Logs)

See [docs/architecture.md](docs/architecture.md) for details.

## 📊 Observability

The system supports multiple observability backends:

1. **System Logs** (Default): Standard Python logging
2. **Prometheus**: Exposes metrics at `http://localhost:8000`

To enable Prometheus:
1. Set `OBSERVABILITY_BACKEND=prometheus` in `.env`
2. Install `prometheus-client` (included in dependencies)

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## 📝 License

MIT
