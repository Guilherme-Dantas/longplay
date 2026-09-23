"""Wall-clock logs for one album pick: model turns, tools, and catalog HTTP."""

from __future__ import annotations

import logging
import time
from typing import Any

from strands.hooks import HookProvider, HookRegistry
from strands.hooks.events import (
    AfterInvocationEvent,
    AfterModelCallEvent,
    AfterToolCallEvent,
    BeforeInvocationEvent,
    BeforeModelCallEvent,
)

LOG = logging.getLogger("longplay")


def configure_timing_logs() -> None:
    """Show timing lines on the server and CLI. Uvicorn does not configure this logger."""
    LOG.setLevel(logging.INFO)
    if not any(isinstance(handler, logging.StreamHandler) for handler in LOG.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M:%S"))
        LOG.addHandler(handler)
    LOG.propagate = False


def log_elapsed(label: str, started: float, status: str) -> None:
    elapsed_ms = (time.perf_counter() - started) * 1000
    LOG.info("%s %s %.0fms", label, status, elapsed_ms)


class LoopTiming(HookProvider):
    """One pick: how long the model waited, and how long each tool ran."""

    def __init__(self) -> None:
        self._run_started = 0.0
        self._model_started = 0.0
        self._model_ms = 0.0
        self._tool_ms = 0.0
        self._model_calls = 0

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeInvocationEvent, self.on_invocation_start)
        registry.add_callback(AfterInvocationEvent, self.on_invocation_end)
        registry.add_callback(BeforeModelCallEvent, self.on_model_start)
        registry.add_callback(AfterModelCallEvent, self.on_model_end)
        registry.add_callback(AfterToolCallEvent, self.on_tool_end)

    def on_invocation_start(self, event: BeforeInvocationEvent) -> None:
        del event
        self._run_started = time.perf_counter()
        self._model_ms = 0.0
        self._tool_ms = 0.0
        self._model_calls = 0

    def on_model_start(self, event: BeforeModelCallEvent) -> None:
        del event
        self._model_started = time.perf_counter()

    def on_model_end(self, event: AfterModelCallEvent) -> None:
        elapsed_ms = (time.perf_counter() - self._model_started) * 1000
        self._model_ms += elapsed_ms
        self._model_calls += 1
        if event.exception is not None:
            LOG.info(
                "model %d %.0fms error %s",
                self._model_calls,
                elapsed_ms,
                type(event.exception).__name__,
            )
            return
        stop = event.stop_response
        message = stop.message if stop is not None else None
        reason = stop.stop_reason if stop is not None else "unknown"
        tools = _tool_names(message)
        reasoning = " reasoning=yes" if _has_reasoning(message) else ""
        tool_part = f" tools={tools}" if tools else ""
        LOG.info(
            "model %d %.0fms stop=%s%s%s",
            self._model_calls,
            elapsed_ms,
            reason,
            tool_part,
            reasoning,
        )

    def on_tool_end(self, event: AfterToolCallEvent) -> None:
        duration_s = event.duration if event.duration is not None else 0.0
        elapsed_ms = duration_s * 1000
        self._tool_ms += elapsed_ms
        name = str(event.tool_use.get("name") or "?")
        status = "error" if event.exception is not None else str(event.result.get("status") or "unknown")
        LOG.info("tool %s %.0fms status=%s", name, elapsed_ms, status)

    def on_invocation_end(self, event: AfterInvocationEvent) -> None:
        del event
        total_ms = (time.perf_counter() - self._run_started) * 1000
        gap_ms = max(0.0, total_ms - self._model_ms - self._tool_ms)
        LOG.info(
            "run %.0fms model_calls=%d model=%.0fms tools=%.0fms gap=%.0fms",
            total_ms,
            self._model_calls,
            self._model_ms,
            self._tool_ms,
            gap_ms,
        )


def _content(message: Any) -> list[Any]:
    if message is None:
        return []
    content = message.get("content") if isinstance(message, dict) else getattr(message, "content", None)
    return content if isinstance(content, list) else []


def _tool_names(message: Any) -> str:
    names: list[str] = []
    for block in _content(message):
        if isinstance(block, dict) and "toolUse" in block:
            names.append(str(block["toolUse"].get("name") or "?"))
    return ",".join(names)


def _has_reasoning(message: Any) -> bool:
    return any(isinstance(block, dict) and "reasoningContent" in block for block in _content(message))
