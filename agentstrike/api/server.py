"""FastAPI application factory.

The factory pattern keeps the app testable: each test can construct a fresh
app with its own settings, in-memory event log, and stub agents. The module
also exposes a top-level ``app`` for ``uvicorn agentstrike.api.server:app``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from agentstrike import __version__

if TYPE_CHECKING:
    from agentstrike.config import Settings


def create_app(settings: "Settings | None" = None) -> FastAPI:
    """Build and return a configured FastAPI app.

    The factory:
        1. Loads :class:`agentstrike.config.Settings` if not supplied.
        2. Wires the routers from :mod:`agentstrike.api.routes` and
           :mod:`agentstrike.api.sse`.
        3. Configures CORS so the React dashboard can connect.
        4. Mounts startup / shutdown handlers for the global event broadcaster.

    Args:
        settings: Optional override; defaults to :func:`agentstrike.config.get_settings`.

    Returns:
        A ready-to-serve ``FastAPI`` instance.
    """
    del settings

    fastapi_app = FastAPI(
        title="AgentStrike",
        version=__version__,
        description="Red team simulation platform for Claude-based AI agent deployments.",
    )

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @fastapi_app.get("/")
    async def root() -> dict[str, str]:
        return {
            "name": "AgentStrike",
            "version": __version__,
            "status": "scaffold",
            "docs": "/docs",
        }

    @fastapi_app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @fastapi_app.get("/favicon.ico")
    async def favicon() -> Response:
        return Response(status_code=204)

    return fastapi_app


app: FastAPI = create_app()
"""Module-level ASGI app for ``uvicorn agentstrike.api.server:app``.

Once :mod:`agentstrike.api.routes` and :mod:`agentstrike.api.sse` are
implemented, :func:`create_app` should ``include_router`` them here so the
``/api/*`` and SSE endpoints come online automatically.
"""
