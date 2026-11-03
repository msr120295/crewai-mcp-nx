# Nutanix CrewAI Assistant

AI assistant berbasis **CrewAI** — murni agent yang konek ke `ntnx-api-mcp-server` (Nutanix V4 API via MCP). Tanpa knowledge base, tanpa embedder. Persistent memory opsional.

## Setup

```bash
cd /app/prism_mcp/nutanix-crewai-assistant
uv venv && uv pip install -e .
cp .env.example .env
# edit .env: LLM_* (omniroute/codex) + NUTANIX_MCP_URL
```

Yang wajib diisi cuma dua hal: **LLM endpoint** dan **IP MCP server**.

## Run

```bash
# validasi config + MCP + tools (tanpa chat LLM call)
uv run nx-assistant --selfcheck

# chat REPL
uv run nx-assistant
```

Contoh pertanyaan: `cluster health nutanix seperti apa?`

## Koneksi MCP

### Mode 1 — HTTP (recommended, "IP mcp-nya di env")

```bash
# sisi server MCP
cd /app/prism_mcp/ntnx-api-mcp-server && source .venv/bin/activate
nutanix-mcp serve-http --host 0.0.0.0 --port 8000
```
```ini
# .env project ini
NUTANIX_MCP_URL=http://127.0.0.1:8000/mcp
MCP_ENABLED=true
```

### Mode 2 — stdio (spawn subprocess otomatis)

```ini
NUTANIX_MCP_COMMAND=/app/prism_mcp/ntnx-api-mcp-server/.venv/bin/nutanix-mcp
NUTANIX_MCP_ARGS=serve-stdio
```

### Behavior

- MCP configured tapi tidak reachable → **fallback otomatis ke stub tools** (data dummy), chat tetap jalan (log warning).
- Tools dari MCP: `listOperations`, `getOperationSchema`, `getCodeSample`, `getOperationPermissions` + `<namespace>_execute` per namespace.
- Namespace tools baru muncul setelah `nutanix-mcp init` (butuh Prism Central).

## Persistent memory (opsional)

Default `MEMORY_ENABLED=false` — murni MCP agent, tidak butuh embedder.
Kalau mau context antar sesi:

```ini
MEMORY_ENABLED=true
EMBEDDER_BASE_URL=http://127.0.0.1:11434/v1   # endpoint dengan /v1/embeddings
EMBEDDER_API_KEY=ollama
EMBEDDER_MODEL=nomic-embed-text
```

## Arsitektur

- `src/nx_assistant/config.py` — settings dari `.env` (pydantic-settings)
- `llm.py` — LLM OpenAI-compatible (+ embedder helper, hanya untuk memory)
- `mcp_client.py` — koneksi MCP (HTTP/stdio) + tool discovery
- `tools/nutanix.py` — stub tools dummy (fallback)
- `crew.py` — Agent + Task + Crew
- `main.py` — CLI REPL + `--selfcheck`
