"""Hello Strands agent: one local tool, same model endpoint as the album picker."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from strands import Agent, tool

from apps.workout_album.runtime import build_model


class HelloAnswer(BaseModel):
    answer: str = Field(description="Short reply for the user")
    used_tool: bool = Field(description="Whether get_time was called")


@tool
def get_time() -> dict[str, str]:
    """Return the current local date and time as ISO-8601."""
    return {"now": datetime.now().astimezone().isoformat()}


def main() -> None:
    agent = Agent(
        model=build_model(),
        tools=[get_time],
        system_prompt=(
            "You are a concise assistant. When the user asks the time, call get_time. "
            "Then answer with HelloAnswer."
        ),
        structured_output_model=HelloAnswer,
    )
    result = agent("What time is it now?")
    output = result.structured_output
    if not isinstance(output, HelloAnswer):
        raise SystemExit("model did not return HelloAnswer")
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
