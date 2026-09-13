from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class Policy:
    """System prompt plus run limits. Apps customize this; the loop stays generic."""

    name: str
    system_prompt: str
    max_steps: int = 8
    timeout_seconds: float = 90.0
    output_schema: type[BaseModel] | None = None
    repair_attempts: int = 1
