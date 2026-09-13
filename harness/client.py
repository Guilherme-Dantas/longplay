from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from openai import APIConnectionError, APITimeoutError, OpenAI


@dataclass(frozen=True)
class ModelConfig:
    """One OpenAI-compatible endpoint. Swap URL + key + model name, nothing else."""

    base_url: str
    api_key: str
    model: str
    timeout: float = 60.0
    extra_headers: dict[str, str] | None = None

    @classmethod
    def from_env(cls, prefix: str = "MODEL") -> ModelConfig:
        base_url = os.environ.get(f"{prefix}_BASE_URL", "").strip()
        api_key = os.environ.get(f"{prefix}_API_KEY", "").strip() or "not-needed"
        model = (
            os.environ.get(f"{prefix}_NAME", "").strip()
            or os.environ.get(f"{prefix}_MODEL", "").strip()
        )
        if not base_url or not model:
            raise RuntimeError(
                f"Missing {prefix}_BASE_URL and {prefix}_NAME (or {prefix}_MODEL). "
                "Copy .env.example to .env."
            )
        timeout = float(
            os.environ.get(f"{prefix}_TIMEOUT", os.environ.get("MODEL_TIMEOUT", "60"))
        )
        headers: dict[str, str] = {}
        if "openrouter.ai" in base_url:
            headers["HTTP-Referer"] = os.environ.get(
                "OPENROUTER_HTTP_REFERER", "https://github.com/longplay"
            )
            headers["X-Title"] = os.environ.get("OPENROUTER_TITLE", "longplay")
        return cls(
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            model=model,
            timeout=timeout,
            extra_headers=headers or None,
        )


class ModelClient:
    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        self._client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=config.timeout,
            default_headers=config.extra_headers,
        )

    @property
    def model(self) -> str:
        return self.config.model

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
        return self._client.chat.completions.create(**kwargs)

    @staticmethod
    def is_unreachable(exc: BaseException) -> bool:
        return isinstance(
            exc, (APIConnectionError, APITimeoutError, TimeoutError, ConnectionError, OSError)
        )
