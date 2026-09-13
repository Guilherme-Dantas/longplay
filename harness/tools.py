from __future__ import annotations

import inspect
import json
from collections.abc import Callable
from typing import Any, get_type_hints

from pydantic import create_model


class ToolError(RuntimeError):
    pass


class ToolRegistry:
    """Named functions the model can call. Handlers stay in your code."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., Any]] = {}
        self._specs: list[dict[str, Any]] = []

    def register(
        self,
        name: str,
        description: str,
        handler: Callable[..., Any],
        parameters: dict[str, Any] | None = None,
    ) -> None:
        schema = parameters or _schema_from_callable(handler)
        self._handlers[name] = handler
        self._specs.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": schema,
                },
            }
        )

    def tool(
        self, description: str, *, name: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.register(name or fn.__name__, description, fn)
            return fn

        return decorator

    def openai_tools(self) -> list[dict[str, Any]] | None:
        return self._specs or None

    def execute(self, name: str, arguments: dict[str, Any] | str | None) -> str:
        if name not in self._handlers:
            return json.dumps({"error": f"unknown tool: {name}"})
        if isinstance(arguments, str):
            arguments = json.loads(arguments) if arguments.strip() else {}
        arguments = arguments or {}
        try:
            result = self._handlers[name](**arguments)
        except Exception as exc:  # noqa: BLE001 — surface tool failures to the model
            return json.dumps({"error": str(exc), "tool": name})
        if isinstance(result, str):
            return result
        return json.dumps(result, default=str)


def _schema_from_callable(fn: Callable[..., Any]) -> dict[str, Any]:
    hints = get_type_hints(fn)
    fields: dict[str, Any] = {}
    signature = inspect.signature(fn)
    for param_name, param in signature.parameters.items():
        if param_name in {"self", "cls"}:
            continue
        annotation = hints.get(param_name, str)
        default = ... if param.default is inspect.Parameter.empty else param.default
        fields[param_name] = (annotation, default)
    if not fields:
        return {"type": "object", "properties": {}, "additionalProperties": False}
    model = create_model(f"{fn.__name__}Args", **fields)
    schema = model.model_json_schema()
    schema.pop("title", None)
    schema.pop("$defs", None)
    schema.setdefault("type", "object")
    schema.setdefault("additionalProperties", False)
    return schema
