"""LLM factory — custom OpenAI-compatible endpoint."""

from __future__ import annotations

from crewai import LLM

from nx_assistant.config import Settings


def build_llm(settings: Settings) -> LLM:
    """Create a CrewAI LLM pointing at a custom OpenAI-compatible base URL."""
    return LLM(
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    )


def build_embedder(settings: Settings) -> dict:
    """CrewAI embedder config — only used when memory_enabled."""
    base_url = settings.embedder_base_url or settings.llm_base_url
    api_key = settings.embedder_api_key or settings.llm_api_key
    model = settings.embedder_model or settings.llm_model
    return {
        "provider": "openai",
        "config": {
            "model": model,
            "api_key": api_key,
            "url": base_url,
        },
    }
