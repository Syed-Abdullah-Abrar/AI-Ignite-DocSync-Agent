"""
DocSync Configuration Module

Loads environment variables and provides typed access throughout the application.
"""
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

import os


@dataclass
class AIConfig:
    """AI model configuration."""
    minimax_api_key: str = os.getenv("MINIMAX_API_KEY", "")
    minimax_api_base: str = os.getenv("OPENAI_API_BASE", "https://api.minimax.io/v1")
    model_name: str = "MiniMax-m2.7"


@dataclass
class UHIConfig:
    """ABDM UHI gateway configuration."""
    client_id: str = os.getenv("UHI_CLIENT_ID", "")
    client_secret: str = os.getenv("UHI_CLIENT_SECRET", "")
    gateway_url: str = os.getenv("UHI_GATEWAY_URL", "https://sandbox.abdm.gov.in/uhi/gateway")
    callback_url: str = os.getenv("CALLBACK_URL", "")


@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration."""
    url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ayusync")


@dataclass
class LangfuseConfig:
    """Langfuse observability configuration."""
    public_key: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    secret_key: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    host: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")


@dataclass
class WhatsAppConfig:
    """WhatsApp MCP configuration."""
    api_key: str = os.getenv("WHATSAPP_API_KEY", "")


@dataclass
class AppConfig:
    """Main application configuration."""
    ai: AIConfig = field(default_factory=AIConfig)
    uhi: UHIConfig = field(default_factory=UHIConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    langfuse: LangfuseConfig = field(default_factory=LangfuseConfig)
    # FIX: Renamed from `whats_app` to `whatsapp` for consistency
    whatsapp: WhatsAppConfig = field(default_factory=WhatsAppConfig)


def get_config() -> AppConfig:
    """Get the application configuration singleton."""
    return AppConfig()


# Convenience accessors
config = get_config()
