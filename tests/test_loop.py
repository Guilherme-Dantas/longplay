from harness.loop import AgentLoop
from harness.policy import Policy
from harness.tools import ToolRegistry
from pydantic import BaseModel


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, id, name, arguments):
        self.id = id
        self.function = FakeFunction(name, arguments)


class FakeChoice:
    def __init__(self, message):
        self.message = message


class FakeResponse:
    def __init__(self, message):
        self.choices = [FakeChoice(message)]


class ScriptedClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.model = "fake"

    def chat(self, messages, tools=None, tool_choice=None):
        return self.responses.pop(0)


class Out(BaseModel):
    answer: str
    used_tool: bool


def test_loop_tool_then_json() -> None:
    tools = ToolRegistry()

    @tools.tool(description="Return a fixed time.")
    def get_time() -> dict[str, str]:
        return {"now": "2026-09-13T19:30:00"}

    client = ScriptedClient(
        [
            FakeResponse(
                FakeMessage(
                    tool_calls=[FakeToolCall("call_1", "get_time", "{}")],
                )
            ),
            FakeResponse(
                FakeMessage(content='{"answer": "19:30", "used_tool": true}'),
            ),
        ]
    )
    loop = AgentLoop(
        client=client,
        tools=tools,
        policy=Policy(name="t", system_prompt="test", output_schema=Out),
    )
    result = loop.run("que horas?")
    assert result.answer == "19:30"
    assert result.used_tool is True
