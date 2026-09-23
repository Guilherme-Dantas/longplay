# longplay

An album sized to the session. The agent loop is **Strands**. The Session Soundtrack picker discovers on MusicBrainz and plays on Spotify.

Ollama, API keys, and model weights are local runtime, not the repository.

## Pieces

- `apps/workout_album/runtime.py` — Strands `Agent` over an OpenAI-compatible endpoint
- `examples/hello.py` — `get_time` tool to prove the loop
- `apps/workout_album/` — Session Soundtrack: catalog tools, policy, CLI / `POST /runs`
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

If local inference is down, `ModelRouter` tries `FALLBACK_*`. Both sides are an `OpenAIModel` pointed at a base URL.

Spotify (client credentials, no user OAuth):

1. App at [developer.spotify.com](https://developer.spotify.com/dashboard)
2. `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in `.env`

## Hello agent

```powershell
python examples/hello.py
```

## Album picker

```powershell
python -m apps.workout_album pick --duration 45 --criteria "electronic instrumental"
python -m apps.workout_album serve
```

## Phone (Expo)

```powershell
python -m apps.workout_album serve
cd apps\mobile
npm run web
```

The screen calls `POST /runs` on `http://127.0.0.1:8000`. On a phone via Expo Go, set `EXPO_PUBLIC_API_URL` to this machine's LAN address. The carousel and activity selectors are still later (`docs/product-later.md`).

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
