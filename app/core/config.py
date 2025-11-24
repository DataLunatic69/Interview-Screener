"""
Application configuration using Pydantic Settings.
Loads from environment variables with validation.
"""
from functools import lru_cache
from typing import List
import os
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    api_title: str = Field(default="AI Interview Screener", alias="API_TITLE")
    api_version: str = Field(default="1.0.0", alias="API_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # CORS Settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "http://localhost:8001"],
        alias="CORS_ORIGINS"
    )
    
    # Groq API Configuration
    groq_api_key: str = Field(default=os.getenv("GROQ_API_KEY", ""), alias="GROQ_API_KEY")
    llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        alias="LLM_MODEL"
    )
    llm_temperature: float = Field(default=0.3, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, alias="LLM_MAX_TOKENS")
    
    @validator("groq_api_key")
    def validate_groq_api_key(cls, v):
        """Warn if API key is not set."""
        if not v or v == "":
            import warnings
            warnings.warn(
                "GROQ_API_KEY is not set. LLM features will not work. "
                "Set it in your environment variables or .env file."
            )
        return v
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    redis_ttl: int = Field(default=86400, alias="REDIS_TTL")  # 24 hours
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Performance Settings
    worker_count: int = Field(default=2, alias="WORKER_COUNT")
    max_concurrent_requests: int = Field(default=100, alias="MAX_CONCURRENT_REQUESTS")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    
    # Agent Configuration
    enable_caching: bool = Field(default=True, alias="ENABLE_CACHING")
    agent_timeout: int = Field(default=30, alias="AGENT_TIMEOUT")  # seconds
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Ensure log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @validator("llm_temperature")
    def validate_temperature(cls, v):
        """Ensure temperature is in valid range."""
        if not 0 <= v <= 1:
            raise ValueError("LLM_TEMPERATURE must be between 0 and 1")
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        """Ensure environment is valid."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of {valid_envs}")
        return v.lower()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are loaded once and reused.
    This is the recommended pattern for FastAPI dependency injection.
    """
    return Settings()


# Export settings instance for convenience
settings = get_settings()