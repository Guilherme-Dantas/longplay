from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from apps.workout_album.match import pick_spotify_match
from apps.workout_album.musicbrainz import MusicBrainzClient, MusicBrainzError
from apps.workout_album.spotify import SpotifyClient, SpotifyError

# One search should stay a short list. More albums mean more Spotify calls and tokens.
MAX_CANDIDATES = 4


class CatalogSearch:
    """Find albums in MusicBrainz, then resolve the Spotify page by name."""

    def __init__(
        self,
        spotify: SpotifyClient | None = None,
        musicbrainz: MusicBrainzClient | None = None,
    ) -> None:
        self.spotify = spotify or SpotifyClient()
        self.musicbrainz = musicbrainz or MusicBrainzClient()

    def search_albums(self, query: str, limit: int = MAX_CANDIDATES) -> dict[str, Any]:
        limit = max(1, min(int(limit), MAX_CANDIDATES))
        try:
            hits = self.musicbrainz.search_release_groups(query, limit=limit)
        except MusicBrainzError:
            hits = []

        albums: list[dict[str, Any]] = []
        seen: set[str] = set()
        for resolved in self._resolve_hits(hits):
            album_id = resolved.get("album_id") if resolved else None
            if not resolved or not album_id or album_id in seen:
                continue
            seen.add(album_id)
            albums.append(resolved)
            if len(albums) >= limit:
                break

        if albums:
            source = "musicbrainz+spotify"
        else:
            source = "spotify"
            albums = list(self.spotify.search_albums(query, limit=limit).get("albums") or [])

        return {
            "query": query,
            "source": source,
            "albums": self._measure_all(albums[:limit]),
        }

    def _resolve_hits(self, hits: list[dict[str, Any]]) -> list[dict[str, Any] | None]:
        if not hits:
            return []
        workers = min(MAX_CANDIDATES, len(hits))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(self._resolve, hits))

    def _resolve(self, hit: dict[str, Any]) -> dict[str, Any] | None:
        title = str(hit.get("title") or "")
        artist = str(hit.get("artist") or "")
        lookup = f'album:"{title}" artist:"{artist}"'
        candidates = self.spotify.search_albums(lookup, limit=3).get("albums") or []
        match = pick_spotify_match(title, artist, candidates)
        if match is None and candidates:
            # Spotify field filters are picky; try a looser name search once.
            loose = self.spotify.search_albums(f"{title} {artist}", limit=3).get("albums") or []
            match = pick_spotify_match(title, artist, loose)
        if match is None:
            return None
        return match

    def _measure_all(self, albums: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not albums:
            return []
        workers = min(MAX_CANDIDATES, len(albums))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(self._measure, albums))

    def _measure(self, album: dict[str, Any]) -> dict[str, Any]:
        card = _short_card(album)
        measure = getattr(self.spotify, "get_album_duration", None)
        album_id = card.get("album_id")
        if measure is None or not album_id:
            return card
        try:
            measured = measure(album_id)
        except SpotifyError:
            return card
        if measured.get("duration_ms") is None:
            return card
        card["duration_ms"] = int(measured["duration_ms"])
        card["duration_minutes"] = measured.get("duration_minutes")
        if "year" not in card:
            year = _year(measured.get("release_date"))
            if year is not None:
                card["year"] = year
        if not card.get("spotify_url") and measured.get("spotify_url"):
            card["spotify_url"] = measured["spotify_url"]
        return card


def _year(release_date: Any) -> int | None:
    text = str(release_date or "")
    if len(text) < 4 or not text[:4].isdigit():
        return None
    return int(text[:4])


def _short_card(album: dict[str, Any]) -> dict[str, Any]:
    """Fields the model needs to pick. Drop discovery metadata and track lists."""
    card: dict[str, Any] = {
        "album_id": album.get("album_id"),
        "name": album.get("name"),
        "artists": album.get("artists") or [],
    }
    year = _year(album.get("release_date"))
    if year is not None:
        card["year"] = year
    if album.get("spotify_url"):
        card["spotify_url"] = album["spotify_url"]
    if album.get("duration_ms") is not None:
        card["duration_ms"] = int(album["duration_ms"])
        card["duration_minutes"] = album.get("duration_minutes")
    return card
