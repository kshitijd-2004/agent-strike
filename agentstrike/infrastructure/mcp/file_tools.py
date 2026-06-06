"""File tools for the mock MCP server.

Exposes::

    file.read(path: str) -> str
    file.write(path: str, contents: str) -> None
    file.list(path: str) -> list[str]

against an in-memory virtual filesystem seeded per scenario. The sandbox
prevents path traversal (``..``) and never touches the host disk.
"""

from __future__ import annotations

from typing import Any


def register(server: Any, sandbox: dict[str, str]) -> None:
    """Register the ``file.*`` tools with ``server``.

    Args:
        server:  MCP server returned by :func:`agentstrike.infrastructure.mcp.server.build_server`.
        sandbox: Mapping of virtual path -> contents that seeds the FS.
    """
    raise NotImplementedError


async def file_read(path: str, sandbox: dict[str, str]) -> str:
    """Return the contents of ``path`` from the sandbox.

    Raises:
        FileNotFoundError: ``path`` is not in the sandbox.
        PermissionError:   ``path`` attempts traversal (``..``) or is absolute.
    """
    raise NotImplementedError


async def file_write(path: str, contents: str, sandbox: dict[str, str]) -> None:
    """Write ``contents`` to ``path`` in the sandbox (in-memory only)."""
    raise NotImplementedError


async def file_list(path: str, sandbox: dict[str, str]) -> list[str]:
    """List virtual directory entries beneath ``path``."""
    raise NotImplementedError
