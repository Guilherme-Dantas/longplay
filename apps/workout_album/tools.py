from __future__ import annotations

from typing import Any

from strands import tool

from apps.workout_album.catalog import CatalogSearch
from apps.workout_album.spotify import SpotifyClient


def build_spotify_tools(client: SpotifyClient | None = None) -> list[Any]:
    spotify = client or SpotifyClient()
    catalog = CatalogSearch(spotify=spotify)

    @tool
    def search_albums(query: str, limit: int = 4) -> dict:
        """Find up to 4 albums for a wide listening brief.

        One MusicBrainz search, then Spotify by title and artist. Each album
        includes album_id, name, artists, year, duration_minutes, and spotify_url.
        Duration is already measured. Do not pass an album title or artist as the query.
        """
        return catalog.search_albums(query=query, limit=limit)

    @tool
    def get_album_tracks(album_id: str) -> dict:
        """List tracks for a Spotify album id, including each track duration_ms."""
        return spotify.get_album_tracks(album_id=album_id)

    @tool
    def get_album_duration(album_id: str) -> dict:
        """Sum Spotify track durations for an album id.

        Use this before recommending. Never guess album length.
        """
        return spotify.get_album_duration(album_id=album_id)

    return [search_albums, get_album_tracks, get_album_duration]
