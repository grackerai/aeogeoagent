# Architecture Documentation

## Overview

The Multi-Agent Crew system is designed with a scalable, modular architecture that supports:
- **Pluggable Observability**: Support for multiple backends (Prometheus, Grafana, System Logs)
- **Modular Components**: Independent agents, tools, and crews
- **Configuration Management**: Centralized configuration using Pydantic
- **Robust Error Handling**: Custom exceptions and graceful degradation

---

## Core Components

### 1. Observability Layer (`core/observability/`)

The observability layer uses the **Adapter Pattern** to support multiple backends.

- **Interface**: `ObservabilityBackend` (abstract base class)
- **Adapters**:
  - `SystemLoggerBackend`: Default fallback using Python logging
  - `PrometheusBackend`: Exposes metrics for Prometheus scraping
  - `GrafanaBackend`: (Planned) Direct integration with Grafana Cloud
- **Factory**: `ObservabilityFactory` creates the appropriate backend based on configuration with automatic fallback.

### 2. Configuration (`core/config.py`)

Configuration is managed using `pydantic-settings`, allowing configuration via:
1. Environment variables (`.env` file)
2. Default values in code

### 3. Base Classes

- **BaseAgent**: Handles observability initialization and agent creation.
- **CachedTool**: Provides built-in caching (TTL-based) and observability instrumentation for all tools.
- **BaseCrew**: Standardizes crew creation and execution with tracing.

---

## Directory Structure

```
multi_agent_crew/
├── src/multi_agent_crew/
│   ├── agents/           # Agent definitions (Factory pattern)
│   ├── crews/            # Crew definitions
│   ├── tasks/            # Task definitions by domain
│   ├── tools/            # Shared tools
│   │   ├── base/         # Base tool classes
│   │   ├── data/         # Data fetching tools
│   │   └── search/       # Search tools
│   ├── core/             # Core infrastructure
│   │   ├── observability/# Pluggable observability
│   │   ├── config.py     # Configuration
│   │   └── exceptions.py # Custom exceptions
│   └── main.py           # CLI entry point
```

---

## Adding New Components

### Adding a New Agent

1. Create a new class inheriting from `BaseAgent` in `src/multi_agent_crew/agents/`.
2. Implement the `create()` method.
3. Register the agent in `AgentFactory`.

### Adding a New Tool

1. Create a new class inheriting from `CachedTool` in `src/multi_agent_crew/tools/`.
2. Implement the `_run()` method.
3. Use `self._run_with_observability()` wrapper.

### Adding a New Crew

1. Create a new class inheriting from `BaseCrew` in `src/multi_agent_crew/crews/`.
2. Implement the `create()` method using `AgentFactory` and Task classes.

---

## Design Principles

1. **Fail-Safe Defaults**: The system should run with minimal configuration.
   - Default observability: System Logs
   - Default LLM: OpenRouter (free tier)
   - Default Storage: In-memory

2. **Graceful Degradation**: If a component fails (e.g., Prometheus), the system falls back to a working alternative (System Logs) without crashing.

3. **Separation of Concerns**: Agents, Tools, and Tasks are decoupled to allow independent evolution.
