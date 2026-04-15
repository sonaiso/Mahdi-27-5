"""Shared dependencies — التبعيات المشتركة.

Provides dependency injection callables for FastAPI route handlers
(settings, database sessions, etc.).
"""

from __future__ import annotations

from api.config import Settings, settings


def get_settings() -> Settings:
    """Return the global application settings."""
    return settings
