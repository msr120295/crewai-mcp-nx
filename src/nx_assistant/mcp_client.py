"""MCP connection to ntnx-api-mcp-server.

Dua mode (dipilih via .env):
- HTTP   : NUTANIX_MCP_URL=http://<ip>:8000/mcp   → MCPServerHTTP
- stdio  : NUTANIX_MCP_COMMAND=...nutanix-mcp     → MCPServerStdio (spawn subprocess)

Tools-nya langsung dipakai Agent via `Agent(mcps=[...])` — crewai 1.15+
melakukan discovery + wrapping otomatis lewat MCPToolResolver.
"""

from __future__ import annotations

import logging

from crewai.mcp.config import MCPServerConfig, MCPServerHTTP, MCPServerStdio
from crewai.mcp.tool_resolver import MCPToolResolver

from nx_assistant.config import Settings

logger = logging.getLogger(__name__)


def build_mcp_server_config(settings: Settings) -> MCPServerConfig | None:
    """Build one MCP server config from .env; None if disabled/unconfigured."""
    if not settings.mcp_enabled:
        return None
    if settings.nutanix_mcp_url:
        return MCPServerHTTP(url=settings.nutanix_mcp_url)
    if settings.nutanix_mcp_command:
        return MCPServerStdio(
            command=settings.nutanix_mcp_command,
            args=settings.nutanix_mcp_args_list,
        )
    return None


def resolve_mcp_tools(settings: Settings) -> tuple[list, MCPToolResolver | None]:
    """Discover tools from the configured MCP server.

    Returns (tools, resolver) — keep the resolver reference alive for the
    crew's lifetime and call resolver.cleanup() when done.
    """
    config = build_mcp_server_config(settings)
    if config is None:
        return [], None
    # crewai 1.15 MCPToolResolver requires (agent, logger) positionally, but
    # the native MCP resolution path (_resolve_native) never touches them.
    resolver = MCPToolResolver(agent=None, logger=None)
    try:
        tools = resolver.resolve([config])
    except Exception:
        logger.exception("MCP tool discovery failed for ntnx-api-mcp-server")
        resolver.cleanup()
        raise
    logger.info("Discovered %d MCP tools", len(tools))
    return tools, resolver
