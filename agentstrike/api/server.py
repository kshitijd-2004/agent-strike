"""FastAPI application factory.

The factory pattern keeps the app testable: each test can construct a fresh
app with its own settings, in-memory event log, and stub agents. The module
also exposes a top-level ``app`` for ``uvicorn agentstrike.api.server:app``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentstrike.config import Settings


def create_app(settings: "Settings | None" = None) -> Any:
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
    raise NotImplementedError


app: Any = None
"""Module-level ASGI app populated at import time by :func:`create_app`.

Implementation note:
    The real module will replace this ``None`` with
    ``app = create_app()`` once :func:`create_app` is implemented, so the
    standard ``uvicorn agentstrike.api.server:app`` invocation works.
"""
