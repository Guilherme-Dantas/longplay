from __future__ import annotations

import json
import re
from typing import Any

_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def parse_json_object(text: str) -> dict[str, Any]:
    """Pull a JSON object out of model text (raw or fenced)."""
    raw = (text or "").strip()
    if not raw:
        raise ValueError("empty model response")
    match = _FENCE.search(raw)
    if match:
        raw = match.group(1)
    else:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            raw = raw[start : end + 1]
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("model response JSON is not an object")
    return data
