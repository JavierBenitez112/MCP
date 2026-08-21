"""Minimal self-check for the tool_use/tool_result loop — no real API calls."""
from types import SimpleNamespace

from host.conversation import Conversation
from host.demo_tool import DemoAdapter
from host.logger import JsonlLogger
from host.tool_registry import ToolRegistry


class FakeMessages:
    def __init__(self, responses):
        self._responses = iter(responses)

    def create(self, **kwargs):
        return next(self._responses)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


def text_block(t):
    return SimpleNamespace(type="text", text=t)


def tool_use_block(name, input_, id_="tu_1"):
    return SimpleNamespace(type="tool_use", name=name, input=input_, id=id_)


def response(content, stop_reason, id_="msg_1"):
    return SimpleNamespace(content=content, stop_reason=stop_reason, id=id_)


def demo():
    registry = ToolRegistry()
    registry.register("demo", DemoAdapter(), transport="local")
    logger = JsonlLogger("/dev/null")

    responses = [
        response([tool_use_block("demo__get_time", {})], "tool_use"),
        response([text_block("it is now that time")], "end_turn"),
    ]
    conv = Conversation(FakeClient(responses), "fake-model", registry, logger)
    reply = conv.send("what time is it?")

    assert reply == "it is now that time", reply
    assert len(conv.messages) == 4, conv.messages  # user, assistant(tool_use), user(tool_result), assistant(text)
    tool_result_msg = conv.messages[2]
    assert tool_result_msg["role"] == "user"
    assert tool_result_msg["content"][0]["type"] == "tool_result"
    assert tool_result_msg["content"][0]["tool_use_id"] == "tu_1"
    print("ok")


if __name__ == "__main__":
    demo()
