"""Strands agent for one album pick. Catalog tools stay in this app."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.models.routing import ModelRouter

from apps.workout_album.policy import SYSTEM_PROMPT, AlbumPick
from apps.workout_album.tools import build_spotify_tools


class AgentRunError(RuntimeError):
    pass


def openai_model_from_env(prefix: str) -> OpenAIModel:
    """One OpenAI-compatible endpoint. Ollama and OpenRouter differ only by URL."""
    base_url = os.environ.get(f"{prefix}_BASE_URL", "").strip().rstrip("/")
    model_id = (
        os.environ.get(f"{prefix}_NAME", "").strip()
        or os.environ.get(f"{prefix}_MODEL", "").strip()
    )
    if not base_url or not model_id:
        raise AgentRunError(
            f"Missing {prefix}_BASE_URL and {prefix}_NAME (or {prefix}_MODEL). "
            "Copy .env.example to .env."
        )
    api_key = os.environ.get(f"{prefix}_API_KEY", "").strip() or "not-needed"
    timeout = float(os.environ.get(f"{prefix}_TIMEOUT", os.environ.get("MODEL_TIMEOUT", "90")))
    client_args: dict[str, Any] = {
        "api_key": api_key,
        "base_url": base_url,
        "timeout": timeout,
    }
    if "openrouter.ai" in base_url:
        client_args["default_headers"] = {
            "HTTP-Referer": os.environ.get(
                "OPENROUTER_HTTP_REFERER", "https://github.com/longplay"
            ),
            "X-Title": os.environ.get("OPENROUTER_TITLE", "longplay"),
        }
    return OpenAIModel(client_args=client_args, model_id=model_id)


def build_model() -> OpenAIModel | ModelRouter:
    load_dotenv()
    primary = openai_model_from_env("MODEL")
    fallback_url = os.environ.get("FALLBACK_BASE_URL", "").strip()
    fallback_name = (
        os.environ.get("FALLBACK_NAME", "").strip() or os.environ.get("FALLBACK_MODEL", "").strip()
    )
    if not fallback_url or not fallback_name:
        return primary
    return ModelRouter([primary, openai_model_from_env("FALLBACK")])


def build_agent(
    *,
    stream: bool = False,
    output_schema: type[BaseModel] | None = None,
    system_prompt: str | None = None,
    tools: list[Any] | None = None,
) -> Agent:
    kwargs: dict[str, Any] = {}
    if not stream:
        kwargs["callback_handler"] = None
    return Agent(
        model=build_model(),
        tools=tools if tools is not None else build_spotify_tools(),
        system_prompt=SYSTEM_PROMPT if system_prompt is None else system_prompt,
        structured_output_model=AlbumPick if output_schema is None else output_schema,
        **kwargs,
    )


def run_album_pick(user_message: str, *, stream: bool = False) -> AlbumPick:
    agent = build_agent(stream=stream)
    result = agent(user_message)
    if stream:
        print_trace(agent.messages)
    output = result.structured_output
    if not isinstance(output, AlbumPick):
        raise AgentRunError("model did not return AlbumPick")
    return output


def trace_lines(messages: list[dict[str, Any]]) -> list[str]:
    """Same shape as the strands-lab trace: role, tool name, result."""
    lines: list[str] = []
    for message in messages:
        role = message.get("role", "?")
        content = message.get("content") or []
        if isinstance(content, str):
            text = content.strip()
            if text:
                lines.append(f"{role} text {text}")
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if "toolUse" in block:
                use = block["toolUse"]
                lines.append(f"{role} tool {use.get('name')} {use.get('input')}")
            elif "toolResult" in block:
                result = block["toolResult"]
                lines.append(f"{role} tool result {result.get('status')} {result.get('content')}")
            elif "text" in block and role == "assistant" and str(block["text"]).strip():
                lines.append(f"{role} text {str(block['text']).strip()}")
    return lines


def print_trace(messages: list[dict[str, Any]]) -> None:
    print("\n--- loop trace ---")
    for line in trace_lines(messages):
        print(line)
