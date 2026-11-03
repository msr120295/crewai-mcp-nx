"""Stub Nutanix tools — dummy data, swap-ready for ntnx-api-mcp-server (MCP stdio).

TODO (saat Prism Central tersedia):
    Ganti tiap stub dengan pemanggilan ntnx-api-mcp-server via MCPServerAdapter:

        from crewai.mcp import MCPServerAdapter
        server = MCPServerAdapter(server_params={
            "command": "/app/prism_mcp/ntnx-api-mcp-server/.venv/bin/nutanix-mcp",
            "args": ["serve-stdio"],
            "env": {...},
        })
        tools = server.tools  # listOperations, getOperationSchema, <ns>_execute, ...

    Lalu di crew.py cukup ganti `tools=nutanix_stub_tools()` menjadi
    `tools=server.tools` — agent/task tidak perlu diubah.
"""

from __future__ import annotations

import json
from typing import Any, Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class _NoInput(BaseModel):
    pass


class ClusterHealthInput(BaseModel):
    cluster: str = Field(default="all", description="Cluster name, or 'all'")


class AlertsInput(BaseModel):
    severity: str = Field(
        default="all", description="Filter by severity: critical|warning|info|all"
    )


class VmsInput(BaseModel):
    cluster: str = Field(default="all", description="Cluster name to filter VMs")


class NutanixStubTool(BaseTool):
    """Base class: stub tools carry realistic dummy payloads."""

    name: str
    description: str
    args_schema: Type[BaseModel] = _NoInput
    payload: dict[str, Any] = {}

    def _run(self, **kwargs: Any) -> str:
        return json.dumps(self.payload, indent=2)


def _stub(name: str, description: str, payload: dict, schema: Type[BaseModel] = _NoInput) -> NutanixStubTool:
    return NutanixStubTool(name=name, description=description, payload=payload, args_schema=schema)


# ── Dummy data ────────────────────────────────────────────────────────────────

_CLUSTERS = [
    {"name": "cluster-01", "nodes": 4, "cpu_usage_pct": 41.2, "memory_usage_pct": 58.7,
     "storage_usage_pct": 63.1, "status": "healthy"},
    {"name": "cluster-02", "nodes": 3, "cpu_usage_pct": 77.9, "memory_usage_pct": 81.4,
     "storage_usage_pct": 88.6, "status": "degraded"},
    {"name": "cluster-03", "nodes": 6, "cpu_usage_pct": 22.5, "memory_usage_pct": 35.0,
     "storage_usage_pct": 40.2, "status": "healthy"},
]

_ALERTS = [
    {"id": "alert-1001", "cluster": "cluster-02", "severity": "critical",
     "message": "Storage container 'sc-prod' usage above 88%"},
    {"id": "alert-1002", "cluster": "cluster-02", "severity": "warning",
     "message": "Host node-2 disk latency elevated (35ms)"},
    {"id": "alert-1003", "cluster": "cluster-01", "severity": "info",
     "message": "LCM inventory update available"},
]

_VMS = [
    {"name": "vm-db-prod-01", "cluster": "cluster-01", "state": "ON", "vcpu": 8, "memory_gb": 32},
    {"name": "vm-web-01", "cluster": "cluster-01", "state": "ON", "vcpu": 4, "memory_gb": 16},
    {"name": "vm-test-07", "cluster": "cluster-02", "state": "OFF", "vcpu": 2, "memory_gb": 8},
]


def nutanix_stub_tools() -> list[BaseTool]:
    """All stub tools — nanti diganti MCP tools dari ntnx-api-mcp-server."""
    return [
        _stub(
            "get_cluster_health",
            "Get overall Nutanix cluster health: status per cluster, resource usage, "
            "and a summary. Use for questions like 'cluster health nutanix seperti apa'.",
            {
                "overall_health": "degraded",
                "summary": "2 healthy, 1 degraded (cluster-02 storage 88%)",
                "clusters": _CLUSTERS,
            },
        ),
        _stub(
            "list_clusters",
            "List all Nutanix clusters with node counts and resource usage.",
            {"clusters": _CLUSTERS},
        ),
        _stub(
            "get_alerts",
            "List Nutanix alerts, optionally filtered by severity "
            "(critical|warning|info).",
            {"alerts": _ALERTS},
            schema=AlertsInput,
        ),
        _stub(
            "list_vms",
            "List VMs, optionally filtered by cluster name.",
            {"vms": _VMS},
            schema=VmsInput,
        ),
    ]
