"""Local tool used only to exercise the tool_use/tool_result cycle before
any real MCP server (Fase 2+) is wired in. Replace/remove once Filesystem
and Git servers are connected.
"""
from datetime import datetime, timezone


class DemoAdapter:
    def list_tools(self) -> list[dict]:
        return [{
            "name": "get_time",
            "description": "Return the current UTC time.",
            "input_schema": {"type": "object", "properties": {}},
        }]

    def call_tool(self, name: str, arguments: dict):
        if name == "get_time":
            return datetime.now(timezone.utc).isoformat()
        raise ValueError(f"unknown tool {name}")
