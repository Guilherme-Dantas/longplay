# longplay

An album sized to the session. This repo is a small OpenAI-compatible **harness** plus a Session Soundtrack picker (Spotify catalog, workout duration).

The harness is product code and belongs on GitHub. Ollama, API keys, and model weights are local runtime, not the repository.

## Pieces

- `harness/` — `ModelClient`, `ToolRegistry`, `Policy`, `AgentLoop` (Agent Runtime context)
- `examples/hello.py` — fake `get_time` tool to prove the loop
- `apps/workout_album/` — Session Soundtrack: Spotify tools, policy, CLI / `POST /runs`
- `docs/` — product and domain language (English, DDD where it earns its keep)

The phone never calls the model. It calls the backend (`POST /runs`). Album runtime is the sum of track `duration_ms`, never an LLM guess.

## Setup

```powershell
cd F:\homelab\longplay
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
```

Edit `.env`:

| Variable | Local (Ollama) | Cloud (OpenRouter) |
| --- | --- | --- |
| `MODEL_BASE_URL` | `http://localhost:11434/v1` | `https://openrouter.ai/api/v1` |
| `MODEL_API_KEY` | `ollama` | your key |
| `MODEL_NAME` | `qwen3:8b` | model slug (`openrouter/free`, `deepseek/deepseek-chat`, …) |

If local inference is down, the loop tries `FALLBACK_*`. No vendor `if` in code — both sides speak `chat.completions`.

Spotify (client credentials, no user OAuth):

1. App at [developer.spotify.com](https://developer.spotify.com/dashboard)
2. `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in `.env`

## Hello harness

```powershell
python examples/hello.py
```

## Album picker

```powershell
python -m apps.workout_album pick --duration 45 --criteria "electronic instrumental"
python -m apps.workout_album serve
```

`POST /runs`:

```json
{
  "duration_minutes": 45,
  "criteria": "electronic, no vocals",
  "tolerance_minutes": 5
}
```

## Ollama (optional)

On an RTX 3060, 8B is the daily driver:

```powershell
winget install Ollama.Ollama
ollama pull qwen3:8b
```

Clones without a GPU point `MODEL_*` at OpenRouter and run the same code.

## Domain docs

See [docs/README.md](docs/README.md).
