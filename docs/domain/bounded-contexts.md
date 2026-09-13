# Bounded contexts

Two contexts. Keep their models and language from leaking.

```text
┌─────────────────────┐     ┌──────────────────────────┐
│   Agent Runtime     │     │   Session Soundtrack     │
│                     │     │                          │
│  Run, Tool, Policy  │────▶│  Session, Taste, Album   │
│  Model endpoint     │     │  Runtime, Recommendation │
└─────────────────────┘     └────────────┬─────────────┘
         harness/                        │
                                         ▼
                                ┌─────────────────┐
                                │ Catalog (Spotify)│
                                │ anti-corruption  │
                                └─────────────────┘
```

## Agent Runtime

**Purpose.** Talk to a language model, execute tools, stop with valid structured output.

**In code.** `harness/`

**Does not know.** Workouts, albums, Spotify, minutes of training.

**Published language.** `Policy`, `ToolRegistry`, `AgentLoop.run(user_message) → schema`.

Treat this as a generic supporting domain. Other apps should be able to register different tools without renaming types after music.

## Session Soundtrack

**Purpose.** Turn a session and a listening taste into one fitting album.

**In code.** `apps/workout_album/`

**Does not know.** OpenRouter, Ollama, HTTP chat completions, token counts.

**Published language.** Session duration, tolerance, taste, recommendation (`AlbumPick` at the HTTP edge).

This is the core domain. If a rule is about clocks, records, or taste, it lives here — in policy, duration math, and tool contracts — not in `harness/loop.py`.

## Catalog (external)

Spotify is not a third bounded context we own. It is an upstream catalog behind an anti-corruption layer.

- We accept catalog ids, names, artists, track durations.
- We do not import playlists, markets, playback, or user libraries.
- `get_album_duration` is domain work (sum tracks) implemented next to the adapter so the model cannot invent runtime.

When a second catalog appears, the Session Soundtrack names stay; only the adapter changes.

## Integration

The soundtrack context uses the runtime context as a platform:

1. It supplies tools (search, list tracks, measure runtime).
2. It supplies a policy (fit first, then taste, JSON recommendation).
3. It maps a session + taste into the user message of a run.

The runtime context must not grow soundtrack types. The soundtrack context must not grow model-vendor types.
