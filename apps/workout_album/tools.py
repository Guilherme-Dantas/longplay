from __future__ import annotations

from typing import Any

from strands import tool

from apps.workout_album.catalog import CatalogSearch
from apps.workout_album.spotify import SpotifyClient


def build_spotify_tools(client: SpotifyClient | None = None) -> list[Any]:
    spotify = client or SpotifyClient()
    catalog = CatalogSearch(spotify=spotify)

    @tool
    def search_albums(query: str, limit: int = 8) -> dict:
        """Find albums matching listening taste.

        Discovers candidates in MusicBrainz, then resolves each to a Spotify album
        by title and artist. Returns Spotify id, name, artists, total_tracks,
        release_date, and spotify_url. Does not include duration — call
        get_album_duration next.
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
