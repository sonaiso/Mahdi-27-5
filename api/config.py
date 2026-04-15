"""API configuration — إعدادات الواجهة.

Centralised settings using pydantic-settings for environment-based
configuration (DB URL, debug mode, API prefix, etc.).
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    app_name: str = "Arabic Engine API"
    version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api/v1"
    database_url: str = ""

    @classmethod
    def from_env(cls) -> Settings:
        """Create settings from environment variables."""
        return cls(
            app_name=os.getenv("APP_NAME", "Arabic Engine API"),
            version=os.getenv("APP_VERSION", "0.1.0"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            api_prefix=os.getenv("API_PREFIX", "/api/v1"),
            database_url=os.getenv("DATABASE_URL", ""),
        )


settings = Settings.from_env()
