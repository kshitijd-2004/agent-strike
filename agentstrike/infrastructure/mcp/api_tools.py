"""API tools for the mock MCP server.

Exposes a single tool::

    api.fetch(url: str, method: str = "GET", body: str | None = None) -> dict

The tool resolves URLs against an in-memory routing table seeded per scenario
rather than performing real network I/O. Outbound traffic to *unknown* hosts
deliberately returns a structured "blocked" result so red-team scenarios can
test exfiltration attempts without leaking data.
"""

from __future__ import annotations

from typing import Any


def register(server: Any, routes: dict[str, Any]) -> None:
    """Register the ``api.*`` tools with ``server``.

    Args:
        server: MCP server instance.
        routes: Mapping of URL prefix -> canned JSON response.
    """
    raise NotImplementedError


async def api_fetch(
    url: str,
    method: str,
    body: str | None,
    routes: dict[str, Any],
) -> dict[str, Any]:
    """Resolve ``url`` against the canned ``routes`` table.

    Returns a dict shaped like ``{"status": int, "headers": {...}, "body": ...}``.
    Unknown hosts return ``{"status": 0, "blocked": true, "reason": ...}``.
    """
    raise NotImplementedError
