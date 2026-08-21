import time

import anthropic

from host.logger import JsonlLogger
from host.tool_registry import ToolRegistry


class Conversation:
    """Messages API loop: sends the user turn, resolves every tool_use the
    model requests against the registry, and keeps looping until the model
    returns a final text answer. Full history (including tool blocks) stays
    in memory for context.
    """

    def __init__(self, client: anthropic.Anthropic, model: str,
                 registry: ToolRegistry, logger: JsonlLogger, max_tokens: int = 1024):
        self.client = client
        self.model = model
        self.registry = registry
        self.logger = logger
        self.max_tokens = max_tokens
        self.messages: list[dict] = []

    def send(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})

        while True:
            start = time.time()
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                tools=self.registry.tool_schemas(),
                messages=self.messages,
            )
            latency_ms = (time.time() - start) * 1000
            self.logger.log(server="anthropic", transport="https", direction="recv",
                             type_="response", id_=response.id, method="messages.create",
                             latency_ms=latency_ms)

            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                return "".join(b.text for b in response.content if b.type == "text")

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                server, real_name = self.registry.split(block.name)
                start = time.time()
                try:
                    result = self.registry.call_tool(block.name, block.input)
                    is_error = False
                except Exception as exc:
                    result = str(exc)
                    is_error = True
                latency_ms = (time.time() - start) * 1000
                self.logger.log(server=server, transport=self.registry.transport(server),
                                 direction="local", type_="tool_call", id_=block.id,
                                 method=real_name, latency_ms=latency_ms)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                    "is_error": is_error,
                })
            self.messages.append({"role": "user", "content": tool_results})
