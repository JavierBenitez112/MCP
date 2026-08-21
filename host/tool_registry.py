class ToolRegistry:
    """Aggregates tools from multiple MCP servers under a unique, prefixed
    name (e.g. fs__read_file, dist__consultar_inventario), so all servers
    can share one Messages API `tools` array without name collisions.
    """

    def __init__(self):
        self._adapters = {}
        self._transports = {}

    def register(self, prefix: str, adapter, transport: str) -> None:
        self._adapters[prefix] = adapter
        self._transports[prefix] = transport

    def tool_schemas(self) -> list[dict]:
        schemas = []
        for prefix, adapter in self._adapters.items():
            for tool in adapter.list_tools():
                schemas.append({**tool, "name": f"{prefix}__{tool['name']}"})
        return schemas

    def split(self, prefixed_name: str) -> tuple[str, str]:
        prefix, _, real_name = prefixed_name.partition("__")
        return prefix, real_name

    def transport(self, prefix: str) -> str:
        return self._transports.get(prefix, "unknown")

    def call_tool(self, prefixed_name: str, arguments: dict):
        prefix, real_name = self.split(prefixed_name)
        adapter = self._adapters[prefix]
        return adapter.call_tool(real_name, arguments)
