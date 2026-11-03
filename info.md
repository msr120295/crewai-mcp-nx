# Info — nutanix-crewai-assistant

> Catatan dari sesi Claude Code, 2026-11-03

## 1. Koneksi CrewAI Agent ke MCP Nutanix (source code)

**Status: sudah wired up penuh di source code.**

Alur koneksi:

1. **`crew.py:22-29` — `acquire_tools()`**: Cek `settings.mcp_configured`.
   - Jika MCP dikonfigurasi → panggil `resolve_mcp_tools()`.
   - Jika gagal/tidak di-set → fallback ke `nutanix_stub_tools()` (dummy data).
2. **`mcp_client.py:37-53` — `resolve_mcp_tools()`**: Pakai `MCPToolResolver` dari CrewAI untuk discovery tools dari MCP server.
3. **`mcp_client.py:23-34` — `build_mcp_server_config()`**: Dua mode koneksi:
   - **HTTP**: `NUTANIX_MCP_URL=http://<ip>:8000/mcp` → `MCPServerHTTP`
   - **stdio**: `NUTANIX_MCP_COMMAND=...` → `MCPServerStdio` (spawn subprocess)
4. **`config.py:50-51` — `mcp_configured`**: `True` jika salah satu env var MCP di-set.

Kesimpulan: tanpa env var MCP, agent jalan dengan 4 stub tools (data dummy). Set `NUTANIX_MCP_URL` di `.env` → agent otomatis discover tools dari `ntnx-api-mcp-server`.

## 2. Selfcheck vs REPL Interactive

| | `--selfcheck` | REPL Interactive |
|---|---|---|
| Fungsi | Validasi config tanpa chat LLM | Chat loop interaktif |
| Butuh LLM aktif | Tidak | Ya |
| Kegunaan | Smoke test / CI-CD setelah build | Penggunaan sehari-hari |
| Exit code | 0 = semua OK, 1 = ada yang salah | — |

Selfcheck memvalidasi 4 hal: settings loaded, LLM configured, MCP connection (atau fallback stub), crew build.

## 3. Docker Build & Run

Dockerfile: base `python:3.12-slim`, non-root user `appuser`, entrypoint `nx-assistant`.
Entry point lain: `nx-assistant-ask` (one-shot question, tanpa REPL).

**Penting:** Docker daemon jalan di host (Zorin OS), jadi build context harus pakai **path host**, bukan path container.

```bash
# Build image (path host!)
nsenter -t 1 -m -u -n -i -- docker build -t nutanix-crewai-assistant /home/l340/salman/prism_mcp/nutanix-crewai-assistant
```

Hasil build terakhir (2026-11-03): **sukses**, ~197 detik, image `nutanix-crewai-assistant:latest`.

```bash
# Selfcheck (tanpa LLM)
nsenter -t 1 -m -u -n -i -- docker run --rm nutanix-crewai-assistant --selfcheck

# REPL interactive (pakai .env)
nsenter -t 1 -m -u -n -i -- docker run -it --env-file /home/l340/salman/prism_mcp/nutanix-crewai-assistant/.env nutanix-crewai-assistant

# One-shot question (pakai .env)
nsenter -t 1 -m -u -n -i -- docker run --rm --env-file /home/l340/salman/prism_mcp/nutanix-crewai-assistant/.env --entrypoint nx-assistant-ask nutanix-crewai-assistant "cluster health?"
```

## 4. Status .env

`.env` sudah disiapkan user berisi konfigurasi LLM (base URL, API key, model) dan MCP (`NUTANIX_MCP_URL`). Tinggal run container dengan `--env-file`.
