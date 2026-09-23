import pytest

from apps.workout_album.runtime import (
    AgentRunError,
    ModelRouter,
    OpenAIModel,
    build_model,
    openai_model_from_env,
    trace_lines,
)
from apps.workout_album.tools import build_spotify_tools


def test_trace_lines_show_tool_then_text() -> None:
    lines = trace_lines(
        [
            {
                "role": "assistant",
                "content": [{"toolUse": {"name": "multiply", "input": {"a": 17, "b": 23}}}],
            },
            {
                "role": "user",
                "content": [{"toolResult": {"status": "success", "content": [{"text": "391.0"}]}}],
            },
            {"role": "assistant", "content": [{"text": "17 times 23 equals 391."}]},
        ]
    )
    assert lines[0].startswith("assistant tool multiply")
    assert "391.0" in lines[1]
    assert lines[2] == "assistant text 17 times 23 equals 391."


def test_openrouter_model_sets_attribution_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FALLBACK_BASE_URL", "https://openrouter.ai/api/v1")
    monkeypatch.setenv("FALLBACK_API_KEY", "test-key")
    monkeypatch.setenv("FALLBACK_MODEL", "openrouter/free")
    model = openai_model_from_env("FALLBACK")
    assert model.config["model_id"] == "openrouter/free"
    assert model.client_args["default_headers"]["X-Title"] == "longplay"
    assert model.config["params"]["max_tokens"] == 2048
    assert model.config["params"]["extra_body"]["reasoning"] == {"effort": "minimal"}


def test_build_model_uses_router_when_fallback_is_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("apps.workout_album.runtime.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setenv("MODEL_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("MODEL_API_KEY", "ollama")
    monkeypatch.setenv("MODEL_NAME", "qwen3:8b")
    monkeypatch.setenv("FALLBACK_BASE_URL", "https://openrouter.ai/api/v1")
    monkeypatch.setenv("FALLBACK_API_KEY", "test-key")
    monkeypatch.setenv("FALLBACK_MODEL", "openrouter/free")
    model = build_model()
    assert isinstance(model, ModelRouter)


def test_build_model_is_single_endpoint_without_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("apps.workout_album.runtime.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setenv("MODEL_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("MODEL_API_KEY", "ollama")
    monkeypatch.setenv("MODEL_NAME", "qwen3:8b")
    monkeypatch.delenv("FALLBACK_BASE_URL", raising=False)
    monkeypatch.delenv("FALLBACK_NAME", raising=False)
    monkeypatch.delenv("FALLBACK_MODEL", raising=False)
    model = build_model()
    assert isinstance(model, OpenAIModel)
    assert model.config.get("params") is None


def test_missing_model_env_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("MODEL_MODEL", raising=False)
    with pytest.raises(AgentRunError):
        openai_model_from_env("MODEL")


def test_spotify_tools_keep_catalog_names() -> None:
    class FakeSpotify:
        pass

    tools = build_spotify_tools(client=FakeSpotify())  # type: ignore[arg-type]
    names = [tool.tool_spec["name"] for tool in tools]
    assert names == ["search_albums", "get_album_tracks", "get_album_duration"]
