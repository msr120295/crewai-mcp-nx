"""Configuration for the Nutanix CrewAI assistant (pydantic-settings)."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """All settings come from environment / .env file at project root."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM (OpenAI-compatible)
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    # Embedder (OpenAI-compatible) — ONLY needed if MEMORY_ENABLED=true
    embedder_model: str = ""
    embedder_base_url: str = ""
    embedder_api_key: str = ""

    # Nutanix MCP server (ntnx-api-mcp-server)
    # Mode HTTP (recommended — "masukin IP mcp-nya di env"):
    #   NUTANIX_MCP_URL=http://<ip>:8000/mcp
    # Mode stdio (spawn nutanix-mcp sebagai subprocess):
    #   NUTANIX_MCP_COMMAND=/app/prism_mcp/ntnx-api-mcp-server/.venv/bin/nutanix-mcp
    #   NUTANIX_MCP_ARGS=serve-stdio
    mcp_enabled: bool = True
    nutanix_mcp_url: str = ""
    nutanix_mcp_command: str = ""
    nutanix_mcp_args: str = "serve-stdio"

    # CrewAI persistent memory (butuh embedder — default OFF agar murni MCP agent)
    memory_enabled: bool = False

    @property
    def nutanix_mcp_args_list(self) -> list[str]:
        return [a.strip() for a in self.nutanix_mcp_args.split() if a.strip()]

    @property
    def mcp_configured(self) -> bool:
        return bool(self.nutanix_mcp_url or self.nutanix_mcp_command)

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_base_url and self.llm_api_key and self.llm_model)


def get_settings() -> Settings:
    return Settings()
