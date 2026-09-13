# longplay

Monorepo: OpenAI-compatible harness on GitHub + a Session Soundtrack picker (album runtime matches session duration; workout is the first activity type).

Write and comment in **English**. Domain words: [docs/domain/ubiquitous-language.md](docs/domain/ubiquitous-language.md). Contexts: [docs/domain/bounded-contexts.md](docs/domain/bounded-contexts.md).

## Layout

- `harness/` — Agent Runtime: `ModelClient`, `ToolRegistry`, `Policy`, `AgentLoop`. Generic. Apps register tools and a policy.
- `examples/hello.py` — smoke test with a fake `get_time` tool.
- `apps/workout_album/` — Session Soundtrack consumer: catalog tools, policy, CLI, `POST /runs`.
- `docs/` — product and domain.
- `.env.example` — config contract. Never commit `.env`.

## Rules

- Do not add LangChain, LangGraph, CrewAI, or LiteLLM. The harness is ours.
- Models only through an OpenAI-compatible API (`MODEL_BASE_URL`, `MODEL_API_KEY`, `MODEL_NAME`). Fallback: `FALLBACK_*`. No vendor SDKs.
- Album runtime is the sum of track `duration_ms`. The model must not invent minutes or album ids.
- Fit (clock) before taste. See Session Soundtrack invariants.
- The phone talks to the backend, never to the model endpoint.
- Spotify is client credentials (playback + duration) until someone asks for user OAuth. Setup, token, and dashboard traps: [docs/integrations/spotify.md](docs/integrations/spotify.md). Discovery is MusicBrainz, then resolve by name: [docs/integrations/catalog.md](docs/integrations/catalog.md). Phone ideas (activity categories, listening history) stay in [docs/product-later.md](docs/product-later.md) until explicitly requested.
- Python 3.11+, Pydantic v2, pytest in `tests/`. New harness behavior gets a test that does not hit the network.

## Commands

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
python examples/hello.py
python -m apps.workout_album pick --duration 45 --criteria "electronic instrumental"
python -m apps.workout_album serve
```
