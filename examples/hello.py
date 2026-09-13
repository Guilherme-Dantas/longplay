"""Hello harness: one fake tool, same ModelClient as production."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from harness import AgentLoop, Policy, ToolRegistry


class HelloAnswer(BaseModel):
    answer: str = Field(description="Short reply for the user")
    used_tool: bool = Field(description="Whether get_time was called")


def build_hello_loop() -> AgentLoop:
    tools = ToolRegistry()

    @tools.tool(description="Return the current local date and time as ISO-8601.")
    def get_time() -> dict[str, str]:
        return {"now": datetime.now().astimezone().isoformat()}

    policy = Policy(
        name="hello",
        system_prompt=(
            "You are a concise assistant. When the user asks the time, call get_time. "
            "Then reply with a single JSON object: "
            '{"answer": string, "used_tool": boolean}. No markdown.'
        ),
        max_steps=6,
        output_schema=HelloAnswer,
    )
    return AgentLoop.from_env(tools=tools, policy=policy)


def main() -> None:
    result = build_hello_loop().run("Que horas sao agora?")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
