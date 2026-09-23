import logging
from types import SimpleNamespace

from apps.workout_album.runtime import build_agent
from apps.workout_album.timing import LoopTiming


def test_loop_timing_splits_model_and_tool(caplog) -> None:
    caplog.set_level(logging.INFO, logger="longplay")
    timing = LoopTiming()
    timing.on_invocation_start(SimpleNamespace())
    timing.on_model_start(SimpleNamespace())
    timing.on_model_end(
        SimpleNamespace(
            exception=None,
            stop_response=SimpleNamespace(
                stop_reason="tool_use",
                message={
                    "role": "assistant",
                    "content": [
                        {"reasoningContent": {"text": "thinking"}},
                        {"toolUse": {"name": "search_albums", "input": {}}},
                    ],
                },
            ),
        )
    )
    timing.on_tool_end(
        SimpleNamespace(
            tool_use={"name": "search_albums"},
            duration=1.5,
            result={"status": "success"},
            exception=None,
        )
    )
    timing.on_invocation_end(SimpleNamespace())

    text = caplog.text
    assert "model 1" in text
    assert "stop=tool_use" in text
    assert "tools=search_albums" in text
    assert "reasoning=yes" in text
    assert "tool search_albums" in text
    assert "status=success" in text
    assert "1500ms" in text
    assert "run " in text
    assert "model_calls=1" in text


def test_build_agent_registers_loop_timing(monkeypatch) -> None:
    captured: dict = {}

    class FakeAgent:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    monkeypatch.setattr("apps.workout_album.runtime.Agent", FakeAgent)
    monkeypatch.setattr("apps.workout_album.runtime.build_model", lambda: "model")
    monkeypatch.setattr("apps.workout_album.runtime.build_spotify_tools", lambda: [])
    monkeypatch.setattr("apps.workout_album.runtime.configure_timing_logs", lambda: None)

    build_agent()

    assert any(isinstance(hook, LoopTiming) for hook in captured["hooks"])
