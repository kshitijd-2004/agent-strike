"""Mock MCP (Model Context Protocol) tool environment.

Provides a self-contained, in-process MCP server that the agents can call
without touching the real internet or filesystem. Three tool families are
exposed:

* :mod:`agentstrike.infrastructure.mcp.file_tools`        — virtual filesystem.
* :mod:`agentstrike.infrastructure.mcp.api_tools`         — mock HTTP API.
* :mod:`agentstrike.infrastructure.mcp.data_store_tools`  — mock key/value
  store (used to model "secrets" and "user data" for exfiltration scenarios).

The :class:`agentstrike.infrastructure.mcp.server.MockMCPServer` registers
every tool and exposes the standard MCP transport so agents can connect via
the Anthropic SDK's tool-use interface.
"""
