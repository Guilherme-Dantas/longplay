import json

from harness.tools import ToolRegistry


def test_register_and_execute() -> None:
    tools = ToolRegistry()

    @tools.tool(description="Echo a word.")
    def echo(text: str) -> dict[str, str]:
        return {"text": text}

    specs = tools.openai_tools()
    assert specs is not None
    assert specs[0]["function"]["name"] == "echo"
    params = specs[0]["function"]["parameters"]
    assert "text" in params["properties"]
    payload = json.loads(tools.execute("echo", {"text": "oi"}))
    assert payload == {"text": "oi"}


def test_unknown_tool() -> None:
    tools = ToolRegistry()
    payload = json.loads(tools.execute("nope", {}))
    assert "error" in payload


def test_handler_error_is_json() -> None:
    tools = ToolRegistry()

    @tools.tool(description="Always fails.")
    def boom() -> dict:
        raise RuntimeError("broken")

    payload = json.loads(tools.execute("boom", {}))
    assert payload["error"] == "broken"
