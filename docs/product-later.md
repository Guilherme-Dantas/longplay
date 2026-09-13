# Product later (phone)

Not in the current CLI / `POST /runs`. Do not implement from this file until someone asks. The clock and the album stay the product: one session window, full LPs, measured runtime.

Exercise is the **first activity type**, not the ceiling. The package name `workout_album` can stay until a second type actually ships.

## Activity categories

The phone is not an exercise app. A session is any block of time that wants a record.

Planned selectors (coarse → fine):

| Category | Example subcategories |
| --- | --- |
| Exercise | gym, run, walk, HIIT |
| Chores | dishes, cleaning, laundry |
| Code | deep work, review, ops |
| Study | reading, language, exam |

The category/subcategory pair is structured context for energy and mood (HIIT vs a quiet walk vs dishes). Natural-language taste still maps onto a **closed** list of catalog facets (MusicBrainz tags: genre, instrumental/vocal, energy). Selectors do not replace the clock.

Today there is no category tree in code. Treat every run as an exercise-shaped session.

## Phone pick (direction)

Inputs: duration as a number control; one natural-language field (what they will do + what they want to hear). Optional later: category and subcategory chips above that field.

The model maps the text onto filterable catalog categories. It does not search with the raw sentence and does not invent album ids or minutes.

Default path: submit → shortlist. Extracted chips show as **labels on the result**, not as a blocking confirm. A setting (off by default) lets someone edit chips before search.

Shortlist: **one recommendation** that follows the musical ask, plus **up to four** other fits.

- All cards fit the session duration ± tolerance. Fewer fits → fewer cards. Never pad with a miss.
- If activity energy and listening taste agree, alternatives stay in the same parent genre (other electronic styles, etc.).
- If they clash (HIIT vs quiet instrumental jazz), the rec still honors the ask; alternatives may change energy or genre (faster jazz, R&B, …).
- Card copy (year, people, why this session). Album lore only when a source exists (MusicBrainz annotation, Wikipedia later). No invented studio myths.

Confirming chips before the carousel is friction; keep it a setting.

## Listening history (Spotify user)

Goal: recommendations that know the listener, not only the session.

Examples we want later:

- Deprioritize (or skip) albums they already know well.
- If they stream a lot of rock but little of that genre’s canonical artists, surface those.
- If they rarely listen to new records, bias some alternatives toward newer releases.

Client credentials **cannot** see this. It needs the listener logged in (Authorization Code + PKCE on the phone). Do not add PKCE, scopes, or history tools until this slice is requested. When it is, pick scopes from Spotify’s list (likely `user-top-read`, `user-read-recently-played`, `user-library-read` — re-check the docs; do not copy playlist types into the domain).

Login unlocks a **signal**, not a lifetime diary:

- Top artists/tracks (`GET /v1/me/top/{type}`) — affinity over ~4 weeks, ~6 months, or ~1 year (not “everything they ever streamed”).
- Recently played (`GET /v1/me/player/recently-played`) — last **50** tracks only; a play counts after ~30 seconds. Cursors do not unlock older history.
- Saved albums/tracks (`GET /v1/me/albums`, …) — the library, not plays.

“Already heard” ≈ in library, in that recent 50, or among top-track albums. Absence is not proof they never heard the LP. Genre on Spotify albums is empty; artist `genres` on the top-artists payload is deprecated — infer genre via MusicBrainz from artist/album names. “Few new artists” ≈ `release_date` on top/saved vs now. Full streaming history only exists in Spotify’s account data export, not the Web API.

Pass the model a **short summary** (genres they play, artists they play, albums already consumed, prefer-new vs prefer-canonical). Not a raw play-history dump.

Listening history ranks and filters **fits**. It does not override the clock.

## Still out of scope until asked

Playback SDKs, saving the LP to the library, queues, overlapping sessions, multi-album programs (warm-up + main set).
