"""Trace middleware — البرمجية الوسيطة للتتبع.

Adds request tracing headers and logging for audit and reproducibility.
"""

from __future__ import annotations

import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TraceMiddleware(BaseHTTPMiddleware):
    """Middleware that adds X-Request-ID and X-Duration-Ms headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # type: ignore[type-arg]
        """Add tracing headers to every request/response cycle."""
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        # Attach request_id to request state
        request.state.request_id = request_id

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Duration-Ms"] = f"{duration_ms:.2f}"

        return response
