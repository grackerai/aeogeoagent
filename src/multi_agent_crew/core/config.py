"""Configuration management using Pydantic."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Observability
    observability_backend: str = Field("system", description="Observability backend (system, prometheus, grafana)")
    prometheus_port: int = Field(8000, description="Port for Prometheus metrics")
    log_level: str = Field("INFO", description="Logging level")
    
    # LLM Configuration
    openrouter_api_key: Optional[str] = Field(None, description="OpenRouter API Key")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API Key")
    default_llm_model: str = Field("openrouter/google/gemini-2.5-flash-lite", description="Default LLM model")
    
    # Google Search Console
    gsc_credentials_path: str = Field("credentials.json", description="Path to GSC credentials")
    gsc_token_path: str = Field("token.json", description="Path to GSC token")
    
    # Caching
    enable_caching: bool = Field(True, description="Enable tool caching")
    cache_ttl_seconds: int = Field(300, description="Default cache TTL in seconds")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Global settings instance
settings = Settings()
