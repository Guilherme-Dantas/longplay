# Catalog discovery

Session Soundtrack discovers albums **outside Spotify**, then opens the matching record **on Spotify**.

Spotify search is weak on genre (no `genre:` filter for albums; album `genres` is empty). MusicBrainz has tags and titles. Playback still happens on Spotify.

## Flow

1. `search_albums(query)` asks MusicBrainz for release groups matching the listening taste.
2. For each hit, Spotify search is `album:"Title" artist:"Artist"` (loose `Title Artist` if that misses).
3. A name score keeps only close matches (`apps/workout_album/match.py`).
4. `get_album_duration` still sums Spotify `duration_ms`. Fit is never taken from MusicBrainz.

If MusicBrainz returns nothing or errors, the tool falls back to a plain Spotify text search.

MusicBrainz is a public API: send a `User-Agent` (`longplay/0.1.0` plus the GitHub URL) and stay around **1 request per second**. A pick does one search, then N Spotify lookups.

## Why not skip Spotify

The user presses play on a Spotify id. Editions differ (deluxe vs original). Confirm runtime on the page they will open.

## Code

- `apps/workout_album/musicbrainz.py` — discovery
- `apps/workout_album/catalog.py` — resolve by name
- `apps/workout_album/spotify.py` — token, search, duration
