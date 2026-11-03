"""Smoke tests — no LLM calls, no network."""

from nx_assistant.config import get_settings
from nx_assistant.mcp_client import build_mcp_server_config
from nx_assistant.tools.nutanix import nutanix_stub_tools


def test_stub_tools_registered():
    tools = nutanix_stub_tools()
    names = {t.name for t in tools}
    assert {"get_cluster_health", "list_clusters", "get_alerts", "list_vms"} <= names


def test_cluster_health_stub_runs():
    tools = {t.name: t for t in nutanix_stub_tools()}
    out = tools["get_cluster_health"]._run()
    assert "overall_health" in out


def test_mcp_config_http(monkeypatch):
    monkeypatch.setenv("NUTANIX_MCP_URL", "http://127.0.0.1:8000/mcp")
    cfg = build_mcp_server_config(get_settings())
    assert cfg is not None
    assert getattr(cfg, "url", "").endswith("/mcp")
