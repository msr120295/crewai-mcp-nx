# Get Started — Nutanix CrewAI Assistant

Murni CrewAI agent yang konek ke **ntnx-api-mcp-server** (Nutanix V4 API via MCP). Tanpa knowledge base, tanpa embedder — cuma butuh **LLM endpoint** dan **IP MCP server**.

---

## 1. Prasyarat

| Komponen | Keterangan |
|---|---|
| Python ≥ 3.11 / uv / Docker | pilih salah satu cara jalanin |
| LLM endpoint | OpenAI-compatible (omniroute/codex, vLLM, dll) |
| ntnx-api-mcp-server | bisa jalan di mesin yang sama atau beda host |

---

## 2. Quickstart (tanpa Docker)

```bash
cd /app/prism_mcp/nutanix-crewai-assistant
uv venv && uv pip install -e .
cp .env.example .env
```

Edit `.env`:

```ini
# LLM (omniroute/codex misalnya)
LLM_BASE_URL=http://<omniroute-host>:<port>/v1
LLM_API_KEY=<key>
LLM_MODEL=<model>

# Nutanix MCP server — IP-nya di env
NUTANIX_MCP_URL=http://<ip-mcp>:8000/mcp
```

> Ganti mode stdio kalau MCP di mesin yang sama dan nggak mau buka port:
> `NUTANIX_MCP_COMMAND=/app/prism_mcp/ntnx-api-mcp-server/.venv/bin/nutanix-mcp`

Jalankan:

```bash
uv run nx-assistant --selfcheck   # validasi config + MCP + tools
uv run nx-assistant               # chat REPL
```

Contoh: `cluster health nutanix seperti apa?`

---

## 3. Quickstart (Docker)

### Build

```bash
cd /app/prism_mcp/nutanix-crewai-assistant
docker build -t nx-assistant .
```

### Run (interactive REPL)

```bash
docker run -it --rm \
  -e LLM_BASE_URL=http://<omniroute-host>:<port>/v1 \
  -e LLM_API_KEY=<key> \
  -e LLM_MODEL=<model> \
  -e NUTANIX_MCP_URL=http://<ip-mcp>:8000/mcp \
  nx-assistant
```

Atau pakai file `.env`:

```bash
docker run -it --rm --env-file .env nx-assistant
```

### Run one-shot (tanpa REPL)

```bash
docker run --rm --env-file .env nx-assistant \
  nx-assistant-ask "cluster health nutanix seperti apa?"
```

### docker-compose (assistant + MCP server sekalian, satu host)

```yaml
# docker-compose.yml di folder yang sama
services:
  ntnx-mcp:
    image: ntnx-api-mcp-server          # build dari ../ntnx-api-mcp-server
    ports: ["8000:8000"]
    environment:
      PC_HOST: 10.1.1.10                # Prism Central
      PC_API_KEY: <key>
    command: ["serve-http", "--host", "0.0.0.0", "--port", "8000"]

  assistant:
    build: .
    environment:
      LLM_BASE_URL: http://<omniroute-host>:<port>/v1
      LLM_API_KEY: <key>
      LLM_MODEL: <model>
      NUTANIX_MCP_URL: http://ntnx-mcp:8000/mcp
    depends_on: [ntnx-mcp]
```

```bash
docker compose up -d
docker compose exec assistant nx-assistant
```

---

## 4. Verifikasi

1. `--selfcheck` harus exit 0 dan menampilkan tools dari MCP:
   `listOperations`, `getOperationSchema`, `getCodeSample`, `getOperationPermissions`, `<namespace>_execute`...
2. Kalau MCP belum siap → fallback ke stub tools (`get_cluster_health`, dst, data dummy) dengan log warning. Chat tetap jalan.
3. Smoke test: `uv run pytest tests/ -q`

---

## 5. Troubleshooting

| Gejala | Penyebab & solusi |
|---|---|
| `MCP unavailable ... falling back to stub` | MCP server belum jalan / URL salah — cek `curl http://<ip-mcp>:8000/mcp` |
| Tools MCP cuma 4 discovery | jalankan `nutanix-mcp init` di server MCP (butuh Prism Central) |
| LLM error format/response | omniroute/codex kadang tidak full OpenAI-compatible — cek error, sesuaikan `LLM_MODEL` |
| Container exit langsung saat REPL | `docker run` harus pakai `-it` (stdin buat REPL) |

---

## 6. Env vars lengkap

| Var | Wajib | Default | Fungsi |
|---|---|---|---|
| `LLM_BASE_URL` | ✅ | — | endpoint OpenAI-compatible (`/v1`) |
| `LLM_API_KEY` | ✅ | — | key LLM |
| `LLM_MODEL` | ✅ | — | nama model |
| `NUTANIX_MCP_URL` | ✅* | — | URL MCP HTTP (mode HTTP) |
| `NUTANIX_MCP_COMMAND` | ✅* | — | path binary nutanix-mcp (mode stdio) |
| `NUTANIX_MCP_ARGS` | ❌ | `serve-stdio` | args untuk mode stdio |
| `MCP_ENABLED` | ❌ | `true` | toggle koneksi MCP |
| `MEMORY_ENABLED` | ❌ | `false` | persistent memory (butuh embedder) |
| `EMBEDDER_*` | ❌ | — | hanya kalau `MEMORY_ENABLED=true` |

\* salah satu harus diisi; kalau dua-duanya kosong → stub tools.
