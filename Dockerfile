FROM python:3.12-slim

LABEL org.opencontainers.image.title="nutanix-crewai-assistant"
LABEL org.opencontainers.image.description="CrewAI assistant connected to ntnx-api-mcp-server (Nutanix V4 API via MCP)"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests

RUN pip install --no-cache-dir . \
    && groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# Default: interactive chat REPL (docker run -it ...)
# One-shot: docker run --rm ... nx-assistant-ask "question"
ENTRYPOINT ["nx-assistant"]
CMD []

# A helper alias for one-shot questions via a separate entrypoint is provided
# by the same image using --entrypoint override, e.g.:
#   docker run --rm --entrypoint nx-assistant-ask ... "question"
