"""Crew definition — Nutanix Operations Assistant.

Murni agent + MCP: tools dari ntnx-api-mcp-server (HTTP atau stdio via .env),
tanpa knowledge base dan tanpa embedder. CrewAI persistent memory opsional
(MEMORY_ENABLED=true) karena butuh embedder endpoint.
"""

from __future__ import annotations

import logging

from crewai import Agent, Crew, Process, Task

from nx_assistant.config import Settings
from nx_assistant.llm import build_embedder, build_llm
from nx_assistant.mcp_client import build_mcp_server_config, resolve_mcp_tools
from nx_assistant.tools.nutanix import nutanix_stub_tools

logger = logging.getLogger(__name__)


def acquire_tools(settings: Settings) -> tuple[list, object | None]:
    """MCP tools if configured, else local stubs. Returns (tools, resolver|None)."""
    if settings.mcp_configured:
        try:
            return resolve_mcp_tools(settings)
        except Exception as exc:
            logger.warning("MCP unavailable (%s) — falling back to stub tools", exc)
    return nutanix_stub_tools(), None


def build_crew(settings: Settings) -> Crew:
    llm = build_llm(settings)
    tools, resolver = acquire_tools(settings)
    logger.info("Agent tools: %s", [t.name for t in tools])

    agent = Agent(
        role="Nutanix Operations Assistant",
        goal=(
            "Answer Nutanix infrastructure questions accurately using the "
            "Nutanix MCP tools, remembering context from previous conversations."
        ),
        backstory=(
            "You are an expert Nutanix infrastructure operations engineer. "
            "You operate through MCP tools backed by the Nutanix V4 API: "
            "listOperations / getOperationSchema / getCodeSample / "
            "getOperationPermissions for discovery, and <namespace>_execute "
            "(prism, vmm, clustermgmt, lifecycle, monitoring, etc.) for live "
            "data. Answer in the same language the user writes in (Indonesian "
            "or English). Before destructive operations, check permissions "
            "and confirm with the user."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
    )

    task = Task(
        description=(
            "Answer the user's question: {question}\n\n"
            "Work through the MCP tools: use listOperations/getOperationSchema "
            "to find the right operation, then <namespace>_execute to get live "
            "data. Be concise and factual."
        ),
        expected_output=(
            "A concise, correct answer in the user's language, citing the "
            "tool operations used."
        ),
        agent=agent,
    )

    return Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        memory=settings.memory_enabled,   # off by default (needs embedder)
        embedder=build_embedder(settings) if settings.memory_enabled else None,
        verbose=True,
    )
