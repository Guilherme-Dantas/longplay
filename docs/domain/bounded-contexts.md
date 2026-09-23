# Bounded contexts

Two contexts. Keep their models and language from leaking.

```text
┌─────────────────────┐     ┌──────────────────────────┐
│   Agent Runtime     │     │   Session Soundtrack     │
│                     │     │                          │
│  Strands Agent      │────▶│  Session, Taste, Album   │
│  Model endpoint     │     │  Runtime, Recommendation │
└─────────────────────┘     └────────────┬─────────────┘
   runtime.py (Strands)                  │
                                         ▼
                         ┌──────────────────────────┐
                         │ Catalog (anti-corruption)│
                         │ MusicBrainz → Spotify    │
                         └──────────────────────────┘
```

## Agent Runtime

**Purpose.** Talk to a language model, execute tools, stop with valid structured output.

**In code.** `apps/workout_album/runtime.py` builds a Strands `Agent`. The loop itself is the Strands SDK.

**Does not know.** Workouts, albums, Spotify, minutes of training. Those stay in the tool functions and `AlbumPick`.

**Published language.** `Agent` + `@tool` + `structured_output_model`. One call returns `AlbumPick`.

## Session Soundtrack

**Purpose.** Turn a session and a listening taste into one fitting album.

**In code.** `apps/workout_album/`

**Does not know.** OpenRouter, Ollama, HTTP chat completions, token counts.

**Published language.** Session duration, tolerance, taste, recommendation (`AlbumPick` at the HTTP edge).

This is the core domain. If a rule is about clocks, records, or taste, it lives here — in the system prompt, duration math, and tool contracts — not inside the Strands SDK.

## Catalog (external)

MusicBrainz and Spotify are not bounded contexts we own. They sit behind an anti-corruption layer.

- MusicBrainz is **discovery** (tags, titles, artists). It does not supply playback ids or album runtime.
- Spotify is **playback identity** (album id, URL) and **measured duration** (sum of track `duration_ms`).
- We do not import playlists, markets, playback, or user libraries.
- `get_album_duration` is domain work (sum tracks) implemented next to the Spotify adapter so the model cannot invent runtime.

Session Soundtrack names stay when a catalog source is swapped; only the adapters change. See [catalog discovery](../integrations/catalog.md).

## Integration

The soundtrack context uses the runtime context as a platform:

1. It supplies tools (search, list tracks, measure runtime).
2. It supplies a policy (fit first, then taste, JSON recommendation).
3. It maps a session + taste into the user message of a run.

Strands stays in `runtime.py`. Album, fit, and duration rules stay in the rest of this app.
