import os
import sys

import anthropic

from host.conversation import Conversation
from host.demo_tool import DemoAdapter
from host.logger import JsonlLogger
from host.tool_registry import ToolRegistry


def load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY no configurada (copia .env.example a .env)")

    model = os.environ.get("MCP_MODEL", "claude-haiku-4-5-20251001")
    log_path = os.environ.get("MCP_LOG_PATH", "logs/session.jsonl")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    client = anthropic.Anthropic(api_key=api_key)

    registry = ToolRegistry()
    registry.register("demo", DemoAdapter(), transport="local")
    # Fase 2 añadirá: registry.register("fs", StdioAdapter(...), "stdio")
    #                 registry.register("git", StdioAdapter(...), "stdio")
    # Fase 3/4 añadirá: registry.register("dist", StdioAdapter(...) o HttpAdapter(...), ...)

    logger = JsonlLogger(log_path)
    conversation = Conversation(client, model, registry, logger)

    print("Chatbot MCP — Fase 1 (escribe 'salir' para terminar)")
    while True:
        try:
            user_text = input("\ntú> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_text.lower() in {"salir", "exit", "quit"}:
            break
        if not user_text:
            continue
        reply = conversation.send(user_text)
        print(f"\nbot> {reply}")


if __name__ == "__main__":
    main()
