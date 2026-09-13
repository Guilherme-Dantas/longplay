# Ubiquitous language

Use these words in code, docs, prompts, and API payloads. Do not invent synonyms in the same context.

## Session Soundtrack (core domain)

**Session.** A planned window of time with a target duration and a tolerance. Today the only type in code is a workout. Later it is any activity (chores, code, study, exercise). It is not a Spotify playback, not a gym booking, not a calendar event.

**Duration.** Elapsed listening time, stored as milliseconds in code and shown as minutes at the edge. Never a track count, never a “feels like 45 minutes.”

**Tolerance.** How far an album runtime may drift from the session duration and still count as a fit. Hard constraint, not a preference.

**Listening taste.** Free-text intent (genre, vocals, energy, language, era). Used only to rank albums that already fit the clock.

**Album.** A catalog long-play: a named, ordered set of tracks with a stable catalog id. Not a playlist, not a single, not a mix.

**Track.** One cut on an album, with its own duration. The source of truth for runtime.

**Album runtime.** Sum of track durations. Computed. Never estimated by a model.

**Fit.** An album whose runtime is within session duration ± tolerance.

**Recommendation.** Exactly one fitting album plus a short reason that cites taste. The output of a run in this domain.

## Agent Runtime (generic)

**Harness.** Our agent loop: model call, tool execution, validation. Not a product feature. Not LangChain.

**Run.** One request through the harness until a final structured result or a limit. No memory across runs.

**Tool.** A named function the model may call. In this product, tools read the catalog and measure runtime. They do not pick.

**Policy.** System prompt plus step limits plus the output schema. Apps own policies; the harness only enforces them.

**Model endpoint.** An OpenAI-compatible URL, key, and model name. Local or cloud is configuration, not a domain type.

## Words to avoid here

| Do not say | Say instead | Why |
| --- | --- | --- |
| playlist / mix | album | The unit is a record, not a queue we built |
| song length we guessed | album runtime | Runtime is summed from tracks |
| vibe match first | fit, then taste | Clock is the invariant |
| agent / LLM pick | recommendation | The product result is a recommendation; the model is machinery |
| Spotify album | catalog album | Spotify is an adapter, not the language of the domain |
