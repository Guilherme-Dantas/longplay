# Session Soundtrack

Core domain: match a timed session to catalog album(s).

Today the CLI treats the session as a workout. Later the same clock rules apply to other activities. Do not implement that tree here; see [product later](../product-later.md).

## Aggregate (logical)

We do not persist a cluster of entities yet. The in-memory unit of consistency for one pick is:

**Session** (root of the request)

- duration
- tolerance
- listening taste (value)

**Candidates** drawn from the catalog, each with an identity (album id) and a measured **album runtime**.

**Recommendation** — at most one candidate that satisfies the invariants below.

Until we store history, this aggregate lives for a single run and then disappears. Do not introduce repositories or domain events until a recommendation is saved or shared.

## Invariants

1. **Measured runtime.** A candidate is eligible only after album runtime is the sum of its track durations.
2. **Fit before taste.** Runtime must fall within `duration ± tolerance`. Taste never overrides a miss on the clock.
3. **One album.** A completed pick names exactly one catalog album, or it fails. No ranked list in the product contract.
4. **Honest identity.** Album id, name, and URL come from the catalog tools. The model may not mint them.
5. **Taste is ranking, not a filter with fake precision.** Criteria are hints (genre, vocals, energy). Missing metadata is not a hard reject unless the user made it one.

Invariant 1 and 2 are domain rules. They should eventually be checked in code after the model returns, not only in the prompt. Today duration helpers live in `apps/workout_album/duration.py`; the HTTP/CLI path still trusts the policy. Close that gap when touching the picker, not in the harness.

## Value objects (names)

- **Duration** — milliseconds internally.
- **Tolerance** — same unit, non-negative, small relative to the session.
- **ListeningTaste** — unstructured text on purpose. Do not prematurely enumerate genres.
- **AlbumRuntime** — derived; not an input.

## Application flow

1. Capture session duration, tolerance, and taste.
2. Search the catalog from the taste (MusicBrainz tags/titles, then the same record on Spotify by name; retries if nothing fits).
3. Measure runtime per candidate.
4. Discard non-fits.
5. Choose one remaining album by taste.
6. Return a recommendation.

Steps 2–5 may be performed by an agent with tools. The rules above do not change if we later replace the agent with a query.

## Out of scope (for this context)

Playback, likes, queueing, user library, listening history, activity category trees, overlapping sessions, multi-album programs (e.g. warm-up + main set). Those live in [product later](../product-later.md) — new aggregates or phone UX, not fields on today’s `AlbumPick`.
