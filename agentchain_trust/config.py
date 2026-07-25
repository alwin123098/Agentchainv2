"""Configuration management for AgentChain Trust Layer."""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    api_env: str = Field(default="development", alias="API_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    secret_key: str = Field(default="dev-secret-key", alias="SECRET_KEY")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=4, alias="WORKERS")

    # Database
    database_url: str = Field(default="postgresql://user:password@localhost:5432/agentchain_trust", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # JWT
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, alias="JWT_EXPIRATION_HOURS")

    # Trust Layer
    verification_timeout_seconds: int = Field(default=30, alias="VERIFICATION_TIMEOUT_SECONDS")
    replay_enabled: bool = Field(default=True, alias="REPLAY_ENABLED")
    audit_log_enabled: bool = Field(default=True, alias="AUDIT_LOG_ENABLED")

    # Monitoring
    prometheus_enabled: bool = Field(default=True, alias="PROMETHEUS_ENABLED")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Rate Limiting (per minute)
    rate_limit_free: int = 100
    rate_limit_pro: int = 1000
    rate_limit_enterprise: int = 10000

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()