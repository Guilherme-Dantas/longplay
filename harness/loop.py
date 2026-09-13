from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from harness.client import ModelClient, ModelConfig
from harness.jsonutil import parse_json_object
from harness.policy import Policy
from harness.tools import ToolRegistry


class AgentError(RuntimeError):
    pass


class AgentLoop:
    """Run until the model returns a final answer or hits max_steps."""

    def __init__(
        self,
        client: ModelClient,
        tools: ToolRegistry,
        policy: Policy,
        fallback: ModelClient | None = None,
    ) -> None:
        self.client = client
        self.fallback = fallback
        self.tools = tools
        self.policy = policy

    @classmethod
    def from_env(cls, tools: ToolRegistry, policy: Policy) -> AgentLoop:
        load_dotenv()
        client = ModelClient(ModelConfig.from_env("MODEL"))
        fallback = None
        if os.environ.get("FALLBACK_BASE_URL", "").strip() and (
            os.environ.get("FALLBACK_NAME", "").strip()
            or os.environ.get("FALLBACK_MODEL", "").strip()
        ):
            fallback = ModelClient(ModelConfig.from_env("FALLBACK"))
        return cls(client=client, tools=tools, policy=policy, fallback=fallback)

    def run(self, user_message: str) -> Any:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.policy.system_prompt},
            {"role": "user", "content": user_message},
        ]
        tools = self.tools.openai_tools()
        repair_left = self.policy.repair_attempts
        used_fallback = False

        for _ in range(self.policy.max_steps):
            try:
                response = self.client.chat(messages, tools=tools)
            except Exception as exc:
                if (
                    self.fallback is not None
                    and not used_fallback
                    and ModelClient.is_unreachable(exc)
                ):
                    used_fallback = True
                    self.client = self.fallback
                    response = self.client.chat(messages, tools=tools)
                else:
                    raise AgentError(f"model call failed: {exc}") from exc

            choice = response.choices[0]
            message = choice.message
            tool_calls = list(message.tool_calls or [])

            if tool_calls:
                messages.append(_assistant_tool_message(message, tool_calls))
                for call in tool_calls:
                    payload = self.tools.execute(call.function.name, call.function.arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": payload,
                        }
                    )
                continue

            content = message.content or ""
            if self.policy.output_schema is None:
                return content
            try:
                return self._parse(content)
            except (ValidationError, ValueError, json.JSONDecodeError) as exc:
                if repair_left <= 0:
                    raise AgentError(
                        f"model did not return valid {self.policy.output_schema.__name__}: {exc}"
                    ) from exc
                repair_left -= 1
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your last message was not valid JSON for the required schema. "
                            f"Reply with a single JSON object matching {self.policy.output_schema.__name__} "
                            f"exactly. Error: {exc}"
                        ),
                    }
                )

        raise AgentError(f"max_steps ({self.policy.max_steps}) exceeded in policy {self.policy.name}")

    def _parse(self, content: str) -> BaseModel:
        schema = self.policy.output_schema
        assert schema is not None
        return schema.model_validate(parse_json_object(content))


def _assistant_tool_message(message: Any, tool_calls: list[Any]) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": message.content or None,
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments or "{}",
                },
            }
            for call in tool_calls
        ],
    }
