from __future__ import annotations

from typing import Any

from apps.workout_album.match import pick_spotify_match
from apps.workout_album.musicbrainz import MusicBrainzClient, MusicBrainzError
from apps.workout_album.spotify import SpotifyClient


class CatalogSearch:
    """Find albums in MusicBrainz, then resolve the Spotify page by name."""

    def __init__(
        self,
        spotify: SpotifyClient | None = None,
        musicbrainz: MusicBrainzClient | None = None,
    ) -> None:
        self.spotify = spotify or SpotifyClient()
        self.musicbrainz = musicbrainz or MusicBrainzClient()

    def search_albums(self, query: str, limit: int = 8) -> dict[str, Any]:
        limit = max(1, min(int(limit), 10))
        try:
            hits = self.musicbrainz.search_release_groups(query, limit=limit)
        except MusicBrainzError:
            hits = []

        albums: list[dict[str, Any]] = []
        seen: set[str] = set()
        for hit in hits:
            resolved = self._resolve(hit)
            album_id = resolved.get("album_id") if resolved else None
            if not resolved or not album_id or album_id in seen:
                continue
            seen.add(album_id)
            albums.append(resolved)
            if len(albums) >= limit:
                break

        if albums:
            return {
                "query": query,
                "source": "musicbrainz+spotify",
                "albums": albums,
            }
        fallback = self.spotify.search_albums(query, limit=limit)
        fallback["source"] = "spotify"
        return fallback

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
        return {
            **match,
            "discovery_title": title,
            "discovery_artist": artist,
        }
