"""FastAPI application — التطبيق الرئيسي.

Creates and configures the FastAPI app, registers routers, and
provides the lifespan context manager.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from api.config import settings
from api.middleware.trace import TraceMiddleware
from api.routers import (
    cognition,
    diacritics,
    judgement,
    morphology,
    pipeline,
    semantics,
    syllables,
    syntax,
    unicode,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown hooks."""
    # Startup: initialize resources
    yield
    # Shutdown: cleanup resources


def create_app() -> FastAPI:
    """Factory function that creates and configures the FastAPI app."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=(
            "Computational Arabic language analysis API based on the "
            "atomic-beginning law and ascending closure principles."
        ),
        lifespan=lifespan,
    )

    # Register middleware
    app.add_middleware(TraceMiddleware)

    # Register routers
    prefix = settings.api_prefix
    app.include_router(unicode.router, prefix=f"{prefix}/unicode", tags=["E1 Unicode"])
    app.include_router(diacritics.router, prefix=f"{prefix}/diacritics", tags=["E2 Diacritics"])
    app.include_router(syllables.router, prefix=f"{prefix}/syllables", tags=["E3 Syllables"])
    app.include_router(morphology.router, prefix=f"{prefix}/morphology", tags=["E4 Morphology"])
    app.include_router(syntax.router, prefix=f"{prefix}/syntax", tags=["E5 Syntax"])
    app.include_router(semantics.router, prefix=f"{prefix}/semantics", tags=["E6 Semantics"])
    app.include_router(cognition.router, prefix=f"{prefix}/cognition", tags=["E7 Cognition"])
    app.include_router(judgement.router, prefix=f"{prefix}/judgement", tags=["E8 Judgement"])
    app.include_router(pipeline.router, prefix=f"{prefix}/pipeline", tags=["Pipeline"])

    return app


app = create_app()
