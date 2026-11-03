"""CLI chat REPL for the Nutanix CrewAI assistant (pure MCP agent)."""

from __future__ import annotations

import argparse
import sys

from nx_assistant.config import get_settings
from nx_assistant.crew import build_crew
from nx_assistant.mcp_client import build_mcp_server_config
from nx_assistant.tools.nutanix import nutanix_stub_tools


def selfcheck() -> int:
    """Validate config, MCP connection, and tools -- no chat LLM call."""
    settings = get_settings()
    print("[1/4] Settings loaded (project .env: %s)" % settings.model_config["env_file"])
    print("      LLM configured: %s" % settings.llm_configured)
    if not settings.llm_configured:
        print("      WARNING: .env belum diisi -- copy .env.example lalu isi LLM_* / NUTANIX_MCP_*")

    cfg = build_mcp_server_config(settings)
    print("[2/4] MCP server: " + (repr(cfg) if cfg else "not configured -> stub tools"))
    if cfg is None:
        print("      fallback stubs: " + str([t.name for t in nutanix_stub_tools()]))

    if not settings.llm_configured:
        print("[3/4] Skipped crew build (LLM not configured)")
        print("[4/4] Skipped")
        return 0

    try:
        crew = build_crew(settings)
    except Exception as exc:
        print("[3/4] Crew build FAILED: %s" % exc)
        return 1
    agent = crew.agents[0]
    tools = agent.tools or []
    print("[3/4] Agent tools (%d): %s" % (len(tools), [getattr(t, "name", t) for t in tools]))
    print("[4/4] Crew built OK (memory=%s)" % settings.memory_enabled)
    return 0


def chat() -> int:
    settings = get_settings()
    if not settings.llm_configured:
        print("LLM belum dikonfigurasi. Copy .env.example -> .env dan isi LLM_* variables.")
        return 1

    crew = build_crew(settings)
    mode = "MCP" if settings.mcp_configured else "STUB"
    memory = "on" if settings.memory_enabled else "off"
    print("Nutanix Ops Assistant (tools: %s, memory: %s). Ketik exit untuk keluar." % (mode, memory))
    while True:
        try:
            question = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        result = crew.kickoff(inputs={"question": question})
        print("\nAssistant > %s" % result.raw)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="nx-assistant")
    parser.add_argument("--selfcheck", action="store_true",
                        help="Validate config/MCP/tools without a chat LLM call")
    args = parser.parse_args()
    if args.selfcheck:
        return selfcheck()
    return chat()


if __name__ == "__main__":
    sys.exit(main())


def ask() -> int:
    """One-shot: print answer for a question passed as argv, no REPL."""
    if len(sys.argv) < 2:
        print("Usage: nx-assistant-ask \"your question\"")
        return 1
    question = " ".join(sys.argv[1:])
    settings = get_settings()
    if not settings.llm_configured:
        print("LLM belum dikonfigurasi (.env).")
        return 1
    crew = build_crew(settings)
    result = crew.kickoff(inputs={"question": question})
    print(result.raw)
    return 0
